from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Features(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    # price = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


PACKAGE_TYPES = [
        ('month', 'Monthly'),
        ('year', 'Yearly'),
        ('week', 'Week'),
        ('day', 'Day')
    ]
class Packages(models.Model):
    features = models.ManyToManyField(Features, related_name="package_features")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    package_type = models.CharField(max_length=10, choices=PACKAGE_TYPES, default='month')
    stripe_product_id = models.CharField(max_length=100, blank=True)
    stripe_price_id = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    # discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('package-detail', kwargs={'pk': self.pk})
    

class Subscription(models.Model):
    stripe_subscriptoin_id = models.CharField(max_length=200,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Packages, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='active')  # other status cancel  

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.package.name}"
    
    def get_absolute_url(self):
        return reverse('subscription-detail', kwargs={'pk': self.pk})
    

class Payment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    transaction_id = models.CharField(max_length=255)
    payment_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subscription.user.username} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse('payment-detail', kwargs={'pk': self.pk})
    
    @property
    def is_paid(self):
        return self.amount >= self.subscription.total_price
    
    @property
    def is_expired(self):
        return timezone.now() > self.subscription.end_date
    