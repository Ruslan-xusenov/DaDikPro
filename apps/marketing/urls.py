from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_home, name='dashboard'),
    path('dashboard/customers/', views.admin_customers, name='admin_customers'),
    path('dashboard/sms/', views.admin_sms, name='admin_sms'),
    path('dashboard/news/', views.admin_news, name='admin_news'),
    path('dashboard/banners/', views.admin_banners, name='admin_banners'),
    path('dashboard/export/excel/', views.export_customers_excel, name='export_customers_excel'),
    path('dashboard/export/csv/', views.export_customers_csv, name='export_customers_csv'),
    path('dashboard/points/', views.admin_add_points, name='admin_add_points'),
    path('dashboard/customer-info/', views.get_customer_info, name='get_customer_info'),
]
