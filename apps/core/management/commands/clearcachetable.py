from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Clears all entries from the cache table'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_cache_table")
        self.stdout.write(self.style.SUCCESS("Cache table cleared."))
