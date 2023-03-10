from datetime import date
from django.contrib.auth.decorators import permission_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.utils.formats import date_format
from django.utils.translation import gettext as _
from django.shortcuts import render
from services.make_sales_report_service import MakeSalesReportService
from services.data_access_objects import CartDAO, ProductDAO
from .forms import ReportDatesForm
from .signals import PRODUCTS_KEY
import logging

logger = logging.getLogger(__name__)


def products_list_view(request: HttpRequest) -> HttpResponse:
    """ View of products list. """

    if request.user.is_authenticated:
        cart_id = f'{request.user.id}'
    elif request.session.session_key is None:
        request.session.create()
        cart_id = request.session.setdefault('cart_id', request.session.session_key)
    else:
        cart_id = request.session.setdefault('cart_id', request.session.session_key)

    if request.method == 'POST':
        if 'plus' in request.POST:
            CartDAO.plus(cart_id=cart_id, product_id=int(request.POST['plus']))
        elif 'minus' in request.POST:
            CartDAO.minus(cart_id=cart_id, product_id=int(request.POST['minus']))
        else:
            logger.warning(f'Unknown POST key is send: {tuple(request.POST.keys()[-1])!r} !')
    cart = CartDAO.fetch(cart_id=cart_id, threshold_quantity=1)
    cart_products_ids = tuple(cart_line.product.id for cart_line in cart)
    cart_sum = sum(cart_line.line_total for cart_line in cart)
    products = cache.get(PRODUCTS_KEY)  # Cache is cleared by signals
    if products is None:
        products = ProductDAO.fetch_remains()
        cache.set(PRODUCTS_KEY, products, timeout=None)

    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'app_shops/products_list.html', {'cart': cart,
                                                            'cart_sum': cart_sum,
                                                            'cart_products_ids': cart_products_ids,
                                                            'page_obj': page_obj})


@permission_required(perm='app_users.view_ordershistory', raise_exception=True)
def report_view(request: HttpRequest) -> HttpResponse:
    """ View of sales report. """

    start_date, end_date = None, None
    message = _('Selected all dates.')
    if request.method == 'POST':
        form = ReportDatesForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data.get('start')
            end_date = form.cleaned_data.get('end')
            # Dates localization
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
