from decimal import Decimal
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Optional
from django.db.models import F, Sum
from django.db.models.signals import post_save
from app_shops.models import Shop, Product
from app_users.models import Cart, Profile, OrdersHistory, OrderLine


@dataclass
class ProfileEntity:
    id: int
    status: str
    status_choices: tuple
    balance: Decimal
    city: str
    username: str
    first_name: str
    last_name: str
    email: str
    is_authenticated: bool
    is_superuser: bool


@dataclass
class ShopEntity:
    id: int
    name: str
    description: str


@dataclass
class ProductEntity:
    id: int
    name: str
    description: str
    description_100char: str
    price: Decimal
    remains: int
    shop: ShopEntity


@dataclass
class OrderLineEntity:
    id: int
    product: ProductEntity
    purchase_price: Decimal
    quantity: int
    line_total: Decimal


@dataclass
class OrderEntity:
    id: int
    user_id: int
    purchase_date: date
    total: Decimal
    order_lines: tuple[OrderLineEntity]


@dataclass
class CartEntity:
    id: int
    user_id: int
    product: ProductEntity
    line_total: Decimal
    quantity: int


class ProfileDAO:
    """ Data Access Object для модели Profile """

    @classmethod
    def orm_to_entity(cls, profile_orm: Profile) -> ProfileEntity:
        return ProfileEntity(
            id=profile_orm.user.id,
            status=profile_orm.get_status_display(),
            status_choices=profile_orm.STATUS_CHOICES,
            balance=profile_orm.balance,
            city=profile_orm.city,
            username=profile_orm.user.username,
            first_name=profile_orm.user.first_name,
            last_name=profile_orm.user.last_name,
            email=profile_orm.user.email,
            is_authenticated=profile_orm.user.is_authenticated,
            is_superuser=profile_orm.user.is_superuser,
        )

    @classmethod
    def fetch_one(cls, user_id: int) -> ProfileEntity:
        """ Возвращает профиль пользователя """

        return cls.orm_to_entity(Profile.objects.select_related('user').get(user_id=user_id))

    @classmethod
    def update(cls, profile: ProfileEntity, update_fields: list) -> None:
        """ Обновляет значения в БД """

        profile_orm = Profile.objects.get(user_id=profile.id)
        for field in update_fields:
            if field == 'status':
                for idx in range(3):
                    if profile.status == profile.status_choices[idx][1]:
                        profile_orm.status = profile.status_choices[idx][0]
                        break
            else:
                setattr(profile_orm, field, getattr(profile, field))
        profile_orm.save(update_fields=update_fields)


class ShopDAO:
    """ Data Access Object для модели Shop """

    @classmethod
    def orm_to_entity(cls, shop_orm: Shop) -> ShopEntity:
        return ShopEntity(
            id=shop_orm.id,
            name=shop_orm.name,
            description=shop_orm.description,
        )


class ProductDAO:
    """ Data Access Object для модели Product """

    @classmethod
    def orm_to_entity(cls, product_orm: Product) -> ProductEntity:
        return ProductEntity(
            id=product_orm.pk,
            name=product_orm.name,
            description=product_orm.description,
            description_100char=product_orm.description_100char,
            price=product_orm.price,
            remains=product_orm.remains,
            shop=ShopDAO.orm_to_entity(product_orm.shop)
        )

    @classmethod
    def fetch_remains(cls) -> tuple[ProductEntity]:
        """ Возвращает перечень товаров, имеющихся на складе """

        products = Product.objects.select_related('shop').filter(remains__gte=1)
        return tuple(map(cls.orm_to_entity, products))

    @classmethod
    def minus_remains(cls, cart: tuple[CartEntity]) -> None:
        """ Уменьшает остаток товара на складе """

        products = Product.objects.only('remains').filter(id__in=(cart_line.product.id for cart_line in cart))
        for product in products:
            for cart_line in cart:
                if cart_line.product.id == product.id:
                    product.remains -= cart_line.quantity
        Product.objects.bulk_update(products, ['remains'])
        post_save.send(sender=Product)


