from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    UserProfile, Customer, Fabric, Accessory, 
    GarmentType, GarmentTypeAccessory
)
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up initial data for the tailoring system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@tailorpro.com',
                'first_name': 'System',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            UserProfile.objects.create(user=admin_user, role='admin', phone='09171234567')
            self.stdout.write(self.style.SUCCESS('Created admin user (username: admin, password: admin123)'))
        else:
            self.stdout.write('Admin user already exists')
        
        # Create a tailor user
        tailor_user, created = User.objects.get_or_create(
            username='tailor1',
            defaults={
                'email': 'tailor1@tailorpro.com',
                'first_name': 'Juan',
                'last_name': 'Dela Cruz',
            }
        )
        if created:
            tailor_user.set_password('tailor123')
            tailor_user.save()
            UserProfile.objects.create(user=tailor_user, role='tailor', phone='09181234567')
            self.stdout.write(self.style.SUCCESS('Created tailor user (username: tailor1, password: tailor123)'))
        else:
            self.stdout.write('Tailor user already exists')
        
        # Create sample fabrics
        fabrics_data = [
            {'name': 'Cotton White', 'color': 'White', 'stock_meters': Decimal('50.00'), 'price_per_meter': Decimal('150.00')},
            {'name': 'Cotton Black', 'color': 'Black', 'stock_meters': Decimal('45.00'), 'price_per_meter': Decimal('150.00')},
            {'name': 'Linen Cream', 'color': 'Cream', 'stock_meters': Decimal('30.00'), 'price_per_meter': Decimal('250.00')},
            {'name': 'Silk Red', 'color': 'Red', 'stock_meters': Decimal('20.00'), 'price_per_meter': Decimal('450.00')},
            {'name': 'Polyester Blue', 'color': 'Blue', 'stock_meters': Decimal('60.00'), 'price_per_meter': Decimal('100.00')},
            {'name': 'Barong Jusi', 'color': 'Ivory', 'stock_meters': Decimal('25.00'), 'price_per_meter': Decimal('500.00')},
            {'name': 'Uniform Twill', 'color': 'Khaki', 'stock_meters': Decimal('40.00'), 'price_per_meter': Decimal('180.00')},
        ]
        
        for fabric_data in fabrics_data:
            fabric, created = Fabric.objects.get_or_create(
                name=fabric_data['name'],
                defaults=fabric_data
            )
            if created:
                self.stdout.write(f'  Created fabric: {fabric.name}')
        
        # Create sample accessories
        accessories_data = [
            {'name': 'Buttons (Small)', 'unit': 'pcs', 'stock_quantity': Decimal('500'), 'price_per_unit': Decimal('5.00')},
            {'name': 'Buttons (Large)', 'unit': 'pcs', 'stock_quantity': Decimal('300'), 'price_per_unit': Decimal('8.00')},
            {'name': 'Zipper (6 inch)', 'unit': 'pcs', 'stock_quantity': Decimal('100'), 'price_per_unit': Decimal('25.00')},
            {'name': 'Zipper (12 inch)', 'unit': 'pcs', 'stock_quantity': Decimal('80'), 'price_per_unit': Decimal('35.00')},
            {'name': 'Thread (White)', 'unit': 'rolls', 'stock_quantity': Decimal('50'), 'price_per_unit': Decimal('30.00')},
            {'name': 'Thread (Black)', 'unit': 'rolls', 'stock_quantity': Decimal('50'), 'price_per_unit': Decimal('30.00')},
            {'name': 'Lining Fabric', 'unit': 'meters', 'stock_quantity': Decimal('40'), 'price_per_unit': Decimal('80.00')},
            {'name': 'Elastic Band', 'unit': 'meters', 'stock_quantity': Decimal('60'), 'price_per_unit': Decimal('15.00')},
            {'name': 'Hook and Eye', 'unit': 'pcs', 'stock_quantity': Decimal('200'), 'price_per_unit': Decimal('3.00')},
        ]
        
        accessories = {}
        for acc_data in accessories_data:
            accessory, created = Accessory.objects.get_or_create(
                name=acc_data['name'],
                defaults=acc_data
            )
            accessories[acc_data['name']] = accessory
            if created:
                self.stdout.write(f'  Created accessory: {accessory.name}')
        
        # Create sample garment types
        garment_types_data = [
            {
                'name': 'Dress',
                'description': 'Custom-made dress',
                'estimated_fabric_meters': Decimal('3.00'),
                'base_price': Decimal('1500.00'),
                'accessories': [('Zipper (12 inch)', 1), ('Thread (White)', 0.5), ('Hook and Eye', 2)]
            },
            {
                'name': 'Polo Shirt',
                'description': 'Custom polo shirt',
                'estimated_fabric_meters': Decimal('1.50'),
                'base_price': Decimal('800.00'),
                'accessories': [('Buttons (Small)', 4), ('Thread (White)', 0.3)]
            },
            {
                'name': 'Pants',
                'description': 'Custom-made pants/trousers',
                'estimated_fabric_meters': Decimal('2.00'),
                'base_price': Decimal('1000.00'),
                'accessories': [('Zipper (6 inch)', 1), ('Buttons (Large)', 1), ('Hook and Eye', 1)]
            },
            {
                'name': 'Barong Tagalog',
                'description': 'Traditional Filipino formal wear',
                'estimated_fabric_meters': Decimal('2.50'),
                'base_price': Decimal('2500.00'),
                'accessories': [('Buttons (Small)', 6), ('Thread (White)', 0.5)]
            },
            {
                'name': 'Uniform Set',
                'description': 'School or office uniform (top and bottom)',
                'estimated_fabric_meters': Decimal('3.50'),
                'base_price': Decimal('1800.00'),
                'accessories': [('Buttons (Large)', 5), ('Zipper (6 inch)', 1), ('Thread (Black)', 0.5)]
            },
            {
                'name': 'Blouse',
                'description': 'Custom blouse for women',
                'estimated_fabric_meters': Decimal('1.50'),
                'base_price': Decimal('700.00'),
                'accessories': [('Buttons (Small)', 6), ('Thread (White)', 0.3)]
            },
            {
                'name': 'Skirt',
                'description': 'Custom-made skirt',
                'estimated_fabric_meters': Decimal('1.50'),
                'base_price': Decimal('600.00'),
                'accessories': [('Zipper (6 inch)', 1), ('Hook and Eye', 1), ('Elastic Band', 0.5)]
            },
            {
                'name': 'Gown',
                'description': 'Formal gown for special occasions',
                'estimated_fabric_meters': Decimal('5.00'),
                'base_price': Decimal('5000.00'),
                'accessories': [('Zipper (12 inch)', 1), ('Lining Fabric', 3), ('Hook and Eye', 3)]
            },
        ]
        
        for gt_data in garment_types_data:
            accessory_reqs = gt_data.pop('accessories')
            garment_type, created = GarmentType.objects.get_or_create(
                name=gt_data['name'],
                defaults=gt_data
            )
            if created:
                self.stdout.write(f'  Created garment type: {garment_type.name}')
                
                # Add accessory requirements
                for acc_name, qty in accessory_reqs:
                    if acc_name in accessories:
                        GarmentTypeAccessory.objects.create(
                            garment_type=garment_type,
                            accessory=accessories[acc_name],
                            quantity_required=Decimal(str(qty))
                        )
        
        # Create sample customers
        customers_data = [
            {'name': 'Maria Santos', 'contact_number': '09171112222', 'address': '123 Main St, Manila', 'email': 'maria@email.com'},
            {'name': 'Jose Reyes', 'contact_number': '09183334444', 'address': '456 Oak Ave, Quezon City', 'email': 'jose@email.com'},
            {'name': 'Anna Cruz', 'contact_number': '09195556666', 'address': '789 Pine Rd, Makati', 'email': 'anna@email.com'},
        ]
        
        for cust_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                contact_number=cust_data['contact_number'],
                defaults=cust_data
            )
            if created:
                self.stdout.write(f'  Created customer: {customer.name}')
        
        self.stdout.write(self.style.SUCCESS('\nSetup complete!'))
        self.stdout.write('\nYou can now log in with:')
        self.stdout.write('  Admin: username=admin, password=admin123')
        self.stdout.write('  Tailor: username=tailor1, password=tailor123')
        self.stdout.write('\nRun the development server: python manage.py runserver')
