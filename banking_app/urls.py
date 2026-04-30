from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('deposit/', views.deposit_view, name='deposit'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('balance/', views.check_balance_view, name='balance'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('api/verify-pin/', views.verify_pin_ajax, name='verify_pin_ajax'),
]
