"""
Wallet URLs for PesaPlan
"""
from django.urls import path
from . import views

urlpatterns = [
    # Wallet management
    path('', views.WalletView.as_view(), name='wallet-detail'),
    path('balance/', views.WalletBalanceView.as_view(), name='wallet-balance'),
    path('stats/', views.wallet_stats, name='wallet-stats'),
    
    # Transactions
    path('topup/', views.WalletTopupView.as_view(), name='wallet-topup'),
    path('withdraw/', views.WalletWithdrawView.as_view(), name='wallet-withdraw'),
    path('transfer/', views.WalletTransferView.as_view(), name='wallet-transfer'),
    path('transactions/', views.WalletTransactionsView.as_view(), name='wallet-transactions'),
    
    # Limits
    path('limits/', views.WalletLimitsView.as_view(), name='wallet-limits'),
    path('limits/<int:pk>/', views.WalletLimitDetailView.as_view(), name='wallet-limit-detail'),
]
