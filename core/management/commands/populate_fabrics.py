from django.core.management.base import BaseCommand
from core.models import (
    Fabric, FabricColor, FabricMaterial, Order, Payment,
    TailoringTask, Rework, InventoryLog, OrderAccessory
)


class Command(BaseCommand):
    help = 'Clear current fabrics and populate with fresh data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-only',
            action='store_true',
            help='Only clear data without repopulating',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting fabric data population...')

        # Clear dependent data first
        self.stdout.write(self.style.WARNING('Clearing orders and related data...'))
        deleted_orders, _ = Order.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_orders} orders and related data'))

        # Clear existing data
        self.stdout.write(self.style.WARNING('Clearing existing fabrics...'))
        deleted_fabrics, _ = Fabric.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_fabrics} fabrics'))

        self.stdout.write(self.style.WARNING('Clearing existing colors...'))
        deleted_colors, _ = FabricColor.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_colors} colors'))

        self.stdout.write(self.style.WARNING('Clearing existing materials...'))
        deleted_materials, _ = FabricMaterial.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_materials} materials'))

        if options['clear_only']:
            self.stdout.write(self.style.SUCCESS('Data cleared. Skipping repopulation.'))
            return

        # Create materials
        self.stdout.write(self.style.SUCCESS('Creating fabric materials...'))
        materials_data = [
            'Cotton',
            'Silk',
            'Linen',
            'Wool',
            'Polyester',
            'Linen Fabric',
            'Cotton Twill',
            'Silk Charmeuse',
            'Denim',
            'Satin',
            'Velvet',
            'Chiffon',
            'Crepe',
            'Organza',
            'Taffeta',
        ]

        materials = {}
        for material_name in materials_data:
            material, created = FabricMaterial.objects.get_or_create(name=material_name)
            materials[material_name] = material
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {material_name}')

        # Create colors
        self.stdout.write(self.style.SUCCESS('Creating fabric colors...'))
        colors_data = [
            'Navy Blue',
            'Charcoal Gray',
            'Black',
            'White',
            'Beige',
            'Cream',
            'Red',
            'Burgundy',
            'Blue',
            'Light Blue',
            'Green',
            'Dark Green',
            'Gray',
            'Brown',
            'Gold',
            'Silver',
            'Pink',
            'Rose',
            'Purple',
            'Lavender',
            'Orange',
            'Yellow',
            'Olive',
            'Khaki',
            'Tan',
        ]

        colors = {}
        for color_name in colors_data:
            color, created = FabricColor.objects.get_or_create(name=color_name)
            colors[color_name] = color
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {color_name}')

        # Create sample fabrics
        self.stdout.write(self.style.SUCCESS('Creating sample fabrics...'))
        fabric_data = [
            {
                'material': 'Cotton',
                'color': 'Navy Blue',
                'stock': 50.0,
                'price': 450.00,
                'description': 'Premium cotton fabric, soft and breathable'
            },
            {
                'material': 'Silk',
                'color': 'Cream',
                'stock': 30.0,
                'price': 1200.00,
                'description': 'Pure silk, elegant and smooth'
            },
            {
                'material': 'Linen',
                'color': 'Beige',
                'stock': 40.0,
                'price': 500.00,
                'description': 'Natural linen, lightweight and durable'
            },
            {
                'material': 'Wool',
                'color': 'Charcoal Gray',
                'stock': 25.0,
                'price': 800.00,
                'description': 'Premium wool, perfect for winter wear'
            },
            {
                'material': 'Polyester',
                'color': 'Black',
                'stock': 60.0,
                'price': 300.00,
                'description': 'High-quality polyester, easy to maintain'
            },
            {
                'material': 'Cotton Twill',
                'color': 'Khaki',
                'stock': 45.0,
                'price': 550.00,
                'description': 'Durable cotton twill, perfect for trousers'
            },
            {
                'material': 'Silk Charmeuse',
                'color': 'Red',
                'stock': 20.0,
                'price': 1500.00,
                'description': 'Luxurious silk charmeuse, drapes beautifully'
            },
            {
                'material': 'Denim',
                'color': 'Blue',
                'stock': 70.0,
                'price': 400.00,
                'description': 'Classic denim, perfect for casual wear'
            },
            {
                'material': 'Satin',
                'color': 'Gold',
                'stock': 15.0,
                'price': 900.00,
                'description': 'Glossy satin, ideal for formal wear'
            },
            {
                'material': 'Velvet',
                'color': 'Purple',
                'stock': 18.0,
                'price': 1100.00,
                'description': 'Soft velvet, adds elegance and texture'
            },
        ]

        for data in fabric_data:
            material = materials.get(data['material'])
            color = colors.get(data['color'])

            if material and color:
                fabric, created = Fabric.objects.get_or_create(
                    material=material,
                    color=color,
                    defaults={
                        'stock_meters': data['stock'],
                        'price_per_meter': data['price'],
                        'description': data['description']
                    }
                )
                status = 'Created' if created else 'Exists'
                self.stdout.write(
                    f'  {status}: {material.name} ({color.name}) - {data["stock"]}m @ PHP {data["price"]}/m'
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated fabric data!'))
