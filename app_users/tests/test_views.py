from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.urls import reverse
from app_shops.models import Shop, Product
from app_users.models import Profile

USERNAME = 'test_user'
PASSWORD = 'qscv0987'
#  number of products must be less than arg of Paginator in app_shops.views.products_view -> 'Paginator(products, 8)'
NUMBER_OF_PRODUCTS = 3


class MyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.authorized_client = Client()
        cls.unauthorized_client = Client()
        cls.user = User.objects.create_user(username=USERNAME, password=PASSWORD)
        cls.authorized_client.force_login(cls.user)

        Profile.objects.create(user=cls.user, balance=1e4)
        shop = Shop.objects.create(name='shop 1', description='test shop')
        for idx in range(1, NUMBER_OF_PRODUCTS + 1):
            Product.objects.create(
                shop=shop,
                name=f'name #{idx}',
                description=f'test №{idx}',
                price=99.90,
                remains=5
            )


class UserRegisterTest(MyTestCase):
    def test_register_url_exists_at_desired_location(self):
        response = self.unauthorized_client.get('/users/register/')
        self.assertEqual(response.status_code, 200)

    def test_register_uses_correct_template(self):
        response = self.unauthorized_client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/register.html')

    def test_register_post(self):
        response = self.unauthorized_client.post(reverse('register'), {'username': 'reg_user',
                                                                       'password1': PASSWORD,
                                                                       'password2': PASSWORD})
        self.assertEqual(response.status_code, 302)


class UserLogoutTest(MyTestCase):
    def test_logout_url_exists_at_desired_location(self):
        response = self.authorized_client.get('/users/logout/')
        self.assertEqual(response.status_code, 302)


class UserLoginTest(MyTestCase):
    def test_login_url_exists_at_desired_location(self):
        response = self.unauthorized_client.get('/users/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_uses_correct_template(self):
        response = self.unauthorized_client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/login.html')

    def test_login_post(self):
        response = self.unauthorized_client.post(reverse('login'), {'username': USERNAME, 'password': PASSWORD})
        self.assertEqual(response.status_code, 302)


class UserAccountTest(MyTestCase):
    def test_account_exists_at_desired_location(self):
        response = self.authorized_client.get('/users/account/')
        self.assertEqual(response.status_code, 200)

    def test_account_uses_correct_template(self):
        response = self.authorized_client.get(reverse('account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/account.html')

    def test_account_post(self):
        response = self.authorized_client.post(reverse('account'), {'first_name': 'test',
                                                                    'last_name': 'test',
                                                                    'email': 'test@test.com'})
        self.assertEqual(response.status_code, 302)


class UserReplenishTest(MyTestCase):
    def test_replenish_exists_at_desired_location(self):
        response = self.authorized_client.get('/users/account/replenish/')
        self.assertEqual(response.status_code, 200)

    def test_replenish_uses_correct_template(self):
        response = self.authorized_client.get(reverse('replenish'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/replenish.html')

    def test_replenish_post(self):
        response = self.authorized_client.post(reverse('account'), {'amount': 100})
        self.assertEqual(response.status_code, 302)


class UserCartTest(MyTestCase):
    def test_cart_exists_at_desired_location(self):
        response = self.authorized_client.get('/users/cart/')
        self.assertEqual(response.status_code, 200)

    def test_cart_uses_correct_template(self):
        response = self.authorized_client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_users/cart.html')

    def test_cart_post(self):
        for action in ('plus', 'minus', 'delete', 'plus', 'to_pay'):
            response = self.authorized_client.post(reverse('cart'), {action: 1})
            self.assertEqual(response.status_code, 200)
