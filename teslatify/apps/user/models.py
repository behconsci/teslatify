from djstripe.models import Customer, Subscription

from django.db import models
from django.contrib.auth.models import AbstractUser

from teslatify.apps.core.models import Base


class User(AbstractUser, Base):
    SUBSCRIPTION_STATUS_TRIAL = 'trial'
    SUBSCRIPTION_STATUS_PAID = 'paid'

    # add subscription status choices
    SUBSCRIPTION_STATUS_CHOICES = (
        (SUBSCRIPTION_STATUS_TRIAL, 'Trial'),
        (SUBSCRIPTION_STATUS_PAID, 'Paid'),
    )

    tesla_access_token = models.CharField(max_length=2055, null=True, blank=True)
    tesla_refresh_token = models.CharField(max_length=2055, null=True, blank=True)
    spotify_id = models.CharField(max_length=255, null=True, blank=True)
    spotify_access_token = models.CharField(max_length=2055, null=True, blank=True)
    spotify_refresh_token = models.CharField(max_length=2055, null=True, blank=True)
    subscription_status = models.CharField(
        max_length=255,
        choices=SUBSCRIPTION_STATUS_CHOICES,
        blank=True,
        default=''
    )

    def has_active_subscription(self):
        """ Check if user has active subscription. """

        # some friends should be able to use for free, so we don't check if user has active subscription
        friends = ['doniyor.v.j@gmail.com']
        if self.username in friends:
            return True

        # user can't change the email in stripe payment link, so this should be fine.
        customer = Customer.objects.filter(email=self.email).first()
        if not customer:
            return False

        subscription = Subscription.objects.filter(customer=customer).last()
        if not subscription:
            return False

        return subscription.status == 'active' or subscription.status == 'trialing'

    def __str__(self):
        return self.username
