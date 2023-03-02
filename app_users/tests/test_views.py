from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.urls import reverse
from app_shops.models import Shop, Product
from app_users.models import Profile, OrdersHistory
import logging

USERNAME = 'test_user'
PASSWORD = 'qscv0987'
#  NUMBER_OF_PRODUCTS must be less than arg of Paginator
#  in app_shops.views.products_list_view -> 'Paginator(products, 8)'
NUMBER_OF_PRODUCTS = 3


class MyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.authorized_client = Client()
        cls.unauthorized_client = Client()
        cls.user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        cls.permission_for_report = Permission.objects.get(codename='view_ordershistory')
        cls.user.user_permissions.add(cls.permission_for_report)
        cls.authorized_client.force_login(cls.user)
        Profile.objects.create(user=cls.user, balance=1e4)
        shop = Shop.objects.create(name='shop 1', description='test shop')
        for idx in range(1, NUMBER_OF_PRODUCTS + 1):
            Product.objects.create(
                shop=shop,
                name=f'name #{idx}',
                description=f'test №{idx}',
                price=99.90,
                remains=50
            )
        logger = logging.getLogger("django.request")
        cls.previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

    @classmethod
    def tearDownClass(cls):
        logger = logging.getLogger("django.request")
        logger.setLevel(cls.previous_level)
        super().tearDownClass()


class RegisterViewTestCase(MyTestCase):
    def test_register_url_exists_at_desired_location(self):
        response = self.unauthorized_client.get('/users/register/')
        self.assertEqual(response.status_code, 200)

    def test_register_uses_correct_template(self):
        response = self.unauthorized_client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/register.html')

    def test_register_post(self):
        username = 'reg_user'
        number = User.objects.filter(username=username).count()
        response = self.unauthorized_client.post(reverse('register'), {'username': username,
                                                                       'password1': PASSWORD,
                                                                       'password2': PASSWORD})
        self.assertEqual(number + 1, User.objects.filter(username=username).count())
        self.assertRedirects(response, '/')


class LogoutViewTestCase(MyTestCase):
    def test_logout_url_exists_at_desired_location(self):
        response = self.authorized_client.get('/users/logout/')
        self.assertRedirects(response, '/')


class LoginViewTestCase(MyTestCase):
    def test_login_url_exists_at_desired_location(self):
        response = self.unauthorized_client.get('/users/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_uses_correct_template(self):
        response = self.unauthorized_client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/login.html')

    def test_login_post(self):
        response = self.unauthorized_client.post(reverse('login'), {'username': USERNAME, 'password': PASSWORD})
        self.assertRedirects(response, '/')


class AccountViewTestCase(MyTestCase):
    def test_account_exists_at_desired_location(self):
        response = self.authorized_client.get('/users/account/')
        self.assertEqual(response.status_code, 200)

    def test_account_uses_correct_template(self):
        response = self.authorized_client.get(reverse('account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/account.html')

    def test_account_not_authenticated(self):
        response = self.unauthorized_client.get(reverse('account'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_account_orders_list(self):
        n_orders = 3
        for _ in range(n_orders):
            OrdersHistory.objects.create(user=self.user)
        response = self.authorized_client.get(reverse('account'))
        self.assertEqual(n_orders, len(response.context['orders']))

    def test_account_post(self):
        response = self.authorized_client.post(reverse('account'), {'first_name': 'test',
                                                                    'last_name': 'test',
                                                                    'email': 'test@test.com'})
        self.assertRedirects(response, '/')


class ReplenishViewTestCase(MyTestCase):
    def test_replenish_exists_at_desired_location(self):
        response = self.authorized_client.get('/users/account/replenish/')
        self.assertEqual(response.status_code, 200)

    def test_replenish_uses_correct_template(self):
        response = self.authorized_client.get(reverse('replenish'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/replenish.html')

    def test_replenish_post(self):
        response = self.authorized_client.post(reverse('replenish'), {'amount': 100})
        self.assertRedirects(response, reverse('account'))


class CartViewTestCase(MyTestCase):
    def test_cart_exists_at_desired_location(self):
        response = self.unauthorized_client.get('/users/cart/')
        self.assertEqual(response.status_code, 200)

    def test_cart_uses_correct_template(self):
        response = self.unauthorized_client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/cart.html')

    def test_cart_post(self):
        for action in ('plus', 'minus', 'delete', 'plus', 'to_pay'):
            response = self.authorized_client.post(reverse('cart'), {action: 1})
            self.assertEqual(response.status_code, 200)

