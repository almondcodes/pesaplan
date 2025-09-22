"""
Health check utilities for PesaPlan
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Comprehensive health check endpoint
    """
    health_status = {
        'status': 'healthy',
        'timestamp': None,
        'services': {}
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['services']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Check Redis
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        health_status['services']['redis'] = {
            'status': 'healthy',
            'message': 'Redis connection successful'
        }
    except Exception as e:
        health_status['services']['redis'] = {
            'status': 'unhealthy',
            'message': f'Redis connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Check M-Pesa service (basic connectivity)
    try:
        from pesaplan.apps.payments.services import MpesaService
        mpesa_service = MpesaService()
        # Just check if service can be instantiated
        health_status['services']['mpesa'] = {
            'status': 'healthy',
            'message': 'M-Pesa service initialized'
        }
    except Exception as e:
        health_status['services']['mpesa'] = {
            'status': 'unhealthy',
            'message': f'M-Pesa service failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    from django.utils import timezone
    health_status['timestamp'] = timezone.now().isoformat()
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)
