"""
Transaction URLs for PesaPlan
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='transaction-list'),
]
