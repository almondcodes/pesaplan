"""
Tests for Wallet API views
"""
import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from pesaplan.apps.wallets.models import Wallet, WalletTransaction


@pytest.mark.django_db
class TestWalletBalanceView:
    """Test wallet balance API"""
    
    def test_get_wallet_balance_success(self, authenticated_client, wallet):
        """Test successful wallet balance retrieval"""
        # Set wallet balance
        wallet.balance = Decimal('1500.00')
        wallet.save()
        
        url = reverse('wallet-balance')
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['balance'] == '1500.00'
        assert response.data['currency'] == 'KES'
        assert 'last_updated' in response.data
    
    def test_get_wallet_balance_unauthorized(self, api_client):
        """Test wallet balance retrieval without authentication"""
        url = reverse('wallet-balance')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_wallet_balance_no_wallet(self, authenticated_client, user):
        """Test wallet balance retrieval when user has no wallet"""
        # Delete the wallet if it exists
        if hasattr(user, 'wallet'):
            user.wallet.delete()
        
        url = reverse('wallet-balance')
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestWalletTransactionsView:
    """Test wallet transactions API"""
    
    def test_get_wallet_transactions_success(self, authenticated_client, wallet):
        """Test successful wallet transactions retrieval"""
        # Create some transactions
        for i in range(3):
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='deposit',
                amount=Decimal(f'{100 * (i + 1)}.00'),
                balance_before=Decimal(f'{100 * i}.00'),
                balance_after=Decimal(f'{100 * (i + 1)}.00'),
                description=f'Deposit {i + 1}'
            )
        
        url = reverse('wallet-transactions')
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert response.data[0]['amount'] == '300.00'  # Most recent first
        assert response.data[2]['amount'] == '100.00'  # Oldest last
    
    def test_get_wallet_transactions_unauthorized(self, api_client):
        """Test wallet transactions retrieval without authentication"""
        url = reverse('wallet-transactions')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_wallet_transactions_no_wallet(self, authenticated_client, user):
        """Test wallet transactions retrieval when user has no wallet"""
        # Delete the wallet if it exists
        if hasattr(user, 'wallet'):
            user.wallet.delete()
        
        url = reverse('wallet-transactions')
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_wallet_transactions_pagination(self, authenticated_client, wallet):
        """Test wallet transactions pagination"""
        # Create many transactions
        for i in range(25):
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='deposit',
                amount=Decimal('100.00'),
                balance_before=Decimal('0.00'),
                balance_after=Decimal('100.00'),
                description=f'Deposit {i + 1}'
            )
        
        url = reverse('wallet-transactions')
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 20  # Default page size
        assert 'next' in response.data or 'previous' in response.data


