from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Features(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Packages(models.Model):
    features = models.ManyToManyField(Features, related_name="package_features")
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('package-detail', kwargs={'pk': self.pk})
    @property
    def total_price(self):
        return sum([f.price for f in self.package_features.all()])
    

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Packages, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.package.name}"
    
    def get_absolute_url(self):
        return reverse('subscription-detail', kwargs={'pk': self.pk})
    
    @property
    def is_expired(self):
        return timezone.now() > self.end_date
    
    @property
    def is_active_package(self):
        return self.package.is_active
    
    @property
    def remaining_days(self):
        if self.end_date:
            return (self.end_date - timezone.now()).days
        return 0
    
    @property
    def total_price(self):
        return self.package.total_price
    
    def save(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = self.start_date + timezone.timedelta(days=30)
        super().save(*args, **kwargs)

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
    


    