class CartDAO:
    """ Data Access Object для модели Cart """

    @classmethod
    def _orm_to_entity(cls, cart_orm: Cart) -> CartEntity:
        return CartEntity(
            id=cart_orm.id,
            user_id=cart_orm.user_id,
            product=ProductDAO.orm_to_entity(cart_orm.product),
            line_total=cart_orm.line_total,
            quantity=cart_orm.quantity,
        )

    @classmethod
    def fetch(cls, user_id: int, threshold_quantity: int) -> tuple[CartEntity]:
        """ Возвращает перечень строк корзины """

        cart = Cart.objects.select_related('product', 'product__shop')\
                           .filter(user_id=user_id, quantity__gte=threshold_quantity)
        return tuple(map(cls._orm_to_entity, cart))

    @classmethod
    def plus(cls, user_id: int, product_id: int) -> None:
        """ Увеличивает на 1 количество товара в корзине, если его достаточно на складе """

        cart_line, created = Cart.objects.select_related('product')\
                                         .get_or_create(user_id=user_id, product_id=product_id)
        if not created and cart_line.quantity < cart_line.product.remains:
            cart_line.quantity += 1
            cart_line.save()

    @classmethod
    def minus(cls, user_id: int, product_id: int) -> None:
        """ Уменьшает на 1 количество товара в корзине """

        cart_line = Cart.objects.only('quantity').get(user_id=user_id, product_id=product_id)
        if cart_line.quantity > 0:
            cart_line.quantity -= 1
            cart_line.save()

    @classmethod
    def delete(cls, user_id: int, product_id: int = None) -> None:
        """ Удаляет товар из корзины или всю корзину пользователя """

        if product_id is None:
            Cart.objects.filter(user_id=user_id).delete()
        else:
            Cart.objects.filter(user_id=user_id, product_id=product_id).delete()


class OrderLineDAO:
    """ Data Access Object для модели OrderLine """

    @classmethod
    def orm_to_entity(cls, order_line_orm: OrderLine) -> OrderLineEntity:
        return OrderLineEntity(
            id=order_line_orm.id,
            product=ProductDAO.orm_to_entity(order_line_orm.product),
            purchase_price=order_line_orm.purchase_price,
            quantity=order_line_orm.quantity,
            line_total=order_line_orm.line_total,
        )


class OrderDAO:
    """ Data Access Object для модели Order """

    @classmethod
    def _orm_to_entity(cls, order_orm: OrdersHistory) -> OrderEntity:
        return OrderEntity(
            id=order_orm.id,
            user_id=order_orm.user_id,
            purchase_date=order_orm.purchase_date,
            total=order_orm.total,
            order_lines=tuple(map(OrderLineDAO.orm_to_entity, order_orm.order_lines.all()))
        )

    @classmethod
    def create(cls, user_id: int, total: Decimal, cart: Iterable[CartEntity]) -> None:
        """ Создает и заполняет заказ """

        order = OrdersHistory.objects.create(user_id=user_id, total=total)
        order_lines = []
        for cart_line in cart:
            order_line, created = OrderLine.objects.get_or_create(product_id=cart_line.product.id,
                                                                  purchase_price=cart_line.product.price,
                                                                  quantity=cart_line.quantity)
            order_lines.append(order_line)
        order.order_lines.add(*order_lines)
        order.save()

    @classmethod
    def get_total(cls, user_id: int) -> float:
        """ Возвращает сумму всех заказов пользователя """

        total = OrdersHistory.objects.only('total').filter(user_id=user_id).aggregate(s=Sum('total'))['s']
        return round(total, 2)

    @classmethod
    def fetch(cls, user_id: int) -> tuple[OrderEntity]:
        """ Возвращает перечень заказов пользователя """

        orders = OrdersHistory.objects.prefetch_related('order_lines', 'order_lines__product',
                                                        'order_lines__product__shop')\
                                      .filter(user_id=user_id)
        return tuple(map(cls._orm_to_entity, orders))

    @classmethod
    def fetch_on_dates(cls, start: Optional[date], end: Optional[date]) -> tuple[OrderEntity]:
        """ Возвращает перечень заказов всех пользователей в интервале дат [start, end] """

        orders = OrdersHistory.objects.prefetch_related('order_lines',
                                                        'order_lines__product',
                                                        'order_lines__product__shop').all()
        if start is not None:
            if start > end:
                start, end = end, start
            orders = orders.filter(purchase_date__range=(start, end + timedelta(days=1)))
        return tuple(map(cls._orm_to_entity, orders))
