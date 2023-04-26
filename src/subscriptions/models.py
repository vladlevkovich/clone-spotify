from django.db import models
from config import settings


class Subscriptions(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subscription_id = models.CharField(max_length=250, blank=True, null=True)
    duration = models.IntegerField()

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscriptions, on_delete=models.CASCADE)
    sub_id = models.CharField(max_length=500, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def __str__(self):
        return str(self.user)


# class StripeCustomer(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     stripeId = models.CharField(max_length=255)
#     stripeSubscriptionId = models.CharField(max_length=255)
#
#     def __str__(self):
#         return self.user
