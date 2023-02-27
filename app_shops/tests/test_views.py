from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from app_users.models import OrdersHistory
from app_users.tests.test_views import MyTestCase, NUMBER_OF_PRODUCTS


class ProductsViewTestCase(MyTestCase):
    def test_products_list_exists_at_desired_location(self):
        response = self.unauthorized_client.get('')
        self.assertEqual(response.status_code, 200)

    def test_products_list_uses_correct_template(self):
        response = self.unauthorized_client.get(reverse('products_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_shops/products_list.html')

    def test_products_list_number(self):
        response = self.unauthorized_client.get(reverse('products_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), NUMBER_OF_PRODUCTS)

    def test_products_list_post(self):
        response = self.unauthorized_client.post(reverse('products_list'), {'plus': 1})
        self.assertEqual(response.status_code, 200)
        response = self.unauthorized_client.post(reverse('products_list'), {'minus': 1})
        self.assertEqual(response.status_code, 200)


class ReportViewTestCase(MyTestCase):
    def test_report_exists_at_desired_location(self):
        response = self.authorized_client.get('/report/')
        self.assertEqual(response.status_code, 200)

    def test_report_list_uses_correct_template(self):
        response = self.authorized_client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_shops/report.html')

    def test_report_rows_number(self):
        OrdersHistory.objects.all().delete()
        for idx in range(1, NUMBER_OF_PRODUCTS + 1):
            self.authorized_client.post(reverse('cart'), {'plus': idx})
        self.authorized_client.post(reverse('cart'), {'to_pay': ''})

        response = self.authorized_client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['report']), NUMBER_OF_PRODUCTS)

    def test_report_post(self):
        response = self.authorized_client.post(reverse('report'), {'start': timezone.now(),
                                                                   'end': timezone.now() - timedelta(days=1)})
        self.assertEqual(response.status_code, 200)

    def test_report_not_authorized(self):
        self.user.user_permissions.remove(self.permission_for_report)
        response = self.authorized_client.get(reverse('report'))
        self.assertEqual(response.status_code, 403)
