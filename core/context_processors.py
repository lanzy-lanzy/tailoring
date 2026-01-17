from django.conf import settings


def shop_info(request):
    """Add shop information to template context"""
    return {
        'SHOP_NAME': getattr(settings, 'SHOP_NAME', 'El Senior Original Tailoring'),
        'SHOP_ADDRESS': getattr(settings, 'SHOP_ADDRESS', ''),
        'SHOP_PHONE': getattr(settings, 'SHOP_PHONE', ''),
    }
