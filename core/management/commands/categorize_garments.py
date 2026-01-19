from django.core.management.base import BaseCommand
from core.models import GarmentType


class Command(BaseCommand):
    help = 'Auto-categorize garments based on name patterns'

    def handle(self, *args, **options):
        upper_keywords = ['blouse', 'shirt', 'dress', 'jacket', 'coat', 'sweater', 'top', 'blazer']
        lower_keywords = ['skirt', 'shorts', 'trouser', 'pants', 'jeans', 'slacks']
        both_keywords = ['uniform', 'suit', 'jumpsuit', 'overall', 'romper', 'set']

        updated = 0

        for keyword in upper_keywords:
            count = GarmentType.objects.filter(name__icontains=keyword).update(garment_category='upper')
            updated += count
            if count > 0:
                self.stdout.write(f"Upper: '{keyword}' - {count} garments")

        for keyword in lower_keywords:
            count = GarmentType.objects.filter(name__icontains=keyword).update(garment_category='lower')
            updated += count
            if count > 0:
                self.stdout.write(f"Lower: '{keyword}' - {count} garments")

        for keyword in both_keywords:
            count = GarmentType.objects.filter(name__icontains=keyword).update(garment_category='both')
            updated += count
            if count > 0:
                self.stdout.write(f"Both: '{keyword}' - {count} garments")

        self.stdout.write(self.style.SUCCESS(f'\nTotal updated: {updated} garments'))

        # Show remaining uncategorized
        uncategorized = GarmentType.objects.filter(garment_category='upper').count()
        total = GarmentType.objects.count()
        self.stdout.write(f'Garments total: {total}')
