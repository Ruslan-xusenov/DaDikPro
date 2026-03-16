from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('bonus/', views.bonus, name='bonus'),
    path('support/', views.support, name='support'),
    path('news/', views.news, name='news'),
    path('register/', views.register_customer, name='register_customer'),
    path('logout/customer/', views.customer_logout, name='customer_logout'),
]
