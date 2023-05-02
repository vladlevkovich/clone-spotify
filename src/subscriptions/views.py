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
from ..core.models import Profile
from ..users.models import CustomUser


def list_prices(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    user_subscription = UserSubscription.objects.get(user=request.user)
    sub = stripe.Subscription.retrieve(
        user_subscription.sub_id
    )
    user_subscription_price = sub['items']['data'][0]['plan']['id']
    prices = Subscriptions.objects.all()
    context = {
        'prices': prices,
        'user_subscription': user_subscription,
        'user_subscription_price': user_subscription_price
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

        if subscription_current_user['items']['data'][0]['plan']['active']:
            profile = Profile.objects.get(user=request.user)
            profile.is_subscription = True
            profile.save()

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


# @login_required()
# def subscribe_update(request, pk):
#     stripe.api_key = settings.STRIPE_SECRET_KEY
#     profile = Profile.objects.get(user=request.user)
#
#     if profile.is_subscription:
#         subscription = Subscriptions.objects.get(pk=pk)
#         user_subscription = UserSubscription.objects.get(user=request.user)
#         current_subscription = stripe.Subscription.retrieve(
#             user_subscription.sub_id
#         )
#         new_sub = stripe.Subscription.modify(
#             user_subscription.sub_id,
#             cancel_at_period_end=True,
#             proration_behavior='create_perorations',
#             items=[
#                 {
#                     'id': current_subscription['items'].data[0].id,
#                     'deleted': True
#                 },
#                 {
#                     'plan': subscription.subscription_id
#                 }
#             ]
#         )
#
#         user_subscription_id = update_subscription_user['id']  # отримуємо id нової підписки
#
#         try:
#             user_subscription = UserSubscription.objects.get(user=request.user)
#             user_subscription.subscription = new_sub
#             user_subscription.sub_id = user_subscription_id
#             user_subscription.end_date = datetime.now() + timedelta(days=new_sub.duration)
#             user_subscription.save()
#             # user_subscription = UserSubscription(user=request.user, subscription=new_sub, sub_id=user_subscription_id,
#             #                                      end_date=datetime.now() + timedelta(days=new_sub.duration))
#             # user_subscription.save()
#         except UserSubscription.DoesNotExist:
#             user_subscription = UserSubscription(user=request.user, subscription=new_sub, sub_id=user_subscription_id,
#                                                  end_date=datetime.now() + timedelta(days=new_sub.duration))
#             user_subscription.save()  # user_subscription = UserSubscription(user=request.user)
#             # user_subscription.subscription = new_sub
#             # user_subscription.end_date = datetime.now() + timedelta(days=new_sub.duration)
#             # user_subscription.save()
#
#         context = {
#             'subscription': subscription_user,
#             'sub': new_sub
#         }
#
#         return render(request, 'subscription/price.html', context)


@login_required()
def update_subscription(request, pk):
    """Upgrade your subscription to another tariff plan"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    profile = Profile.objects.get(user=request.user)
    # current_user_subscription = UserSubscription.objects.get(user=request.user)

    if profile.is_subscription:
        new_sub = Subscriptions.objects.get(pk=pk)
        subscription_user = UserSubscription.objects.get(user=request.user)
        current_user_subscription = stripe.Subscription.retrieve(
            subscription_user.sub_id
        )
        # update_subscription_user = stripe.Subscription.modify(
        #     subscription_user.sub_id,
        #     items=[
        #         {
        #             'plan': new_sub.subscription_id
        #         }
        #     ]
        # )

        update_subscription_user = stripe.Subscription.modify(
            subscription_user.sub_id,
            cancel_at_period_end=True,
            proration_behavior='create_prorations',
            items=[
                {
                    'id': current_user_subscription['items'].data[0].id,
                    'deleted': True
                },
                {
                    'plan': new_sub.subscription_id
                }
            ]
        )

        user_subscription_id = update_subscription_user['id']  # отримуємо id нової підписки

        print('new_sub_id:', user_subscription_id)
        print(update_subscription_user)

        try:
            user_subscription = UserSubscription.objects.get(user=request.user)
            user_subscription.subscription = new_sub
            user_subscription.sub_id = user_subscription_id
            user_subscription.end_date = datetime.now() + timedelta(days=new_sub.duration)
            user_subscription.save()
            # user_subscription = UserSubscription(user=request.user, subscription=new_sub, sub_id=user_subscription_id,
            #                                      end_date=datetime.now() + timedelta(days=new_sub.duration))
            # user_subscription.save()
        except UserSubscription.DoesNotExist:
            user_subscription = UserSubscription(user=request.user, subscription=new_sub, sub_id=user_subscription_id,
                                                 end_date=datetime.now() + timedelta(days=new_sub.duration))
            user_subscription.save()            # user_subscription = UserSubscription(user=request.user)
            # user_subscription.subscription = new_sub
            # user_subscription.end_date = datetime.now() + timedelta(days=new_sub.duration)
            # user_subscription.save()

        return redirect('profile')

        # context = {
        #     'subscription': subscription_user,
        #     'sub': new_sub
        # }
        #
        # return render(request, 'subscription/price.html', context)

    # subscription_user = UserSubscription.objects.get(user=request.user)
    # sub = Subscriptions.objects.get(pk=pk)
    # user_subscription = UserSubscription.objects.get(user=request.user)
    # stripe.Subscription.modify(
    #     user_subscription.sub_id,
    #     items=[
    #         {
    #             'plan': sub.subscription_id
    #         }
    #     ]
    # )


@login_required()
def canceled(request):
    """Canceled subscribe"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    user_subscription = UserSubscription.objects.get(user=request.user)
    user_profile = Profile.objects.get(user=request.user)
    # user_subscription = UserSubscription.objects.get(user=request.user).sub_id
    stripe.Subscription.delete(
        user_subscription.sub_id
    )
    # user_subscription = UserSubscription.objects.get(user=request.user)
    user_profile.is_subscription = False
    user_profile.save()
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
