# apps/core/management/commands/createcachetable.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connection

class Command(BaseCommand):
    help = 'Creates the cache table for database caching'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS django_cache_table (
                    cache_key VARCHAR(255) NOT NULL PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires DATETIME(6) NOT NULL
                )
            """)