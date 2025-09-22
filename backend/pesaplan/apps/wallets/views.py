"""
Wallet views for PesaPlan
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.utils import timezone
from .models import Wallet, WalletTransaction, WalletLimit
from .serializers import (
    WalletSerializer, WalletTransactionSerializer, WalletTopupSerializer,
    WalletWithdrawSerializer, WalletTransferSerializer, WalletLimitSerializer,
    WalletBalanceSerializer
)
from pesaplan.apps.payments.services import PaymentProcessor


class WalletView(generics.RetrieveAPIView):
    """
    Get user wallet details
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.wallet


class WalletBalanceView(APIView):
    """
    Get wallet balance
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current wallet balance"""
        wallet = request.user.wallet
        serializer = WalletBalanceSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WalletTopupView(APIView):
    """
    Top up wallet via M-Pesa
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Initiate wallet top-up"""
        serializer = WalletTopupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        description = serializer.validated_data['description']
        
        # Create transaction record
        wallet = request.user.wallet
        transaction_record = WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type='credit',
            description=description,
            status='pending',
            balance_before=wallet.balance,
            balance_after=wallet.balance
        )
        
        # Initiate M-Pesa STK Push
        payment_processor = PaymentProcessor()
        # This would trigger M-Pesa STK Push in a real implementation
        
        return Response({
            'message': 'Top-up initiated. Please complete payment on your phone.',
            'transaction_id': str(transaction_record.id),
            'amount': amount
        }, status=status.HTTP_200_OK)


class WalletWithdrawView(APIView):
    """
    Withdraw from wallet
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Withdraw from wallet"""
        serializer = WalletWithdrawSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        description = serializer.validated_data['description']
        
        try:
            with transaction.atomic():
                # Debit wallet
                wallet_transaction = request.user.wallet.debit(
                    amount=amount,
                    description=description,
                    reference=f"WTH-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                )
                
                return Response({
                    'message': 'Withdrawal successful',
                    'transaction_id': str(wallet_transaction.id),
                    'amount': amount,
                    'new_balance': request.user.wallet.balance
                }, status=status.HTTP_200_OK)
                
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class WalletTransferView(APIView):
    """
    Transfer to another user's wallet
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Transfer to another user"""
        serializer = WalletTransferSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        recipient_phone = serializer.validated_data['recipient_phone']
        description = serializer.validated_data['description']
        
        try:
            with transaction.atomic():
                # Get recipient
                from pesaplan.apps.users.models import User
                recipient = User.objects.get(phone_number=recipient_phone)
                
                # Debit sender's wallet
                sender_transaction = request.user.wallet.debit(
                    amount=amount,
                    description=f"Transfer to {recipient.full_name}",
                    reference=f"TFR-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                )
                
                # Credit recipient's wallet
                recipient_transaction = recipient.wallet.credit(
                    amount=amount,
                    description=f"Transfer from {request.user.full_name}",
                    reference=sender_transaction.reference
                )
                
                return Response({
                    'message': 'Transfer successful',
                    'transaction_id': str(sender_transaction.id),
                    'amount': amount,
                    'recipient': recipient.full_name,
                    'new_balance': request.user.wallet.balance
                }, status=status.HTTP_200_OK)
                
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                'error': 'Recipient not found'
            }, status=status.HTTP_400_BAD_REQUEST)


class WalletTransactionsView(generics.ListAPIView):
    """
    List wallet transactions
    """
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WalletTransaction.objects.filter(
            wallet=self.request.user.wallet
        ).order_by('-created_at')


class WalletLimitsView(generics.ListCreateAPIView):
    """
    Manage wallet limits
    """
    serializer_class = WalletLimitSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WalletLimit.objects.filter(wallet=self.request.user.wallet)
    
    def perform_create(self, serializer):
        serializer.save(wallet=self.request.user.wallet)


class WalletLimitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Manage individual wallet limit
    """
    serializer_class = WalletLimitSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WalletLimit.objects.filter(wallet=self.request.user.wallet)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def wallet_stats(request):
    """
    Get wallet statistics
    """
    wallet = request.user.wallet
    
    # Calculate monthly stats
    from django.db.models import Sum
    from datetime import datetime, timedelta
    
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_deposits = WalletTransaction.objects.filter(
        wallet=wallet,
        transaction_type='credit',
        created_at__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_withdrawals = WalletTransaction.objects.filter(
        wallet=wallet,
        transaction_type='debit',
        created_at__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    return Response({
        'current_balance': wallet.balance,
        'total_deposited': wallet.total_deposited,
        'total_withdrawn': wallet.total_withdrawn,
        'monthly_deposits': monthly_deposits,
        'monthly_withdrawals': monthly_withdrawals,
        'daily_limit': wallet.daily_limit,
        'monthly_limit': wallet.monthly_limit,
        'last_transaction': wallet.last_transaction_at
    }, status=status.HTTP_200_OK)
