from django import forms as f
from app_users.models import OrdersHistory


class ReportDatesForm(f.Form):
    """ Form for selecting dates interval. """

    orders = OrdersHistory.objects.order_by('purchase_date').values_list('purchase_date', flat=True)
    if orders.exists():
        years_range = list(range(orders.first().year, orders.last().year + 1))
    else:
        years_range = None
    start = f.DateField(widget=f.SelectDateWidget(years=years_range), label='')
    end = f.DateField(widget=f.SelectDateWidget(years=years_range), label='')
