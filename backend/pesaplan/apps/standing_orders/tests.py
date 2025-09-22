"""
Tests for Standing Orders models and functionality
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.utils import timezone
from pesaplan.apps.standing_orders.models import StandingOrder, StandingOrderExecution
from pesaplan.apps.users.models import User
from pesaplan.apps.wallets.models import Wallet


@pytest.mark.django_db
class TestStandingOrderModel:
    """Test StandingOrder model functionality"""
    
    def test_create_standing_order(self, user, wallet):
        """Test creating a standing order"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Monthly Rent',
            description='Monthly rent payment',
            amount=Decimal('50000.00'),
            frequency='monthly',
            recipient_name='Landlord',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date()
        )
        
        assert standing_order.user == user
        assert standing_order.wallet == wallet
        assert standing_order.title == 'Monthly Rent'
        assert standing_order.description == 'Monthly rent payment'
        assert standing_order.amount == Decimal('50000.00')
        assert standing_order.frequency == 'monthly'
        assert standing_order.recipient_name == 'Landlord'
        assert standing_order.recipient_phone == '+254712345678'
        assert standing_order.recipient_account == '1234567890'
        assert standing_order.status == 'active'
        assert standing_order.is_active is True
    
    def test_standing_order_str_representation(self, user, wallet):
        """Test string representation of standing order"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Monthly Rent',
            description='Monthly rent payment',
            amount=Decimal('50000.00'),
            frequency='monthly',
            recipient_name='Landlord',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date()
        )
        
        expected = f"Monthly Rent - KES 50000.00 ({user.full_name})"
        assert str(standing_order) == expected
    
    def test_standing_order_frequency_choices(self, user, wallet):
        """Test standing order frequency choices"""
        frequencies = ['daily', 'weekly', 'monthly', 'yearly']
        
        for frequency in frequencies:
            standing_order = StandingOrder.objects.create(
                user=user,
                wallet=wallet,
                title=f'Test {frequency}',
                description=f'Test {frequency} payment',
                amount=Decimal('1000.00'),
                frequency=frequency,
                recipient_name='Test Recipient',
                recipient_phone='+254712345678',
                recipient_account='1234567890',
                start_date=timezone.now().date(),
                end_date=(timezone.now() + timedelta(days=365)).date()
            )
            
            assert standing_order.frequency == frequency
    
    def test_standing_order_status_choices(self, user, wallet):
        """Test standing order status choices"""
        statuses = ['active', 'paused', 'completed', 'cancelled']
        
        for status in statuses:
            standing_order = StandingOrder.objects.create(
                user=user,
                wallet=wallet,
                title=f'Test {status}',
                description=f'Test {status} payment',
                amount=Decimal('1000.00'),
                frequency='monthly',
                recipient_name='Test Recipient',
                recipient_phone='+254712345678',
                recipient_account='1234567890',
                start_date=timezone.now().date(),
                end_date=(timezone.now() + timedelta(days=365)).date(),
                status=status
            )
            
            assert standing_order.status == status
    
    def test_standing_order_calculate_next_execution(self, user, wallet):
        """Test next execution date calculation"""
        # Test monthly frequency
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Monthly Test',
            description='Monthly test payment',
            amount=Decimal('1000.00'),
            frequency='monthly',
            recipient_name='Test Recipient',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date()
        )
        
        next_execution = standing_order.calculate_next_execution()
        assert next_execution is not None
        assert next_execution > timezone.now().date()
    
    def test_standing_order_pause_functionality(self, user, wallet):
        """Test pausing a standing order"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Test Order',
            description='Test payment',
            amount=Decimal('1000.00'),
            frequency='monthly',
            recipient_name='Test Recipient',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date(),
            status='active'
        )
        
        assert standing_order.status == 'active'
        assert standing_order.is_active is True
        
        standing_order.pause()
        
        assert standing_order.status == 'paused'
        assert standing_order.is_active is False
    
    def test_standing_order_resume_functionality(self, user, wallet):
        """Test resuming a standing order"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Test Order',
            description='Test payment',
            amount=Decimal('1000.00'),
            frequency='monthly',
            recipient_name='Test Recipient',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date(),
            status='paused'
        )
        
        assert standing_order.status == 'paused'
        assert standing_order.is_active is False
        
        standing_order.resume()
        
        assert standing_order.status == 'active'
        assert standing_order.is_active is True
    
    def test_standing_order_cancel_functionality(self, user, wallet):
        """Test cancelling a standing order"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Test Order',
            description='Test payment',
            amount=Decimal('1000.00'),
            frequency='monthly',
            recipient_name='Test Recipient',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date(),
            status='active'
        )
        
        assert standing_order.status == 'active'
        assert standing_order.is_active is True
        
        standing_order.cancel()
        
        assert standing_order.status == 'cancelled'
        assert standing_order.is_active is False
        assert standing_order.cancelled_at is not None


