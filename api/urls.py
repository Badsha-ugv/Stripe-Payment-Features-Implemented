from django.urls import path
from . import views
from . import stripe_api as stripe_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('products/', views.ProductAPIView.as_view()),
    path('coin/checkout/', stripe_views.coin_checkout, name='coin-checkout'),
    path('product/checkout/url/', stripe_views.create_checkout_session, name='product-checkout-url'),
    path('cart/', views.CartAPIView.as_view()),
    path('cart/item/<int:item_id>/', views.CartItemAPIView.as_view()),

]