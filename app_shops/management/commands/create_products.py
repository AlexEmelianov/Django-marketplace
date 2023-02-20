from django.core.management.base import BaseCommand
from app_shops.models import Product, Shop
from random import randint, choice


class Command(BaseCommand):
    help = 'Creates 1000 Product model instances'

    def handle(self, *args, **options):
        shops = Shop.objects.all()
        prods = []
        for n in range(1000):
            prods.append(Product(name=f'product #{n}',
                                 description=f'description for product #{n}',
                                 price=randint(100, 500),
                                 remains=randint(10, 50),
                                 shop=choice(shops)))

        Product.objects.bulk_create(prods)
