from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, Customer, Fabric, Accessory, 
    GarmentType, GarmentTypeAccessory, Order, 
    OrderAccessory, TailoringTask, Payment, 
    InventoryLog, SMSLog
)


# Inline for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


# Extend User Admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_active')
    
    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_role_display()
        return '-'
    get_role.short_description = 'Role'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number', 'email', 'created_at')
    search_fields = ('name', 'contact_number', 'email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Fabric)
class FabricAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'stock_meters', 'price_per_meter', 'updated_at')
    search_fields = ('name', 'color')
    list_filter = ('color',)
    ordering = ('name',)


@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'stock_quantity', 'price_per_unit', 'updated_at')
    search_fields = ('name',)
    list_filter = ('unit',)
    ordering = ('name',)


class GarmentTypeAccessoryInline(admin.TabularInline):
    model = GarmentTypeAccessory
    extra = 1


@admin.register(GarmentType)
class GarmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'garment_category', 'estimated_fabric_meters', 'base_price', 'default_tailor')
    search_fields = ('name',)
    list_filter = ('garment_category',)
    inlines = [GarmentTypeAccessoryInline]


@admin.register(GarmentTypeAccessory)
class GarmentTypeAccessoryAdmin(admin.ModelAdmin):
    list_display = ('garment_type', 'accessory', 'quantity_required')
    list_filter = ('garment_type', 'accessory')


class OrderAccessoryInline(admin.TabularInline):
    model = OrderAccessory
    extra = 0
    readonly_fields = ('accessory', 'quantity_used')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_number', 'payment_date')


class TailoringTaskInline(admin.StackedInline):
    model = TailoringTask
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'garment_type', 'status', 'total_price', 'payment_status', 'order_date')
    list_filter = ('status', 'garment_type', 'order_date')
    search_fields = ('order_number', 'customer__name')
    readonly_fields = ('order_number', 'order_date', 'created_at', 'updated_at')
    inlines = [OrderAccessoryInline, PaymentInline, TailoringTaskInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'garment_type', 'fabric', 'quantity', 'fabric_meters_used')
        }),
        ('Measurements & Instructions', {
            'fields': ('measurements', 'special_instructions'),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('total_price', 'deposit_amount', 'balance_amount')
        }),
        ('Status & Dates', {
            'fields': ('status', 'due_date', 'completed_date', 'order_date', 'created_by')
        }),
    )


@admin.register(OrderAccessory)
class OrderAccessoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'accessory', 'quantity_used')
    list_filter = ('accessory',)


@admin.register(TailoringTask)
class TailoringTaskAdmin(admin.ModelAdmin):
    list_display = ('order', 'tailor', 'status', 'assigned_date', 'completed_date', 'approved_date')
    list_filter = ('status', 'tailor')
    search_fields = ('order__order_number', 'tailor__username')
    readonly_fields = ('assigned_date', 'started_date', 'completed_date', 'approved_date')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_number', 'order', 'amount', 'payment_type', 'status', 'payment_date')
    list_filter = ('payment_type', 'status', 'payment_date')
    search_fields = ('payment_number', 'order__order_number')
    readonly_fields = ('payment_number', 'payment_date', 'created_at')


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('item_type', 'get_item_name', 'action', 'quantity', 'previous_stock', 'new_stock', 'created_by', 'created_at')
    list_filter = ('item_type', 'action', 'created_at')
    search_fields = ('fabric__name', 'accessory__name', 'order__order_number')
    readonly_fields = ('created_at',)
    
    def get_item_name(self, obj):
        if obj.fabric:
            return obj.fabric.name
        elif obj.accessory:
            return obj.accessory.name
        return '-'
    get_item_name.short_description = 'Item'


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order', 'phone_number', 'status', 'sent_at', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__name', 'phone_number', 'order__order_number')
    readonly_fields = ('created_at', 'sent_at')


# Customize admin site header
admin.site.site_header = 'El Senior Original Tailoring Admin'
admin.site.site_title = 'El Senior Original Tailoring'
admin.site.index_title = 'Administration'
