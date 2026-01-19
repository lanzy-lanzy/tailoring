from django.core.management.base import BaseCommand
from core.models import GarmentType, Fabric
from decimal import Decimal
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Populate realistic garment types'

    def handle(self, *args, **options):
        self.stdout.write('Populating garment types...')

        # Get default fabric (or use first available)
        default_fabric = Fabric.objects.first()
        if not default_fabric:
            self.stdout.write(self.style.ERROR('No fabric found. Please populate inventory first.'))
            return

        garment_types_data = [
            {
                'name': 'Long Sleeve Shirt',
                'garment_category': 'upper',
                'description': 'Classic long sleeve shirt with collar and cuffs. Perfect for formal and casual wear.',
                'estimated_fabric_meters': Decimal('2.5'),
                'base_price': Decimal('850.00'),
            },
            {
                'name': 'Short Sleeve Shirt',
                'garment_category': 'upper',
                'description': 'Comfortable short sleeve shirt with collar. Great for warm weather.',
                'estimated_fabric_meters': Decimal('2.0'),
                'base_price': Decimal('750.00'),
            },
            {
                'name': 'Polo Shirt',
                'garment_category': 'upper',
                'description': 'Casual polo shirt with collar and button placket.',
                'estimated_fabric_meters': Decimal('2.0'),
                'base_price': Decimal('700.00'),
            },
            {
                'name': 'Tuxedo Shirt',
                'garment_category': 'upper',
                'description': 'Formal tuxedo shirt with wing collar and stud buttons. For weddings and black tie events.',
                'estimated_fabric_meters': Decimal('3.0'),
                'base_price': Decimal('1200.00'),
            },
            {
                'name': 'Long Pants',
                'garment_category': 'lower',
                'description': 'Classic long pants with zipper fly, belt loops, and pockets.',
                'estimated_fabric_meters': Decimal('2.5'),
                'base_price': Decimal('900.00'),
            },
            {
                'name': 'Shorts',
                'garment_category': 'lower',
                'description': 'Comfortable shorts with elastic or button waist.',
                'estimated_fabric_meters': Decimal('1.5'),
                'base_price': Decimal('650.00'),
            },
            {
                'name': 'Formal Trousers',
                'garment_category': 'lower',
                'description': 'Elegant dress trousers with pleats or flat front, perfect for suits.',
                'estimated_fabric_meters': Decimal('2.8'),
                'base_price': Decimal('1100.00'),
            },
            {
                'name': 'Jeans',
                'garment_category': 'lower',
                'description': 'Classic denim jeans with five-pocket styling.',
                'estimated_fabric_meters': Decimal('2.0'),
                'base_price': Decimal('800.00'),
            },
            {
                'name': 'Blazer',
                'garment_category': 'upper',
                'description': 'Classic single-breasted blazer with notched lapels. Versatile for formal and smart-casual.',
                'estimated_fabric_meters': Decimal('3.5'),
                'base_price': Decimal('1500.00'),
            },
            {
                'name': 'Suit Jacket',
                'garment_category': 'upper',
                'description': 'Formal suit jacket with notched or peaked lapels. Part of two-piece or three-piece suit.',
                'estimated_fabric_meters': Decimal('3.5'),
                'base_price': Decimal('1800.00'),
            },
            {
                'name': 'Formal Coat',
                'garment_category': 'upper',
                'description': 'Elegant formal coat for special occasions and cold weather.',
                'estimated_fabric_meters': Decimal('4.0'),
                'base_price': Decimal('2200.00'),
            },
            {
                'name': 'Dress',
                'garment_category': 'both',
                'description': 'A-line dress with fitted bodice and flowing skirt. Classic feminine style.',
                'estimated_fabric_meters': Decimal('3.0'),
                'base_price': Decimal('1500.00'),
            },
            {
                'name': 'Long Dress',
                'garment_category': 'both',
                'description': 'Elegant floor-length dress with fitted waist. Perfect for formal events.',
                'estimated_fabric_meters': Decimal('4.0'),
                'base_price': Decimal('2000.00'),
            },
            {
                'name': 'Short Dress',
                'garment_category': 'both',
                'description': 'Cute above-knee dress perfect for casual and semi-formal occasions.',
                'estimated_fabric_meters': Decimal('2.5'),
                'base_price': Decimal('1200.00'),
            },
            {
                'name': 'Gown',
                'garment_category': 'both',
                'description': 'Formal evening gown with elegant details. For proms, weddings, and galas.',
                'estimated_fabric_meters': Decimal('5.0'),
                'base_price': Decimal('3000.00'),
            },
            {
                'name': 'Long Sleeve Polo',
                'garment_category': 'upper',
                'description': 'Long sleeve version of classic polo for cooler weather.',
                'estimated_fabric_meters': Decimal('2.2'),
                'base_price': Decimal('800.00'),
            },
            {
                'name': 'Henley Shirt',
                'garment_category': 'upper',
                'description': 'Casual pullover shirt with button placket at neckline.',
                'estimated_fabric_meters': Decimal('2.0'),
                'base_price': Decimal('720.00'),
            },
            {
                'name': 'Chino Pants',
                'garment_category': 'lower',
                'description': 'Comfortable chino pants with flat front design.',
                'estimated_fabric_meters': Decimal('2.3'),
                'base_price': Decimal('850.00'),
            },
            {
                'name': 'Cargo Pants',
                'garment_category': 'lower',
                'description': 'Utility pants with multiple cargo pockets.',
                'estimated_fabric_meters': Decimal('2.5'),
                'base_price': Decimal('900.00'),
            },
            {
                'name': 'Two-Piece Suit',
                'garment_category': 'both',
                'description': 'Complete suit with jacket and matching trousers. Formal attire for business and special events.',
                'estimated_fabric_meters': Decimal('6.0'),
                'base_price': Decimal('2800.00'),
            },
            {
                'name': 'Three-Piece Suit',
                'garment_category': 'both',
                'description': 'Complete suit with jacket, trousers, and matching vest. Ultimate formal attire.',
                'estimated_fabric_meters': Decimal('7.5'),
                'base_price': Decimal('3500.00'),
            },
            {
                'name': 'Barong Tagalog',
                'garment_category': 'upper',
                'description': 'Traditional Filipino formal wear with intricate embroidery. For weddings and special occasions.',
                'estimated_fabric_meters': Decimal('3.0'),
                'base_price': Decimal('2500.00'),
            },
            {
                'name': 'Saya (Skirt)',
                'garment_category': 'lower',
                'description': 'Traditional Filipino skirt, often worn with Barong.',
                'estimated_fabric_meters': Decimal('2.5'),
                'base_price': Decimal('1200.00'),
            },
            {
                'name': 'Kimona',
                'garment_category': 'upper',
                'description': 'Traditional Filipino blouse/dress top.',
                'estimated_fabric_meters': Decimal('2.0'),
                'base_price': Decimal('900.00'),
            },
            {
                'name': 'Vest',
                'garment_category': 'upper',
                'description': 'Formal vest that can be worn alone or as part of three-piece suit.',
                'estimated_fabric_meters': Decimal('1.5'),
                'base_price': Decimal('700.00'),
            },
            {
                'name': 'Cardigan',
                'garment_category': 'upper',
                'description': 'Button-up cardigan sweater with open front.',
                'estimated_fabric_meters': Decimal('2.0'),
                'base_price': Decimal('650.00'),
            },
            {
                'name': 'Blouse',
                'garment_category': 'upper',
                'description': 'Feminine blouse with various necklines and sleeve styles.',
                'estimated_fabric_meters': Decimal('2.2'),
                'base_price': Decimal('800.00'),
            },
            {
                'name': 'Maxi Dress',
                'garment_category': 'both',
                'description': 'Long, flowing maxi dress perfect for beach and casual wear.',
                'estimated_fabric_meters': Decimal('4.5'),
                'base_price': Decimal('1800.00'),
            },
            {
                'name': 'Midi Dress',
                'garment_category': 'both',
                'description': 'Mid-length dress falling between knee and ankle.',
                'estimated_fabric_meters': Decimal('3.5'),
                'base_price': Decimal('1500.00'),
            },
            {
                'name': 'Jumpsuit',
                'garment_category': 'both',
                'description': 'One-piece garment combining top and pants.',
                'estimated_fabric_meters': Decimal('3.5'),
                'base_price': Decimal('1600.00'),
            },
            {
                'name': 'Romper',
                'garment_category': 'both',
                'description': 'One-piece garment combining top and shorts.',
                'estimated_fabric_meters': Decimal('2.5'),
                'base_price': Decimal('1100.00'),
            },
        ]

        created_count = 0
        updated_count = 0

        for garment_data in garment_types_data:
            garment, created = GarmentType.objects.get_or_create(
                name=garment_data['name'],
                defaults={
                    'garment_category': garment_data['garment_category'],
                    'description': garment_data['description'],
                    'estimated_fabric_meters': garment_data['estimated_fabric_meters'],
                    'base_price': garment_data['base_price'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created garment: {garment.name} - {garment.get_garment_category_display()}')
            else:
                # Update existing with correct category
                if garment.garment_category != garment_data['garment_category']:
                    garment.garment_category = garment_data['garment_category']
                    garment.save()
                    self.stdout.write(f'Updated garment category: {garment.name} -> {garment.get_garment_category_display()}')
                else:
                    updated_count += 1
                    self.stdout.write(f'- Garment already exists: {garment.name}')

        total = created_count + updated_count
        self.stdout.write(self.style.SUCCESS(
            f'\nGarment types populated successfully!')
        )
        self.stdout.write(f'  - {created_count} created')
        self.stdout.write(f'  - {updated_count} already existed')
        self.stdout.write(f'  - Total: {total} garment types')
