"""
Notification views for PesaPlan
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import Notification


class NotificationListView(generics.ListAPIView):
    """
    List user notifications
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
