import json
import time

import stripe
import djstripe
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from config import settings
from datetime import datetime, timedelta
from .models import *
from ..users.models import CustomUser


def list_prices(request):
    prices = Subscriptions.objects.all()
    context = {
        'prices': prices
    }
    return render(request, 'subscription/price.html', context)


@login_required()
def subscribe(request, subscribe_id):
    """
        Create a session for subscribe
    """
    sub = get_object_or_404(Subscriptions, pk=subscribe_id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    # data = request.data
    # print('data:', data)
    # domain_url = 'http://127.0.0.1:8000/'

    try:
        prices = stripe.Price.list(
            lookup_keys=[request.POST.get('lookup_key')],
            expand=['data.product']
        )
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # 'price': settings.STRIPE_PRICE_ID,
                    'price': sub.subscription_id,
                    'quantity': 1
                },
            ],
            mode='subscription',
            payment_method_types=['card'],
            success_url=request.build_absolute_uri('/profile'),
            cancel_url=request.build_absolute_uri('/subscription/cancel'),
            customer_email=request.user.email
            # success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
            # cancel_url=domain_url + 'cancel/'
        )
        customer = stripe.Customer.create(
            email=request.user.email
        )
        user_id_customer = customer['id']

        subscription_current_user = stripe.Subscription.create(
            customer=user_id_customer,
            items=[
                {
                    'price': sub.subscription_id,
                    'quantity': 1
                }
            ],
            trial_end=int(time.time()) + (sub.duration * 86400)
        )

        user_subscription_id = subscription_current_user['id']
        print(checkout_session)
        print('customer:', customer)
        print('subscribe:', subscription_current_user)
        print('sub_id:', user_subscription_id)

        try:
            user_subscription = UserSubscription(user=request.user, subscription=sub, sub_id=user_subscription_id,
                                                 end_date=datetime.now() + timedelta(days=sub.duration))
            user_subscription.save()
        except UserSubscription.DoesNotExist:
            user_subscription = UserSubscription(user=request.user)
            user_subscription.subscription = sub
            user_subscription.end_date = datetime.now() + timedelta(days=sub.duration)
            user_subscription.save()
        return redirect(checkout_session.url, code=303)
    except Exception as error:
        raise error


@login_required()
def success(request):
    """Success payment"""

    return redirect('profile')


@login_required()
def update_subscription(request):
    pass


@login_required()
def canceled(request):
    """Canceled subscribe"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    user_subscription = UserSubscription.objects.get(user=request.user)
    # user_subscription = UserSubscription.objects.get(user=request.user).sub_id
    stripe.Subscription.delete(
        user_subscription.sub_id
    )
    # user_subscription = UserSubscription.objects.get(user=request.user)
    user_subscription.delete()
    return redirect('profile')
    # return render(request, 'subscription/cancel.html')


@csrf_exempt
def webhook(request):
    """Відслідковує стан підписки"""
    request_data = json.load(request.body)
    event = None

    if settings.STRIPE_ENDPOINT_SECRET:
        signature = request.META['HTTP_STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(
                payload=request.body,
                sig_header=signature,
                secret=settings.STRIPE_ENDPOINT_SECRET
            )
            data = event['data']
        except Exception as error:
            raise error
        except stripe.error.SignatureVerificationError as error:
            raise error

        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']

    data_object = data['object']

    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')
    elif event_type == 'customer.subscription.trial_will_end':
        print('Subscription trial will end')
    elif event_type == 'customer.subscription.created':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.updated':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.deleted':
        # handle subscription canceled automatically based
        # upon your subscription settings. Or if the user cancels it.
        print('Subscription canceled: %s', event.id)

    if event_type == 'checkout.session.completed':
        payment_intent = data['data']['object']
        print('Payment succeeded!!!', payment_intent)
    elif event_type == 'customer.subscription.created':
        print('Subscription created!')
    elif event_type == 'customer.subscription.trial_will_end':
        print('Subscription trial will end', event.id)
    elif event_type == 'customer.subscription.updated':
        subscription_id = event['data']['object']['id']
        subscription_status = event['data']['object']['status']
        user_subscription = UserSubscription.objects.filter(
            subscription__stripe_subscription=subscription_id
        ).first()
        print('Subscription created %s', event.id)
    # elif event_type == 'customer.subscription.deleted':
    #     subscription_id = event['data']['object']['id']
    #     subscription_status = event['data']['object']['status']
    #     user_subscription = UserSubscription.objects.delete()
    #     print('Subscription canceled: %s', event.id)
    elif event_type == 'invoice.paid':
        payment_intent = data
    elif event_type == 'invoice.payment_failed':
        payment_intent = data

    return JsonResponse(success=True, safe=False)


