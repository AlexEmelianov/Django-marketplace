from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from services.ordering_service import CartDAO, OrderingService
from services.data_access_objects import OrderDAO, ProfileDAO
from services.replenishment_service import ReplenishmentService
from .forms import AuthForm, RegisterForm, NamesEditForm, ReplenishmentForm
from .models import Profile
import logging

logger = logging.getLogger(__name__)


def login_view(request: HttpRequest) -> HttpResponse:
    """ View of login. """

    if request.method == 'POST':
        auth_form = AuthForm(request.POST)
        if auth_form.is_valid():
            username = auth_form.cleaned_data['username']
            password = auth_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is None:
                auth_form.add_error('__all__', _('Error! Check the spelling of the username and password.'))
            # elif user.is_superuser:
            #     auth_form.add_error('__all__', _('Admin, you need to login through /admin/'))
            elif not user.is_active:
                auth_form.add_error('__all__', _('Error! User is not active.'))
            else:
                login(request, user)
                CartDAO.merge(cart_id_anonym=request.session.get('cart_id', '0'), cart_id_user=f'{user.id}')
                logger.debug(f'Authentification of the user {username!r}')
                return redirect('/')
    else:
        if request.user.is_authenticated:
            return redirect('/')
        auth_form = AuthForm()
    return render(request, 'app_users/login.html', {'form': auth_form})


def register_view(request: HttpRequest) -> HttpResponse:
    """ View of registration. """

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            city = form.cleaned_data.get('city')
            Profile.objects.create(user=user, city=city)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            CartDAO.merge(cart_id_anonym=request.session.get('cart_id', '0'), cart_id_user=f'{user.id}')
            return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'app_users/register.html', {'form': form})


@login_required
def account_view(request: HttpRequest) -> HttpResponse:
    """ View of account. """

    profile = ProfileDAO.fetch_one(user_id=request.user.id)
    if request.method == 'POST':
        form = NamesEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = NamesEditForm(instance=request.user)
    orders = cache.get(f'orders_{profile.username}')  # Cache is cleared by signals
    if orders is None:
        orders = OrderDAO.fetch(user_id=profile.id)
        cache.set(f'orders_{profile.username}', orders, timeout=None)
    total = sum(order.total for order in orders)
    cart = CartDAO.fetch(cart_id=f'{profile.id}', threshold_quantity=1)
    cart_sum = sum(cart_line.line_total for cart_line in cart)
    return render(request, 'app_users/account.html', {'form': form,
                                                      'profile': profile,
                                                      'orders': orders,
                                                      'total': total,
                                                      'cart_sum': cart_sum})


@login_required
def replenish_view(request: HttpRequest) -> HttpResponse:
    """ View of balance replenishment. """

    if request.method == 'POST':
        form = ReplenishmentForm(request.POST)
        if form.is_valid():
            ReplenishmentService.execute(user_id=request.user.id, amount=form.cleaned_data['amount'])
            return redirect(reverse('account'))
    else:
        form = ReplenishmentForm()
    return render(request, 'app_users/replenish.html', {'form': form})


def cart_view(request: HttpRequest) -> HttpResponse:
    """ View of cart. """

    if request.user.is_authenticated:
        cart_id = f'{request.user.id}'
    elif request.session.session_key is None:
        request.session.create()
        cart_id = request.session.setdefault('cart_id', request.session.session_key)
    else:
        cart_id = request.session.setdefault('cart_id', request.session.session_key)
    message = None
    if request.method == 'POST':
        if 'plus' in request.POST:
            CartDAO.plus(cart_id=cart_id, product_id=int(request.POST['plus']))
        elif 'minus' in request.POST:
            CartDAO.minus(cart_id=cart_id, product_id=int(request.POST['minus']))
        elif 'delete' in request.POST:
            CartDAO.delete(cart_id=cart_id, product_id=int(request.POST['delete']))
        elif 'to_pay' in request.POST and request.user.is_authenticated:
            message = OrderingService.execute(user_id=cart_id)
        else:
            return redirect(reverse('login'))
    cart = CartDAO.fetch(cart_id=cart_id, threshold_quantity=0)
    cart_sum = sum(cart_line.line_total for cart_line in cart)
    return render(request, 'app_users/cart.html', {'cart': cart,
                                                   'cart_sum': cart_sum,
                                                   'message': message})