@pytest.mark.django_db
class TestStandingOrderExecutionModel:
    """Test StandingOrderExecution model functionality"""
    
    def test_create_standing_order_execution(self, user, wallet):
        """Test creating a standing order execution"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Test Order',
            description='Test payment',
            amount=Decimal('1000.00'),
            frequency='monthly',
            recipient_name='Test Recipient',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date()
        )
        
        execution = StandingOrderExecution.objects.create(
            standing_order=standing_order,
            amount=Decimal('1000.00'),
            status='completed',
            execution_date=timezone.now().date(),
            transaction_reference='TXN123456789'
        )
        
        assert execution.standing_order == standing_order
        assert execution.amount == Decimal('1000.00')
        assert execution.status == 'completed'
        assert execution.execution_date == timezone.now().date()
        assert execution.transaction_reference == 'TXN123456789'
    
    def test_standing_order_execution_str_representation(self, user, wallet):
        """Test string representation of standing order execution"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Test Order',
            description='Test payment',
            amount=Decimal('1000.00'),
            frequency='monthly',
            recipient_name='Test Recipient',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date()
        )
        
        execution = StandingOrderExecution.objects.create(
            standing_order=standing_order,
            amount=Decimal('1000.00'),
            status='completed',
            execution_date=timezone.now().date(),
            transaction_reference='TXN123456789'
        )
        
        expected = f"Execution of {standing_order.title} - KES 1000.00"
        assert str(execution) == expected
    
    def test_standing_order_execution_status_choices(self, user, wallet):
        """Test standing order execution status choices"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Test Order',
            description='Test payment',
            amount=Decimal('1000.00'),
            frequency='monthly',
            recipient_name='Test Recipient',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date()
        )
        
        statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        
        for status in statuses:
            execution = StandingOrderExecution.objects.create(
                standing_order=standing_order,
                amount=Decimal('1000.00'),
                status=status,
                execution_date=timezone.now().date(),
                transaction_reference=f'TXN{status}'
            )
            
            assert execution.status == status
    
    def test_standing_order_execution_metadata(self, user, wallet):
        """Test standing order execution metadata field"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Test Order',
            description='Test payment',
            amount=Decimal('1000.00'),
            frequency='monthly',
            recipient_name='Test Recipient',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date()
        )
        
        metadata = {'mpesa_receipt': 'NEF61H8J60', 'gateway_response': 'success'}
        execution = StandingOrderExecution.objects.create(
            standing_order=standing_order,
            amount=Decimal('1000.00'),
            status='completed',
            execution_date=timezone.now().date(),
            transaction_reference='TXN123456789',
            metadata=metadata
        )
        
        assert execution.metadata == metadata
        assert execution.metadata['mpesa_receipt'] == 'NEF61H8J60'
    
    def test_standing_order_execution_ordering(self, user, wallet):
        """Test standing order execution ordering"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Test Order',
            description='Test payment',
            amount=Decimal('1000.00'),
            frequency='monthly',
            recipient_name='Test Recipient',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date()
        )
        
        # Create multiple executions
        for i in range(3):
            StandingOrderExecution.objects.create(
                standing_order=standing_order,
                amount=Decimal('1000.00'),
                status='completed',
                execution_date=timezone.now().date(),
                transaction_reference=f'TXN{i}'
            )
        
        # Get executions ordered by created_at (most recent first)
        executions = StandingOrderExecution.objects.filter(standing_order=standing_order)
        
        assert executions.count() == 3
        assert executions[0].transaction_reference == 'TXN2'  # Most recent first
        assert executions[2].transaction_reference == 'TXN0'  # Oldest last


@pytest.mark.django_db
class TestStandingOrderBusinessLogic:
    """Test standing order business logic"""
    
    def test_standing_order_execution_history(self, user, wallet):
        """Test getting standing order execution history"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Test Order',
            description='Test payment',
            amount=Decimal('1000.00'),
            frequency='monthly',
            recipient_name='Test Recipient',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date()
        )
        
        # Create multiple executions
        for i in range(3):
            StandingOrderExecution.objects.create(
                standing_order=standing_order,
                amount=Decimal('1000.00'),
                status='completed',
                execution_date=timezone.now().date(),
                transaction_reference=f'TXN{i}'
            )
        
        # Get execution history
        executions = standing_order.executions.all()
        
        assert executions.count() == 3
        assert executions[0].transaction_reference == 'TXN2'  # Most recent first
        assert executions[2].transaction_reference == 'TXN0'  # Oldest last
    
    def test_standing_order_success_rate(self, user, wallet):
        """Test calculating standing order success rate"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Test Order',
            description='Test payment',
            amount=Decimal('1000.00'),
            frequency='monthly',
            recipient_name='Test Recipient',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date()
        )
        
        # Create executions with different statuses
        StandingOrderExecution.objects.create(
            standing_order=standing_order,
            amount=Decimal('1000.00'),
            status='completed',
            execution_date=timezone.now().date(),
            transaction_reference='TXN1'
        )
        
        StandingOrderExecution.objects.create(
            standing_order=standing_order,
            amount=Decimal('1000.00'),
            status='completed',
            execution_date=timezone.now().date(),
            transaction_reference='TXN2'
        )
        
        StandingOrderExecution.objects.create(
            standing_order=standing_order,
            amount=Decimal('1000.00'),
            status='failed',
            execution_date=timezone.now().date(),
            transaction_reference='TXN3'
        )
        
        # Calculate success rate (2 completed out of 3 total = 66.67%)
        total_executions = standing_order.executions.count()
        successful_executions = standing_order.executions.filter(status='completed').count()
        success_rate = (successful_executions / total_executions) * 100
        
        assert total_executions == 3
        assert successful_executions == 2
        assert success_rate == 66.67
    
    def test_standing_order_total_amount_paid(self, user, wallet):
        """Test calculating total amount paid through standing order"""
        standing_order = StandingOrder.objects.create(
            user=user,
            wallet=wallet,
            title='Test Order',
            description='Test payment',
            amount=Decimal('1000.00'),
            frequency='monthly',
            recipient_name='Test Recipient',
            recipient_phone='+254712345678',
            recipient_account='1234567890',
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=365)).date()
        )
        
        # Create successful executions
        for i in range(3):
            StandingOrderExecution.objects.create(
                standing_order=standing_order,
                amount=Decimal('1000.00'),
                status='completed',
                execution_date=timezone.now().date(),
                transaction_reference=f'TXN{i}'
            )
        
        # Calculate total amount paid
        total_paid = standing_order.executions.filter(status='completed').aggregate(
            total=models.Sum('amount')
        )['total']
        
        assert total_paid == Decimal('3000.00')
