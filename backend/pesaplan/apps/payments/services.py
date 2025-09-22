"""
M-Pesa payment services for PesaPlan
"""
import base64
import json
import requests
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__name__)


class MpesaService:
    """
    M-Pesa Daraja API service
    """
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.environment = settings.MPESA_ENVIRONMENT
        
        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
    
    def get_access_token(self):
        """
        Get M-Pesa access token with caching
        """
        cache_key = 'mpesa_access_token'
        token = cache.get(cache_key)
        
        if token:
            return token
        
        try:
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            response = requests.get(
                url, 
                auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret),
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            token = data.get('access_token')
            
            if token:
                # Cache token for 55 minutes (tokens expire in 1 hour)
                cache.set(cache_key, token, 3300)
                logger.info("M-Pesa access token obtained and cached")
                return token
            else:
                logger.error(f"Failed to get access token: {data}")
                raise Exception("Failed to get M-Pesa access token")
                
        except requests.RequestException as e:
            logger.error(f"Error getting M-Pesa access token: {str(e)}")
            raise Exception(f"Network error getting M-Pesa access token: {str(e)}")
    
    def generate_password(self):
        """
        Generate M-Pesa API password
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode('utf-8')
        return password, timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """
        Initiate STK Push payment
        """
        try:
            access_token = self.get_access_token()
            password, timestamp = self.generate_password()
            
            # Format phone number (remove + and ensure it starts with 254)
            phone = str(phone_number).replace('+', '').replace(' ', '')
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            elif not phone.startswith('254'):
                phone = '254' + phone
            
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": str(int(amount)),
                "PartyA": phone,
                "PartyB": self.shortcode,
                "PhoneNumber": phone,
                "CallBackURL": settings.MPESA_CALLBACK_URL,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"STK Push initiated: {data}")
            
            return {
                'success': True,
                'data': data,
                'checkout_request_id': data.get('CheckoutRequestID'),
                'merchant_request_id': data.get('MerchantRequestID')
            }
            
        except requests.RequestException as e:
            logger.error(f"STK Push request failed: {str(e)}")
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"STK Push error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def query_stk_push(self, checkout_request_id):
        """
        Query STK Push status
        """
        try:
            access_token = self.get_access_token()
            password, timestamp = self.generate_password()
            
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"STK Push query result: {data}")
            
            return {
                'success': True,
                'data': data
            }
            
        except requests.RequestException as e:
            logger.error(f"STK Push query failed: {str(e)}")
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"STK Push query error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def b2c_payment(self, phone_number, amount, account_reference, transaction_desc):
        """
        Initiate B2C payment (for payouts)
        """
        try:
            access_token = self.get_access_token()
            
            # Format phone number
            phone = str(phone_number).replace('+', '').replace(' ', '')
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            elif not phone.startswith('254'):
                phone = '254' + phone
            
            payload = {
                "InitiatorName": "testapi",
                "SecurityCredential": "your_security_credential",  # This should be encrypted
                "CommandID": "BusinessPayment",
                "Amount": str(int(amount)),
                "PartyA": self.shortcode,
                "PartyB": phone,
                "Remarks": transaction_desc,
                "QueueTimeOutURL": f"{settings.MPESA_CALLBACK_URL}/b2c/timeout",
                "ResultURL": f"{settings.MPESA_CALLBACK_URL}/b2c/result",
                "Occasion": account_reference
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/mpesa/b2c/v1/paymentrequest"
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"B2C payment initiated: {data}")
            
            return {
                'success': True,
                'data': data,
                'conversation_id': data.get('ConversationID'),
                'originator_conversation_id': data.get('OriginatorConversationID')
            }
            
        except requests.RequestException as e:
            logger.error(f"B2C payment request failed: {str(e)}")
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"B2C payment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def c2b_register_url(self):
        """
        Register C2B validation and confirmation URLs
        """
        try:
            access_token = self.get_access_token()
            
            payload = {
                "ShortCode": self.shortcode,
                "ResponseType": "Completed",
                "ConfirmationURL": f"{settings.MPESA_CALLBACK_URL}/c2b/confirmation",
                "ValidationURL": f"{settings.MPESA_CALLBACK_URL}/c2b/validation"
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/mpesa/c2b/v1/registerurl"
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"C2B URL registration: {data}")
            
            return {
                'success': True,
                'data': data
            }
            
        except requests.RequestException as e:
            logger.error(f"C2B URL registration failed: {str(e)}")
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"C2B URL registration error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


class PaymentProcessor:
    """
    Main payment processor for handling different payment methods
    """
    
    def __init__(self):
        self.mpesa_service = MpesaService()
    
    def process_payment(self, transaction):
        """
        Process payment based on transaction type and method
        """
        try:
            if transaction.payment_method == 'mpesa_stk':
                return self._process_mpesa_stk(transaction)
            elif transaction.payment_method == 'wallet':
                return self._process_wallet_payment(transaction)
            elif transaction.payment_method == 'mpesa_b2c':
                return self._process_mpesa_b2c(transaction)
            else:
                raise ValueError(f"Unsupported payment method: {transaction.payment_method}")
                
        except Exception as e:
            logger.error(f"Payment processing failed for transaction {transaction.id}: {str(e)}")
            transaction.mark_failed(error_message=str(e))
            return False
    
    def _process_mpesa_stk(self, transaction):
        """
        Process M-Pesa STK Push payment
        """
        result = self.mpesa_service.stk_push(
            phone_number=transaction.user.phone_number,
            amount=transaction.amount,
            account_reference=transaction.reference,
            transaction_desc=transaction.description
        )
        
        if result['success']:
            transaction.mpesa_checkout_request_id = result['checkout_request_id']
            transaction.mark_processing()
            return True
        else:
            transaction.mark_failed(error_message=result['error'])
            return False
    
    def _process_wallet_payment(self, transaction):
        """
        Process wallet payment
        """
        try:
            # Check if wallet has sufficient balance
            can_transact, message = transaction.wallet.can_transact(transaction.total_amount)
            if not can_transact:
                transaction.mark_failed(error_message=message)
                return False
            
            # Debit wallet
            wallet_transaction = transaction.wallet.debit(
                amount=transaction.total_amount,
                description=transaction.description,
                reference=transaction.reference
            )
            
            # Mark transaction as completed
            transaction.mark_completed()
            return True
            
        except Exception as e:
            transaction.mark_failed(error_message=str(e))
            return False
    
    def _process_mpesa_b2c(self, transaction):
        """
        Process M-Pesa B2C payment (for payouts)
        """
        result = self.mpesa_service.b2c_payment(
            phone_number=transaction.recipient_phone,
            amount=transaction.amount,
            account_reference=transaction.reference,
            transaction_desc=transaction.description
        )
        
        if result['success']:
            transaction.external_reference = result['conversation_id']
            transaction.mark_processing()
            return True
        else:
            transaction.mark_failed(error_message=result['error'])
            return False