@pytest.mark.django_db
class TestWalletDepositView:
    """Test wallet deposit API"""
    
    def test_wallet_deposit_success(self, authenticated_client, wallet):
        """Test successful wallet deposit"""
        initial_balance = wallet.balance
        
        url = reverse('wallet-deposit')
        data = {
            'amount': '500.00',
            'description': 'Test deposit',
            'payment_method': 'mpesa'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['amount'] == '500.00'
        assert response.data['status'] == 'pending'
        assert response.data['description'] == 'Test deposit'
        
        # Check transaction was created
        transaction = WalletTransaction.objects.get(
            wallet=wallet,
            amount=Decimal('500.00')
        )
        assert transaction.transaction_type == 'deposit'
        assert transaction.description == 'Test deposit'
    
    def test_wallet_deposit_unauthorized(self, api_client):
        """Test wallet deposit without authentication"""
        url = reverse('wallet-deposit')
        data = {
            'amount': '500.00',
            'description': 'Test deposit',
            'payment_method': 'mpesa'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_wallet_deposit_invalid_amount(self, authenticated_client):
        """Test wallet deposit with invalid amount"""
        url = reverse('wallet-deposit')
        data = {
            'amount': '-100.00',  # Negative amount
            'description': 'Test deposit',
            'payment_method': 'mpesa'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'amount' in response.data
    
    def test_wallet_deposit_missing_fields(self, authenticated_client):
        """Test wallet deposit with missing required fields"""
        url = reverse('wallet-deposit')
        data = {
            'amount': '500.00',
            # Missing description and payment_method
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'description' in response.data
        assert 'payment_method' in response.data


@pytest.mark.django_db
class TestWalletWithdrawView:
    """Test wallet withdrawal API"""
    
    def test_wallet_withdraw_success(self, authenticated_client, wallet):
        """Test successful wallet withdrawal"""
        # Set wallet balance
        wallet.balance = Decimal('1000.00')
        wallet.save()
        
        url = reverse('wallet-withdraw')
        data = {
            'amount': '200.00',
            'description': 'Test withdrawal',
            'recipient_phone': '+254712345678',
            'recipient_name': 'Test Recipient'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['amount'] == '200.00'
        assert response.data['status'] == 'pending'
        assert response.data['description'] == 'Test withdrawal'
        
        # Check transaction was created
        transaction = WalletTransaction.objects.get(
            wallet=wallet,
            amount=Decimal('200.00')
        )
        assert transaction.transaction_type == 'withdrawal'
        assert transaction.description == 'Test withdrawal'
    
    def test_wallet_withdraw_insufficient_funds(self, authenticated_client, wallet):
        """Test wallet withdrawal with insufficient funds"""
        # Set wallet balance to low amount
        wallet.balance = Decimal('100.00')
        wallet.save()
        
        url = reverse('wallet-withdraw')
        data = {
            'amount': '200.00',  # More than available balance
            'description': 'Test withdrawal',
            'recipient_phone': '+254712345678',
            'recipient_name': 'Test Recipient'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'amount' in response.data
    
    def test_wallet_withdraw_unauthorized(self, api_client):
        """Test wallet withdrawal without authentication"""
        url = reverse('wallet-withdraw')
        data = {
            'amount': '200.00',
            'description': 'Test withdrawal',
            'recipient_phone': '+254712345678',
            'recipient_name': 'Test Recipient'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_wallet_withdraw_missing_fields(self, authenticated_client):
        """Test wallet withdrawal with missing required fields"""
        url = reverse('wallet-withdraw')
        data = {
            'amount': '200.00',
            # Missing description, recipient_phone, recipient_name
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'description' in response.data
        assert 'recipient_phone' in response.data
        assert 'recipient_name' in response.data


@pytest.mark.django_db
class TestWalletTransferView:
    """Test wallet transfer API"""
    
    def test_wallet_transfer_success(self, authenticated_client, wallet, sample_users):
        """Test successful wallet transfer"""
        # Set wallet balance
        wallet.balance = Decimal('1000.00')
        wallet.save()
        
        # Get recipient user and wallet
        recipient = sample_users[0]
        recipient_wallet, created = Wallet.objects.get_or_create(user=recipient)
        
        url = reverse('wallet-transfer')
        data = {
            'amount': '300.00',
            'description': 'Test transfer',
            'recipient_phone': recipient.phone_number
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['amount'] == '300.00'
        assert response.data['status'] == 'pending'
        assert response.data['description'] == 'Test transfer'
        
        # Check transactions were created
        sender_transaction = WalletTransaction.objects.get(
            wallet=wallet,
            amount=Decimal('300.00'),
            transaction_type='transfer_out'
        )
        assert sender_transaction.description == 'Test transfer'
        
        recipient_transaction = WalletTransaction.objects.get(
            wallet=recipient_wallet,
            amount=Decimal('300.00'),
            transaction_type='transfer_in'
        )
        assert recipient_transaction.description == 'Test transfer'
    
    def test_wallet_transfer_insufficient_funds(self, authenticated_client, wallet, sample_users):
        """Test wallet transfer with insufficient funds"""
        # Set wallet balance to low amount
        wallet.balance = Decimal('100.00')
        wallet.save()
        
        recipient = sample_users[0]
        
        url = reverse('wallet-transfer')
        data = {
            'amount': '200.00',  # More than available balance
            'description': 'Test transfer',
            'recipient_phone': recipient.phone_number
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'amount' in response.data
    
    def test_wallet_transfer_invalid_recipient(self, authenticated_client, wallet):
        """Test wallet transfer to invalid recipient"""
        wallet.balance = Decimal('1000.00')
        wallet.save()
        
        url = reverse('wallet-transfer')
        data = {
            'amount': '200.00',
            'description': 'Test transfer',
            'recipient_phone': '+254712345999'  # Non-existent user
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'recipient_phone' in response.data
    
    def test_wallet_transfer_unauthorized(self, api_client):
        """Test wallet transfer without authentication"""
        url = reverse('wallet-transfer')
        data = {
            'amount': '200.00',
            'description': 'Test transfer',
            'recipient_phone': '+254712345678'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestWalletTransactionDetailView:
    """Test wallet transaction detail API"""
    
    def test_get_wallet_transaction_success(self, authenticated_client, wallet):
        """Test successful wallet transaction retrieval"""
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='deposit',
            amount=Decimal('500.00'),
            balance_before=Decimal('0.00'),
            balance_after=Decimal('500.00'),
            description='Test deposit'
        )
        
        url = reverse('wallet-transaction-detail', kwargs={'pk': transaction.id})
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['amount'] == '500.00'
        assert response.data['transaction_type'] == 'deposit'
        assert response.data['description'] == 'Test deposit'
    
    def test_get_wallet_transaction_unauthorized(self, api_client, wallet):
        """Test wallet transaction retrieval without authentication"""
        transaction = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='deposit',
            amount=Decimal('500.00'),
            balance_before=Decimal('0.00'),
            balance_after=Decimal('500.00'),
            description='Test deposit'
        )
        
        url = reverse('wallet-transaction-detail', kwargs={'pk': transaction.id})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_wallet_transaction_not_found(self, authenticated_client):
        """Test wallet transaction retrieval for non-existent transaction"""
        url = reverse('wallet-transaction-detail', kwargs={'pk': 99999})
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_wallet_transaction_other_user(self, authenticated_client, sample_users):
        """Test wallet transaction retrieval for another user's transaction"""
        other_user = sample_users[0]
        other_wallet, created = Wallet.objects.get_or_create(user=other_user)
        
        transaction = WalletTransaction.objects.create(
            wallet=other_wallet,
            transaction_type='deposit',
            amount=Decimal('500.00'),
            balance_before=Decimal('0.00'),
            balance_after=Decimal('500.00'),
            description='Test deposit'
        )
        
        url = reverse('wallet-transaction-detail', kwargs={'pk': transaction.id})
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
