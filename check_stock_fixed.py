import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tailoring_system.settings')
django.setup()

from core.models import Fabric, Accessory

print("Fabrics <= 20m:")
for f in Fabric.objects.filter(stock_meters__lte=20):
    print(f"  {f.material.name if f.material else 'Unknown'} ({f.color.name}): {f.stock_meters}m")

print(f"\nTotal fabrics <= 20m: {Fabric.objects.filter(stock_meters__lte=20).count()}")

print("\nAccessories <= 50:")
for a in Accessory.objects.filter(stock_quantity__lte=50):
    print(f"  {a.name}: {a.stock_quantity} {a.unit}")
    
print(f"\nTotal accessories <= 50: {Accessory.objects.filter(stock_quantity__lte=50).count()}")
print(f"\nTotal low stock items: {Fabric.objects.filter(stock_meters__lte=20).count() + Accessory.objects.filter(stock_quantity__lte=50).count()}")
