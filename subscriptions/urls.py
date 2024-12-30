from django.urls import path 
from . import views

urlpatterns =  [
    path('', views.subscriptoin, name='subscriptions'),
    path('features/create/', views.create_feature, name='create-features'),
    path('packages/create/',  views.create_packages, name='create-packages'),

    path('checkout/<int:package_id>/', views.subscriptoin_checkout, name='subscriptoin-checkout'),
    

]