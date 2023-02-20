from django.contrib.auth.models import User
from app_shops.models import Product
from django.db import models as m
from django.utils.translation import gettext_lazy as _


class Profile(m.Model):
    STATUS_ONE = '1'
    STATUS_TWO = '2'
    STATUS_THREE = '3'
    STATUS_CHOICES = ((STATUS_ONE, _('Beginner')), (STATUS_TWO, _('Advanced')), (STATUS_THREE, _('Expert')))
    status = m.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_ONE)
    user = m.OneToOneField(User, on_delete=m.CASCADE)
    balance = m.DecimalField(default=0, max_digits=9, decimal_places=2, verbose_name=_('balanse'))
    city = m.CharField(max_length=40, null=True, blank=True, verbose_name=_('city'))

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')


class Cart(m.Model):
    id = m.AutoField(primary_key=True)
    user = m.ForeignKey(User, on_delete=m.CASCADE)
    product = m.ForeignKey(Product, on_delete=m.DO_NOTHING, verbose_name=_('product'))
    quantity = m.PositiveSmallIntegerField(default=1, verbose_name=_('quantity'))

    @property
    def line_total(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f'{self.product.name}, {self.quantity} * {self.product.price} = {self.line_total}'

    class Meta:
        ordering = ['user']
        verbose_name = _('purchase')
        verbose_name_plural = _('purchases')


class OrderLine(m.Model):
    id = m.AutoField(primary_key=True)
    product = m.ForeignKey(Product, on_delete=m.DO_NOTHING, verbose_name=_('product'))
    purchase_price = m.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('purchase price'))
    quantity = m.PositiveSmallIntegerField(verbose_name=_('quantity'))

    @property
    def line_total(self):
        return self.quantity * self.purchase_price

    def __str__(self):
        return f'{self.product.name}, {self.quantity} * {self.purchase_price} = {self.line_total}'

    class Meta:
        verbose_name = _('order line')
        verbose_name_plural = _('order lines')


class OrdersHistory(m.Model):
    id = m.AutoField(primary_key=True)
    user = m.ForeignKey(User, on_delete=m.CASCADE)
    purchase_date = m.DateTimeField(auto_now_add=True, verbose_name=_('purchase date'))
    total = m.DecimalField(default=0, max_digits=11, decimal_places=2, verbose_name=_('total'))
    order_lines = m.ManyToManyField(OrderLine, verbose_name=_('order line'))

    def __str__(self):
        return _('order') + f' #{self.id}'

    class Meta:
        ordering = ['-purchase_date']
        verbose_name = _('order')
        verbose_name_plural = _('orders')
