"""
Payment views for PesaPlan
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response


class MpesaCallbackView(generics.CreateAPIView):
    """
    M-Pesa callback endpoint
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Handle M-Pesa callback"""
        # This will be implemented in the next phase
        return Response({"message": "Callback received"}, status=status.HTTP_200_OK)
