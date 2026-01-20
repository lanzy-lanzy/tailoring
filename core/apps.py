from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.dispatch import receiver
import json

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # Add polyfill for JSON_VALID if using sqlite3
        connection_created.connect(activate_sqlite_json_polyfill)

def activate_sqlite_json_polyfill(sender, connection, **kwargs):
    """
    Polyfill for JSON_VALID function in SQLite.
    Django 4.2+ expects JSON_VALID for JSONField, but it's only built-in for SQLite 3.38+.
    """
    if connection.vendor == 'sqlite':
        connection.connection.create_function('JSON_VALID', 1, is_json_valid)

def is_json_valid(value):
    try:
        if value is None:
            return 1
        json.loads(value)
        return 1
    except (ValueError, TypeError):
        return 0
