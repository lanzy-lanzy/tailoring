from django import template
from django.contrib.auth.models import User
from ..models import Accessory

register = template.Library()


@register.filter
def get_tailors(user):
    """Get all active tailors for dropdown"""
    return User.objects.filter(profile__role='tailor', is_active=True)


@register.filter
def get_accessories(user):
    """Get all accessories for dropdown"""
    return Accessory.objects.all()
