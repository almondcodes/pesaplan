"""
Transaction views for PesaPlan
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import Transaction


class TransactionListView(generics.ListAPIView):
    """
    List user transactions
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')
