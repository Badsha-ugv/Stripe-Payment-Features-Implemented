from django.urls import path
from . import views
from . import stripe as stripe_view

urlpatterns = [
    path('',views.home, name='home'),
    path('product/<int:pk>/',views.product_details, name='product-detail'),
    path('cart/',views.cart, name='cart'),
    path('add-to-cart/<int:pk>/',views.add_to_cart, name='add-to-cart'),
    path('increment-cart/<int:pk>/',views.increment_cart, name='increment-cart'),
    path('decrement-cart/<int:pk>/',views.decrement_cart, name='decrement-cart'),
    path('remove-from-cart/<int:pk>/',views.remove_from_cart, name='remove-from-cart'),

    path('apply-coupon/',views.apply_coupon, name='apply-coupon'),
    path('place-order/', views.place_order, name='place-order'),
    path('order-success/', views.order_success, name='order-success'),
    path('order-cancel/', views.order_cancel, name='order-cancel'),

    path('cart-checkout/', stripe_view.create_checkout_session, name='cart-checkout'),
    path('webhook/', stripe_view.stripe_webhooks, name='webhook'),

    path('coin-checkout/', stripe_view.coin_checkout, name='coin-checkout'),
]