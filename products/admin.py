from django.contrib import admin

# Register your models here.
from .models import Medicine, Category, Brand, Cart, CartItem, Coupon, ShippingCharge, ShippingAddress, PaymentMethod, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    pass

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    pass

@admin.register(ShippingCharge)
class ShippingChargeAdmin(admin.ModelAdmin):
    pass

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    pass

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass