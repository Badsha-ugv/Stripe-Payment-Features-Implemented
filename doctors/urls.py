from django.urls import path 
from . import views

urlpatterns =  [
    path('doctor-list/', views.doctor_list, name='doctor_list'),
    path('ask-doctor/<int:doctor_id>/', views.ask_doctor, name='ask-doctor'),
    
]