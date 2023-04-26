from django.urls import path
from .views import *


urlpatterns = [
    path('prices/', list_prices, name='prices'),
    # path('stripe/', stripe_conf, name='stripe'),
    path('subscribe/<int:subscribe_id>/', subscribe, name='subscribe'),
    path('success/', success, name='success'),
    path('cancel/', canceled, name='cancel'),
]
