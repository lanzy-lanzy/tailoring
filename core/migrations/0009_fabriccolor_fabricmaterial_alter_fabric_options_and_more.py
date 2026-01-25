# Generated migration to restructure fabric model with FK relationships

import django.db.models.deletion
from django.db import migrations, models


def create_fabric_materials_and_colors(apps, schema_editor):
    """Migrate existing fabric data into FabricMaterial and FabricColor tables"""
    from django.db import connection
    
    FabricMaterial = apps.get_model('core', 'FabricMaterial')
    FabricColor = apps.get_model('core', 'FabricColor')
    Fabric = apps.get_model('core', 'Fabric')
    
    # Get unique materials from old column (the old 'color' column was actually material)
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT color FROM core_fabric WHERE color IS NOT NULL")
        materials = [row[0] for row in cursor.fetchall()]
    
    # Create material records
    materials_map = {}
    for mat_name in materials:
        fm, _ = FabricMaterial.objects.get_or_create(name=mat_name)
        materials_map[mat_name] = fm.id
    
    # Get unique colors from old column (the old 'name' column was color)
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT name FROM core_fabric WHERE name IS NOT NULL")
        colors = [row[0] for row in cursor.fetchall()]
    
    # Create color records
    colors_map = {}
    for color_name in colors:
        fc, _ = FabricColor.objects.get_or_create(name=color_name)
        colors_map[color_name] = fc.id
    
    # Update Fabric records with FK IDs
    with connection.cursor() as cursor:
        for fabric_id, mat_name, color_name in cursor.execute(
            "SELECT id, color, name FROM core_fabric"
        ).fetchall():
            mat_id = materials_map.get(mat_name)
            color_id = colors_map.get(color_name)
            cursor.execute(
                "UPDATE core_fabric SET material_id = %s, color_id = %s WHERE id = %s",
                [mat_id, color_id, fabric_id]
            )


def reverse_migration(apps, schema_editor):
    """Reverse the data migration"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_alter_order_status_and_more"),
    ]

    operations = [
        # Create new models
        migrations.CreateModel(
            name='FabricColor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='FabricMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        # Add new FK fields as nullable
        migrations.AddField(
            model_name='fabric',
            name='color_id',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='fabric',
            name='material_id',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        # Migrate the data
        migrations.RunPython(create_fabric_materials_and_colors, reverse_migration),
        # Remove old columns
        migrations.RemoveField(
            model_name='fabric',
            name='color',
        ),
        migrations.RemoveField(
            model_name='fabric',
            name='name',
        ),
        # Convert integer fields to FK fields
        migrations.AlterField(
            model_name='fabric',
            name='color_id',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='fabrics',
                to='core.fabriccolor',
                db_column='color_id'
            ),
        ),
        migrations.AlterField(
            model_name='fabric',
            name='material_id',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='fabrics',
                to='core.fabricmaterial',
                db_column='material_id'
            ),
        ),
        # Rename the fields to match model definition
        migrations.RenameField(
            model_name='fabric',
            old_name='color_id',
            new_name='color',
        ),
        migrations.RenameField(
            model_name='fabric',
            old_name='material_id',
            new_name='material',
        ),
        # Update meta options
        migrations.AlterModelOptions(
            name='fabric',
            options={'ordering': ['material__name', 'color__name']},
        ),
    ]
