from datetime import date
from django.core.cache import cache
from django.core.paginator import Paginator
from django.utils.formats import date_format
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from services.make_sales_report_service import MakeSalesReportService
from services.data_access_objects import CartDAO, ProductDAO
from .forms import ReportDatesForm
from .signals import PRODUCTS_SHOPS_KEY
import logging

logger = logging.getLogger(__name__)


def products_view(request):
    """ Представление главной страницы со списком товаров """

    if request.method == 'POST':
        if 'plus' in request.POST:
            CartDAO.plus(user_id=request.user.id, product_id=int(request.POST['plus']))
        elif 'minus' in request.POST:
            CartDAO.minus(user_id=request.user.id, product_id=int(request.POST['minus']))
        else:
            logger.warning(f'Unknown action={tuple(request.POST.keys()[-1])!r} !!!')

    cart = CartDAO.fetch(user_id=request.user.id, threshold_quantity=1)
    cart_products_ids = tuple(cart_line.product.id for cart_line in cart)
    cart_sum = sum(cart_line.line_total for cart_line in cart)
    # Вечный кэш товаров и магазинов. Сбрасывается по сигналам изменения.
    products = cache.get_or_set(PRODUCTS_SHOPS_KEY, ProductDAO.fetch_remains, timeout=None)

    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'app_shops/products_list.html', {'cart': cart,
                                                            'cart_sum': cart_sum,
                                                            'cart_products_ids': cart_products_ids,
                                                            'page_obj': page_obj})


def report_view(request):
    """ Представление страницы отображения отчёта продаж """

    if request.user.username != 'admin':
        raise PermissionDenied
    start_date, end_date = None, None
    message = _('Selected all dates.')
    if request.method == 'POST':
        form = ReportDatesForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start')
            end_date = form.cleaned_data.get('end')
            # Локализация дат
            start = date_format(date.fromisoformat(f'{start_date}'), format='SHORT_DATE_FORMAT', use_l10n=True)
            end = date_format(date.fromisoformat(f'{end_date}'), format='SHORT_DATE_FORMAT', use_l10n=True)
            message = _('Selected dates: ') + '\n' + start + ' - ' + end
    else:
        form = ReportDatesForm()
    report = MakeSalesReportService.execute(start=start_date, end=end_date)
    if report is None:
        message += '\n\n' + _('No purchases')
    return render(request, 'app_shops/report.html', {'report': report,
                                                     'form': form,
                                                     'message': message})
