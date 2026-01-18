from django.conf import settings


def shop_info(request):
    """Add shop information to template context"""
    return {
        'SHOP_NAME': getattr(settings, 'SHOP_NAME', 'El Senior Original Tailoring'),
        'SHOP_ADDRESS': getattr(settings, 'SHOP_ADDRESS', ''),
        'SHOP_PHONE': getattr(settings, 'SHOP_PHONE', ''),
    }


def notifications(request):
    """
    Add notification data to template context for authenticated users.
    This allows the notification bell/dropdown to work on all pages.
    """
    if not request.user.is_authenticated:
        return {
            'unread_notification_count': 0,
            'recent_notifications': [],
            'has_unread_notifications': False,
        }
    
    from .models import Notification
    
    # Get unread count
    unread_count = Notification.get_unread_count(request.user)
    
    # Get recent notifications (last 10)
    recent_notifications = Notification.get_recent_notifications(request.user, limit=10)
    
    # Get notifications by priority
    urgent_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False,
        priority__in=['urgent', 'high']
    ).count()
    
    return {
        'unread_notification_count': unread_count,
        'recent_notifications': recent_notifications,
        'has_unread_notifications': unread_count > 0,
        'urgent_notification_count': urgent_count,
        'has_urgent_notifications': urgent_count > 0,
    }
