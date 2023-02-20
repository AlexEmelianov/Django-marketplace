from django.db import models as m
from django.utils.translation import gettext_lazy as _


class Shop(m.Model):
    name = m.CharField(max_length=50, verbose_name=_('name of shop'))
    description = m.TextField(max_length=1000, verbose_name=_('description of shop'))

    @property
    def description_100char(self):
        if len(self.description) > 100:
            return self.description[:100] + '...'
        else:
            return self.description

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _('shop')
        verbose_name_plural = _('shops')


class Product(m.Model):
    name = m.CharField(max_length=50, verbose_name=_('name of product'))
    description = m.TextField(max_length=1000, verbose_name=_('description of product'))
    price = m.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('price'))
    remains = m.PositiveIntegerField(verbose_name=_('remaining products'))
    shop = m.ForeignKey(Shop, on_delete=m.CASCADE)

    @property
    def description_100char(self):
        if len(self.description) > 100:
            return self.description[:100] + '...'
        else:
            return self.description

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
