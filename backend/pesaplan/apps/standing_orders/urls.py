"""
Standing Orders URLs for PesaPlan
"""
from django.urls import path
from . import views

urlpatterns = [
    # Standing orders
    path('', views.StandingOrderViewSet.as_view(), name='standing-orders'),
    path('<uuid:pk>/', views.StandingOrderDetailView.as_view(), name='standing-order-detail'),
    path('<uuid:pk>/execute/', views.ExecuteStandingOrderView.as_view(), name='execute-standing-order'),
    path('<uuid:pk>/pause/', views.PauseStandingOrderView.as_view(), name='pause-standing-order'),
    path('<uuid:pk>/resume/', views.ResumeStandingOrderView.as_view(), name='resume-standing-order'),
    path('<uuid:pk>/cancel/', views.CancelStandingOrderView.as_view(), name='cancel-standing-order'),
    path('<uuid:pk>/executions/', views.StandingOrderExecutionsView.as_view(), name='standing-order-executions'),
    
    # Statistics and utilities
    path('stats/', views.standing_order_stats, name='standing-order-stats'),
    path('due/', views.due_standing_orders, name='due-standing-orders'),
]
