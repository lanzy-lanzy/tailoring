import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tailoring_system.settings')
django.setup()

from core.models import Fabric, Accessory

print("All fabrics:")
for f in Fabric.objects.all():
    print(f"  {f.material.name if f.material else 'Unknown'} ({f.color.name}): {f.stock_meters}m")

print("\nFabrics <= 5m:", Fabric.objects.filter(stock_meters__lte=5).count())
print("Fabrics <= 15m:", Fabric.objects.filter(stock_meters__lte=15).count())

print("\nAll accessories:")
for a in Accessory.objects.all():
    print(f"  {a.name}: {a.stock_quantity} {a.unit}")
    
print("\nAccessories <= 10:", Accessory.objects.filter(stock_quantity__lte=10).count())
print("Accessories <= 50:", Accessory.objects.filter(stock_quantity__lte=50).count())
