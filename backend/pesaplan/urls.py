"""
PesaPlan URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pesaplan.utils.health import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    path('api/v1/auth/', include('pesaplan.apps.users.urls')),
    path('api/v1/wallets/', include('pesaplan.apps.wallets.urls')),
    path('api/v1/standing-orders/', include('pesaplan.apps.standing_orders.urls')),
    path('api/v1/transactions/', include('pesaplan.apps.transactions.urls')),
    path('api/v1/payments/', include('pesaplan.apps.payments.urls')),
    path('api/v1/notifications/', include('pesaplan.apps.notifications.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
