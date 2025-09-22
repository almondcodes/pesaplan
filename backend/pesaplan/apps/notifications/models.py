"""
Notification models for PesaPlan
"""
import uuid
from django.db import models
from django.utils import timezone
from pesaplan.apps.users.models import User


class Notification(models.Model):
    """
    Notification model for user communications
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('payment_success', 'Payment Success'),
        ('payment_failed', 'Payment Failed'),
        ('standing_order_created', 'Standing Order Created'),
        ('standing_order_executed', 'Standing Order Executed'),
        ('standing_order_failed', 'Standing Order Failed'),
        ('wallet_topup', 'Wallet Top-up'),
        ('wallet_low_balance', 'Low Wallet Balance'),
        ('security_alert', 'Security Alert'),
        ('system_maintenance', 'System Maintenance'),
        ('promotional', 'Promotional'),
    ]
    
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    
    # Notification details
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Status and delivery
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # External service references
    external_id = models.CharField(max_length=100, null=True, blank=True)
    delivery_receipt = models.CharField(max_length=100, null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['channel']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.notification_type} ({self.status})"

    def mark_sent(self, external_id=None):
        """Mark notification as sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        if external_id:
            self.external_id = external_id
        self.save(update_fields=['status', 'sent_at', 'external_id'])

    def mark_delivered(self, delivery_receipt=None):
        """Mark notification as delivered"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        if delivery_receipt:
            self.delivery_receipt = delivery_receipt
        self.save(update_fields=['status', 'delivered_at', 'delivery_receipt'])

    def mark_failed(self, error_message=None):
        """Mark notification as failed"""
        self.status = 'failed'
        if error_message:
            self.error_message = error_message
        self.retry_count += 1
        self.save(update_fields=['status', 'error_message', 'retry_count'])

    def can_retry(self):
        """Check if notification can be retried"""
        return (
            self.status == 'failed' and 
            self.retry_count < self.max_retries
        )


class NotificationTemplate(models.Model):
    """
    Notification templates for different types of messages
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('payment_success', 'Payment Success'),
        ('payment_failed', 'Payment Failed'),
        ('standing_order_created', 'Standing Order Created'),
        ('standing_order_executed', 'Standing Order Executed'),
        ('standing_order_failed', 'Standing Order Failed'),
        ('wallet_topup', 'Wallet Top-up'),
        ('wallet_low_balance', 'Low Wallet Balance'),
        ('security_alert', 'Security Alert'),
        ('system_maintenance', 'System Maintenance'),
        ('promotional', 'Promotional'),
    ]
    
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
    ]

    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    title_template = models.CharField(max_length=255)
    message_template = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_templates'
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
        unique_together = ['notification_type', 'channel']
        indexes = [
            models.Index(fields=['notification_type', 'channel']),
        ]

    def __str__(self):
        return f"{self.notification_type} - {self.channel}"

    def render_message(self, context):
        """Render template with context variables"""
        try:
            return self.message_template.format(**context)
        except KeyError as e:
            # Log error and return template as-is
            return self.message_template


class NotificationPreference(models.Model):
    """
    User notification preferences
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='notification_preferences'
    )
    
    # Channel preferences
    sms_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
    # Type preferences
    payment_notifications = models.BooleanField(default=True)
    standing_order_notifications = models.BooleanField(default=True)
    wallet_notifications = models.BooleanField(default=True)
    security_notifications = models.BooleanField(default=True)
    promotional_notifications = models.BooleanField(default=False)
    
    # Timing preferences
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='Africa/Nairobi')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'

    def __str__(self):
        return f"{self.user.full_name}'s Notification Preferences"

    def is_channel_enabled(self, channel):
        """Check if a specific channel is enabled"""
        channel_map = {
            'sms': self.sms_enabled,
            'email': self.email_enabled,
            'push': self.push_enabled,
            'in_app': self.in_app_enabled,
        }
        return channel_map.get(channel, False)

    def is_type_enabled(self, notification_type):
        """Check if a specific notification type is enabled"""
        type_map = {
            'payment_success': self.payment_notifications,
            'payment_failed': self.payment_notifications,
            'standing_order_created': self.standing_order_notifications,
            'standing_order_executed': self.standing_order_notifications,
            'standing_order_failed': self.standing_order_notifications,
            'wallet_topup': self.wallet_notifications,
            'wallet_low_balance': self.wallet_notifications,
            'security_alert': self.security_notifications,
            'system_maintenance': self.security_notifications,
            'promotional': self.promotional_notifications,
        }
        return type_map.get(notification_type, True)

    def is_quiet_hours(self):
        """Check if current time is within quiet hours"""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        now = timezone.now().time()
        return self.quiet_hours_start <= now <= self.quiet_hours_end
