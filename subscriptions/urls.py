from django.urls import path 
from . import views

urlpatterns =  [
    path('', views.subscriptoin, name='subscriptions'),
    path('features/create/', views.create_feature, name='create-features'),
    path('packages/create/',  views.create_packages, name='create-packages'),

    path('checkout/<int:package_id>/', views.subscriptoin_checkout, name='subscriptoin-checkout'),
    path('customer/portal/', views.customer_portal, name='customer-portal'),
    path('update-package-price/<int:package_id>/', views.update_package_price, name='update-package-price'),
    path('delte-package/<int:package_id>/', views.delete_package, name='delete-package'),
    path('cancel-subscription/<int:subscription_id>/', views.cancel_subscription, name='cancel-subscription'),

]