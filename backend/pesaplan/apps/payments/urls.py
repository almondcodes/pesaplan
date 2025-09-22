"""
Payment URLs for PesaPlan
"""
from django.urls import path
from . import views

urlpatterns = [
    path('mpesa/callback/', views.MpesaCallbackView.as_view(), name='mpesa-callback'),
]
