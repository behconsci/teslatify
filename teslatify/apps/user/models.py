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
        try:
            customer = Customer.objects.get(subscriber=self)
        except Customer.DoesNotExist:
            return False

        return Subscription.objects.filter(customer=customer, status="active").exists()

    def __str__(self):
        return self.username
