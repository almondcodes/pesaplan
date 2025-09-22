"""
Standing Orders views for PesaPlan
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.utils import timezone
from .models import StandingOrder, StandingOrderExecution
from .serializers import (
    StandingOrderSerializer, CreateStandingOrderSerializer,
    StandingOrderExecutionSerializer, StandingOrderStatsSerializer,
    ExecuteStandingOrderSerializer, PauseResumeStandingOrderSerializer,
    CancelStandingOrderSerializer
)


class StandingOrderViewSet(generics.ListCreateAPIView):
    """
    Standing orders viewset
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateStandingOrderSerializer
        return StandingOrderSerializer
    
    def get_queryset(self):
        return StandingOrder.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create standing order"""
        with transaction.atomic():
            standing_order = serializer.save(
                user=self.request.user,
                wallet=self.request.user.wallet
            )
            
            # Calculate next execution date
            standing_order.next_execution = standing_order.calculate_next_execution()
            standing_order.save(update_fields=['next_execution'])


class StandingOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Standing order detail view
    """
    serializer_class = StandingOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return StandingOrder.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        """Cancel standing order instead of deleting"""
        instance.cancel()


class ExecuteStandingOrderView(APIView):
    """
    Manually execute standing order
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Execute standing order manually"""
        try:
            standing_order = StandingOrder.objects.get(
                id=pk,
                user=request.user
            )
        except StandingOrder.DoesNotExist:
            return Response({
                'error': 'Standing order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExecuteStandingOrderSerializer(
            data=request.data,
            context={'request': request, 'standing_order': standing_order}
        )
        serializer.is_valid(raise_exception=True)
        
        try:
            success, result = standing_order.execute()
            if success:
                return Response({
                    'message': 'Standing order executed successfully',
                    'execution_id': str(result.id)
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PauseStandingOrderView(APIView):
    """
    Pause standing order
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Pause standing order"""
        try:
            standing_order = StandingOrder.objects.get(
                id=pk,
                user=request.user
            )
        except StandingOrder.DoesNotExist:
            return Response({
                'error': 'Standing order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PauseResumeStandingOrderSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        if standing_order.status == 'active':
            standing_order.pause()
            return Response({
                'message': 'Standing order paused successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Standing order is not active'
            }, status=status.HTTP_400_BAD_REQUEST)


class ResumeStandingOrderView(APIView):
    """
    Resume standing order
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Resume standing order"""
        try:
            standing_order = StandingOrder.objects.get(
                id=pk,
                user=request.user
            )
        except StandingOrder.DoesNotExist:
            return Response({
                'error': 'Standing order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PauseResumeStandingOrderSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        if standing_order.status == 'paused':
            standing_order.resume()
            return Response({
                'message': 'Standing order resumed successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Standing order is not paused'
            }, status=status.HTTP_400_BAD_REQUEST)


class CancelStandingOrderView(APIView):
    """
    Cancel standing order
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Cancel standing order"""
        try:
            standing_order = StandingOrder.objects.get(
                id=pk,
                user=request.user
            )
        except StandingOrder.DoesNotExist:
            return Response({
                'error': 'Standing order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CancelStandingOrderSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        if standing_order.status in ['active', 'paused']:
            standing_order.cancel()
            return Response({
                'message': 'Standing order cancelled successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Standing order cannot be cancelled'
            }, status=status.HTTP_400_BAD_REQUEST)


class StandingOrderExecutionsView(generics.ListAPIView):
    """
    List standing order executions
    """
    serializer_class = StandingOrderExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        standing_order_id = self.kwargs.get('pk')
        return StandingOrderExecution.objects.filter(
            standing_order__id=standing_order_id,
            standing_order__user=self.request.user
        ).order_by('-created_at')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def standing_order_stats(request):
    """
    Get standing order statistics
    """
    user = request.user
    
    # Get basic counts
    total_orders = StandingOrder.objects.filter(user=user).count()
    active_orders = StandingOrder.objects.filter(user=user, status='active').count()
    paused_orders = StandingOrder.objects.filter(user=user, status='paused').count()
    completed_orders = StandingOrder.objects.filter(user=user, status='completed').count()
    cancelled_orders = StandingOrder.objects.filter(user=user, status='cancelled').count()
    
    # Get execution stats
    from django.db.models import Sum
    total_amount_paid = StandingOrderExecution.objects.filter(
        standing_order__user=user,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    successful_executions = StandingOrderExecution.objects.filter(
        standing_order__user=user,
        status='completed'
    ).count()
    
    failed_executions = StandingOrderExecution.objects.filter(
        standing_order__user=user,
        status='failed'
    ).count()
    
    # Get next due order
    next_due_order = StandingOrder.objects.filter(
        user=user,
        status='active',
        next_execution__lte=timezone.now()
    ).order_by('next_execution').first()
    
    stats = {
        'total_orders': total_orders,
        'active_orders': active_orders,
        'paused_orders': paused_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_amount_paid': total_amount_paid,
        'successful_executions': successful_executions,
        'failed_executions': failed_executions,
        'next_due_order': next_due_order.next_execution if next_due_order else None
    }
    
    serializer = StandingOrderStatsSerializer(stats)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def due_standing_orders(request):
    """
    Get standing orders that are due for execution
    """
    due_orders = StandingOrder.objects.filter(
        user=request.user,
        status='active',
        next_execution__lte=timezone.now()
    ).order_by('next_execution')
    
    serializer = StandingOrderSerializer(due_orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
