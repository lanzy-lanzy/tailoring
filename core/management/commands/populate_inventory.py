from django.core.management.base import BaseCommand
from core.models import Fabric, Accessory
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate inventory with sample fabrics and accessories'

    def handle(self, *args, **options):
        self.stdout.write('Populating inventory...')

        # Create Fabrics
        fabrics_data = [
            {
                'name': 'Premium Cotton',
                'color': 'White',
                'stock_meters': 150.00,
                'price_per_meter': Decimal('450.00'),
                'description': 'High-quality premium cotton fabric, perfect for shirts and blouses.'
            },
            {
                'name': 'Polycotton Blend',
                'color': 'Light Blue',
                'stock_meters': 120.50,
                'price_per_meter': Decimal('320.00'),
                'description': 'Durable polycotton blend with good drape and comfort.'
            },
            {
                'name': 'Linen Fabric',
                'color': 'Beige',
                'stock_meters': 80.00,
                'price_per_meter': Decimal('550.00'),
                'description': 'Breathable linen fabric, ideal for summer wear.'
            },
            {
                'name': 'Silk Blend',
                'color': 'Navy Blue',
                'stock_meters': 45.00,
                'price_per_meter': Decimal('850.00'),
                'description': 'Elegant silk blend fabric for formal wear.'
            },
            {
                'name': 'Cotton Twill',
                'color': 'Black',
                'stock_meters': 200.00,
                'price_per_meter': Decimal('380.00'),
                'description': 'Sturdy cotton twill for pants and jackets.'
            },
            {
                'name': 'Gingham',
                'color': 'Red/White Check',
                'stock_meters': 60.00,
                'price_per_meter': Decimal('420.00'),
                'description': 'Classic gingham check pattern.'
            },
            {
                'name': 'Chambray',
                'color': 'Light Blue',
                'stock_meters': 90.00,
                'price_per_meter': Decimal('460.00'),
                'description': 'Soft chambray fabric for casual shirts.'
            },
            {
                'name': 'Flannel',
                'color': 'Plaid Red',
                'stock_meters': 70.00,
                'price_per_meter': Decimal('400.00'),
                'description': 'Warm flannel fabric for cold weather.'
            },
            {
                'name': 'Corduroy',
                'color': 'Brown',
                'stock_meters': 55.00,
                'price_per_meter': Decimal('480.00'),
                'description': 'Soft corduroy fabric with fine wale.'
            },
            {
                'name': 'Denim',
                'color': 'Blue',
                'stock_meters': 180.00,
                'price_per_meter': Decimal('350.00'),
                'description': 'Classic denim fabric for jeans and jackets.'
            },
        ]

        for fabric_data in fabrics_data:
            fabric, created = Fabric.objects.get_or_create(
                name=fabric_data['name'],
                color=fabric_data['color'],
                defaults={
                    'stock_meters': fabric_data['stock_meters'],
                    'price_per_meter': fabric_data['price_per_meter'],
                    'description': fabric_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created fabric: {fabric.name} ({fabric.color})')
            else:
                self.stdout.write(f'- Fabric already exists: {fabric.name} ({fabric.color})')

        # Create Accessories
        accessories_data = [
            {
                'name': 'Buttons',
                'unit': 'pieces',
                'stock_quantity': 500,
                'price_per_unit': Decimal('5.00'),
                'description': 'Assorted buttons in various sizes and colors.'
            },
            {
                'name': 'Zippers',
                'unit': 'pieces',
                'stock_quantity': 150,
                'price_per_unit': Decimal('35.00'),
                'description': 'Metal and plastic zippers in various lengths.'
            },
            {
                'name': 'Thread Spool',
                'unit': 'spools',
                'stock_quantity': 200,
                'price_per_unit': Decimal('45.00'),
                'description': 'High-quality thread spools in various colors.'
            },
            {
                'name': 'Interfacing',
                'unit': 'meters',
                'stock_quantity': 100,
                'price_per_unit': Decimal('80.00'),
                'description': 'Fusible interfacing for garment structure.'
            },
            {
                'name': 'Lining Fabric',
                'unit': 'meters',
                'stock_quantity': 80,
                'price_per_unit': Decimal('250.00'),
                'description': 'Polyester lining fabric for jackets and coats.'
            },
            {
                'name': 'Velcro Strips',
                'unit': 'pairs',
                'stock_quantity': 75,
                'price_per_unit': Decimal('15.00'),
                'description': 'Hook and loop velcro strips.'
            },
            {
                'name': 'Buckles',
                'unit': 'pieces',
                'stock_quantity': 100,
                'price_per_unit': Decimal('25.00'),
                'description': 'Metal and plastic buckles for belts and straps.'
            },
            {
                'name': 'Elastic',
                'unit': 'meters',
                'stock_quantity': 50,
                'price_per_unit': Decimal('30.00'),
                'description': 'Stretchy elastic for waistbands and cuffs.'
            },
            {
                'name': 'Ribbons',
                'unit': 'meters',
                'stock_quantity': 60,
                'price_per_unit': Decimal('20.00'),
                'description': 'Decorative ribbons in various colors.'
            },
            {
                'name': 'Patches',
                'unit': 'pieces',
                'stock_quantity': 120,
                'price_per_unit': Decimal('10.00'),
                'description': 'Iron-on and sew-on patches.'
            },
            {
                'name': 'Snaps',
                'unit': 'sets',
                'stock_quantity': 80,
                'price_per_unit': Decimal('12.00'),
                'description': 'Metal snap buttons for closures.'
            },
            {
                'name': 'Hook and Eye',
                'unit': 'sets',
                'stock_quantity': 150,
                'price_per_unit': Decimal('8.00'),
                'description': 'Hook and eye closures.'
            },
        ]

        for accessory_data in accessories_data:
            accessory, created = Accessory.objects.get_or_create(
                name=accessory_data['name'],
                defaults={
                    'unit': accessory_data['unit'],
                    'stock_quantity': accessory_data['stock_quantity'],
                    'price_per_unit': accessory_data['price_per_unit'],
                    'description': accessory_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created accessory: {accessory.name}')
            else:
                self.stdout.write(f'- Accessory already exists: {accessory.name}')

        # Count
        fabric_count = Fabric.objects.count()
        accessory_count = Accessory.objects.count()

        self.stdout.write(self.style.SUCCESS(
            f'\nInventory populated successfully!')
        )
        self.stdout.write(f'  - {fabric_count} fabrics')
        self.stdout.write(f'  - {accessory_count} accessories')
