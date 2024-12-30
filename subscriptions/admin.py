from django.contrib import admin

# Register your models here.
from .models import Features, Subscription, Packages

@admin.register(Features)
class FeaturesAdmin(admin.ModelAdmin):
    pass 

@admin.register(Packages)
class PackagesAdmin(admin.ModelAdmin):
    pass 

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'status', 'start_date', 'end_date' ]

