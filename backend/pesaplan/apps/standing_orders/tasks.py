"""
Celery tasks for Standing Orders
"""
from celery import shared_task
from django.utils import timezone
from .models import StandingOrder, StandingOrderExecution
from pesaplan.apps.payments.services import PaymentProcessor
import logging

logger = logging.getLogger(__name__)


@shared_task
def execute_due_standing_orders():
    """
    Execute all standing orders that are due
    """
    due_orders = StandingOrder.objects.filter(
        status='active',
        next_execution__lte=timezone.now()
    )
    
    executed_count = 0
    failed_count = 0
    
    for standing_order in due_orders:
        try:
            success, result = standing_order.execute()
            if success:
                # Process payment
                execution = result
                process_standing_order_payment.delay(str(execution.id))
                executed_count += 1
            else:
                failed_count += 1
                logger.error(f"Failed to execute standing order {standing_order.id}: {result}")
        except Exception as e:
            failed_count += 1
            logger.error(f"Error executing standing order {standing_order.id}: {str(e)}")
    
    logger.info(f"Executed {executed_count} standing orders, {failed_count} failed")
    return {
        'executed': executed_count,
        'failed': failed_count
    }


@shared_task
def process_standing_order_payment(execution_id):
    """
    Process payment for a standing order execution
    """
    try:
        execution = StandingOrderExecution.objects.get(id=execution_id)
        standing_order = execution.standing_order
        
        # Mark as processing
        execution.mark_processing()
        
        # Process payment based on method
        payment_processor = PaymentProcessor()
        
        if standing_order.payment_method == 'wallet':
            # Process wallet payment
            success = process_wallet_payment(execution)
        elif standing_order.payment_method == 'mpesa':
            # Process M-Pesa payment
            success = process_mpesa_payment(execution)
        else:
            # Process both (wallet first, then M-Pesa)
            success = process_wallet_payment(execution)
            if not success:
                success = process_mpesa_payment(execution)
        
        if success:
            execution.mark_completed()
            logger.info(f"Payment processed successfully for execution {execution_id}")
        else:
            execution.mark_failed("Payment processing failed")
            logger.error(f"Payment processing failed for execution {execution_id}")
            
    except StandingOrderExecution.DoesNotExist:
        logger.error(f"Standing order execution {execution_id} not found")
    except Exception as e:
        logger.error(f"Error processing payment for execution {execution_id}: {str(e)}")


def process_wallet_payment(execution):
    """
    Process wallet payment for standing order execution
    """
    try:
        standing_order = execution.standing_order
        wallet = standing_order.wallet
        
        # Check if wallet has sufficient balance
        can_transact, message = wallet.can_transact(execution.amount)
        if not can_transact:
            execution.mark_failed(message)
            return False
        
        # Debit wallet
        wallet_transaction = wallet.debit(
            amount=execution.amount,
            description=f"Standing order: {standing_order.title}",
            reference=f"SO-{execution.id}"
        )
        
        execution.payment_method_used = 'wallet'
        execution.transaction_reference = wallet_transaction.reference
        execution.mark_completed()
        
        return True
        
    except Exception as e:
        execution.mark_failed(str(e))
        return False


def process_mpesa_payment(execution):
    """
    Process M-Pesa payment for standing order execution
    """
    try:
        standing_order = execution.standing_order
        payment_processor = PaymentProcessor()
        
        # Create transaction record
        from pesaplan.apps.transactions.models import Transaction
        transaction = Transaction.objects.create(
            user=standing_order.user,
            wallet=standing_order.wallet,
            standing_order=standing_order,
            transaction_type='payment',
            amount=execution.amount,
            payment_method='mpesa_stk',
            reference=f"SO-{execution.id}",
            description=f"Standing order: {standing_order.title}",
            recipient_name=standing_order.recipient_name,
            recipient_phone=standing_order.recipient_phone
        )
        
        # Process payment
        success = payment_processor.process_payment(transaction)
        
        if success:
            execution.payment_method_used = 'mpesa'
            execution.transaction_reference = transaction.reference
            execution.mark_completed()
            return True
        else:
            execution.mark_failed("M-Pesa payment failed")
            return False
            
    except Exception as e:
        execution.mark_failed(str(e))
        return False


@shared_task
def retry_failed_executions():
    """
    Retry failed standing order executions
    """
    failed_executions = StandingOrderExecution.objects.filter(
        status='failed',
        retry_count__lt=3
    )
    
    retried_count = 0
    
    for execution in failed_executions:
        if execution.can_retry():
            try:
                process_standing_order_payment.delay(str(execution.id))
                retried_count += 1
            except Exception as e:
                logger.error(f"Error retrying execution {execution.id}: {str(e)}")
    
    logger.info(f"Retried {retried_count} failed executions")
    return {'retried': retried_count}
