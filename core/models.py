from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class UserProfile(models.Model):
    """Extended user profile with role"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('tailor', 'Tailor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tailor')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_tailor(self):
        return self.role == 'tailor'


class Customer(models.Model):
    """Customer model for storing customer information"""
    name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.contact_number}"


class Fabric(models.Model):
    """Fabric inventory"""
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=100, blank=True)
    stock_meters = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    price_per_meter = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.color}) - {self.stock_meters}m"
    
    def has_sufficient_stock(self, required_meters):
        return self.stock_meters >= Decimal(str(required_meters))
    
    def deduct_stock(self, meters):
        if self.has_sufficient_stock(meters):
            self.stock_meters -= Decimal(str(meters))
            self.save()
            return True
        return False


class Accessory(models.Model):
    """Accessories inventory (buttons, zippers, threads, etc.)"""
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('meters', 'Meters'),
        ('yards', 'Yards'),
        ('rolls', 'Rolls'),
        ('packs', 'Packs'),
    ]
    
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pcs')
    stock_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    price_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Accessories"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.stock_quantity} {self.unit}"
    
    def has_sufficient_stock(self, required_quantity):
        return self.stock_quantity >= Decimal(str(required_quantity))
    
    def deduct_stock(self, quantity):
        if self.has_sufficient_stock(quantity):
            self.stock_quantity -= Decimal(str(quantity))
            self.save()
            return True
        return False


class GarmentType(models.Model):
    """Types of garments with fabric and accessory requirements"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    garment_category = models.CharField(
        max_length=20,
        choices=[
            ('upper', 'Upper Body'),
            ('lower', 'Lower Body'),
            ('both', 'Upper & Lower (Both)'),
        ],
        default='upper',
        help_text="Category of garment for measurement purposes"
    )
    estimated_fabric_meters = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Estimated fabric meters required per garment"
    )
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Base tailoring price"
    )
    default_tailor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='specialized_garments',
        help_text="Default tailor for this garment type"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_required_measurements(self):
        """Get list of required measurements based on garment category"""
        upper_measurements = [
            'chest', 'shoulder', 'sleeve_length', 'arm_hole', 'cuff', 'neck'
        ]
        lower_measurements = [
            'waist', 'hips', 'thigh', 'knee', 'hem', 'inseam', 'outseam', 'rise'
        ]
        
        if self.garment_category == 'upper':
            return upper_measurements
        elif self.garment_category == 'lower':
            return lower_measurements
        elif self.garment_category == 'both':
            return upper_measurements + lower_measurements
        return []


class GarmentTypeAccessory(models.Model):
    """Required accessories for each garment type"""
    garment_type = models.ForeignKey(
        GarmentType, 
        on_delete=models.CASCADE, 
        related_name='required_accessories'
    )
    accessory = models.ForeignKey(
        Accessory, 
        on_delete=models.CASCADE
    )
    quantity_required = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=1
    )
    
    class Meta:
        unique_together = ['garment_type', 'accessory']
        verbose_name_plural = "Garment Type Accessories"
    
    def __str__(self):
        return f"{self.garment_type.name} - {self.accessory.name} x {self.quantity_required}"


class Order(models.Model):
    """Main order model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delivered', 'Delivered'),
        ('for_adjustment', 'For Adjustment/Rework'),
        ('ready_for_reclaim', 'Ready for Re-Claim'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.PROTECT, 
        related_name='orders'
    )
    garment_type = models.ForeignKey(
        GarmentType, 
        on_delete=models.PROTECT
    )
    fabric = models.ForeignKey(
        Fabric, 
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(default=1)
    fabric_meters_used = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )
    
    # Measurements stored as JSON
    measurements = models.JSONField(default=dict, blank=True)
    special_instructions = models.TextField(blank=True)
    
    # Pricing
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Dates
    order_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def payment_status(self):
        total_paid = sum(p.amount for p in self.payments.filter(status='completed'))
        if total_paid >= self.total_price:
            return 'fully_paid'
        elif total_paid > 0:
            return 'partial'
        return 'unpaid'
    
    @property
    def total_paid(self):
        return sum(p.amount for p in self.payments.filter(status='completed'))
    
    @property
    def remaining_balance(self):
        return self.total_price - self.total_paid


class OrderAccessory(models.Model):
    """Accessories used in an order"""
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='order_accessories'
    )
    accessory = models.ForeignKey(
        Accessory, 
        on_delete=models.PROTECT
    )
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['order', 'accessory']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.accessory.name}"


class TailoringTask(models.Model):
    """Task assigned to tailors"""
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
    ]
    
    order = models.OneToOneField(
        Order, 
        on_delete=models.CASCADE, 
        related_name='tailoring_task'
    )
    tailor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='assigned_tasks'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    notes = models.TextField(blank=True)
    
    # Commission fields
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00'),
        help_text="Commission percentage for this task"
    )
    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Calculated commission amount"
    )
    commission_paid = models.BooleanField(
        default=False,
        help_text="Whether commission has been credited to tailor"
    )
    commission_paid_date = models.DateTimeField(null=True, blank=True)
    
    assigned_date = models.DateTimeField(auto_now_add=True)
    started_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_tasks'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Task for {self.order.order_number} - {self.tailor}"
    
    def calculate_commission(self):
        """Calculate commission based on order total price and commission rate"""
        if self.order and self.order.total_price:
            self.commission_amount = (self.order.total_price * self.commission_rate) / Decimal('100')
        return self.commission_amount
    
    def save(self, *args, **kwargs):
        # Auto-calculate commission if not set
        if self.commission_amount == Decimal('0.00') and self.order_id:
            self.calculate_commission()
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment records for orders"""
    PAYMENT_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('balance', 'Balance Payment'),
        ('full', 'Full Payment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    payment_number = models.CharField(max_length=50, unique=True, editable=False)
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    payment_method = models.CharField(max_length=20, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    
    notes = models.TextField(blank=True)
    received_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='received_payments'
    )
    
    payment_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.payment_number} - {self.order.order_number} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class TailorCommission(models.Model):
    """Track individual commission records for tailors"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('credited', 'Credited'),
        ('paid', 'Paid Out'),
    ]
    
    commission_number = models.CharField(max_length=50, unique=True, editable=False)
    tailor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='commissions'
    )
    task = models.OneToOneField(
        'TailoringTask',
        on_delete=models.CASCADE,
        related_name='commission_record'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='commission_records'
    )
    
    # Commission details
    order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Original order amount"
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Commission percentage applied"
    )
    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Commission amount earned"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Garment details for reporting
    garment_type = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    customer_name = models.CharField(max_length=200)
    
    # Timestamps
    earned_date = models.DateTimeField(auto_now_add=True)
    credited_date = models.DateTimeField(null=True, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-earned_date']
        verbose_name = "Tailor Commission"
        verbose_name_plural = "Tailor Commissions"
        indexes = [
            models.Index(fields=['tailor', 'status']),
            models.Index(fields=['tailor', '-earned_date']),
        ]
    
    def __str__(self):
        return f"{self.commission_number} - {self.tailor.get_full_name() or self.tailor.username} - ₱{self.commission_amount}"
    
    def save(self, *args, **kwargs):
        if not self.commission_number:
            self.commission_number = f"COM-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @classmethod
    def create_from_task(cls, task):
        """Create a commission record from a completed task when order is claimed"""
        from django.utils import timezone
        
        if not task.tailor or not task.order:
            return None
        
        # Check if commission already exists
        if hasattr(task, 'commission_record'):
            return task.commission_record
        
        commission = cls.objects.create(
            tailor=task.tailor,
            task=task,
            order=task.order,
            order_amount=task.order.total_price,
            commission_rate=task.commission_rate,
            commission_amount=task.commission_amount,
            status='credited',
            garment_type=task.order.garment_type.name,
            quantity=task.order.quantity,
            customer_name=task.order.customer.name,
            credited_date=timezone.now()
        )
        
        # Update task commission status
        task.commission_paid = True
        task.commission_paid_date = timezone.now()
        task.save(update_fields=['commission_paid', 'commission_paid_date'])
        
        return commission
    
    @classmethod
    def get_tailor_summary(cls, tailor, start_date=None, end_date=None):
        """Get commission summary for a tailor within date range"""
        from django.db.models import Sum, Count
        
        queryset = cls.objects.filter(tailor=tailor)
        
        if start_date:
            queryset = queryset.filter(earned_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(earned_date__date__lte=end_date)
        
        summary = queryset.aggregate(
            total_commissions=Sum('commission_amount'),
            total_tasks=Count('id'),
            total_orders_value=Sum('order_amount')
        )
        
        return {
            'total_commissions': summary['total_commissions'] or Decimal('0'),
            'total_tasks': summary['total_tasks'] or 0,
            'total_orders_value': summary['total_orders_value'] or Decimal('0'),
        }


class InventoryLog(models.Model):
    """Log for inventory changes"""
    ACTION_CHOICES = [
        ('add', 'Stock Added'),
        ('deduct', 'Stock Deducted'),
        ('adjust', 'Stock Adjusted'),
    ]
    
    ITEM_TYPE_CHOICES = [
        ('fabric', 'Fabric'),
        ('accessory', 'Accessory'),
    ]
    
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    fabric = models.ForeignKey(
        Fabric, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    accessory = models.ForeignKey(
        Accessory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    previous_stock = models.DecimalField(max_digits=10, decimal_places=2)
    new_stock = models.DecimalField(max_digits=10, decimal_places=2)
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Related order if deduction was for an order"
    )
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Inventory Logs"
    
    def __str__(self):
        item = self.fabric or self.accessory
        return f"{self.action} - {item} - {self.quantity}"


class SMSLog(models.Model):
    """Log for SMS notifications sent"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.SET_NULL, 
        null=True
    )
    order = models.ForeignKey(
        Order, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "SMS Log"
        verbose_name_plural = "SMS Logs"
    
    def __str__(self):
        return f"SMS to {self.phone_number} - {self.status}"


class Rework(models.Model):
    """Rework requests for claimed garments that need adjustments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    REASON_CHOICES = [
        ('fitting_issue', 'Fitting Issue'),
        ('design_change', 'Design Change'),
        ('workmanship_concern', 'Workmanship Concern'),
        ('material_issue', 'Material Issue'),
        ('other', 'Other'),
    ]
    
    CHARGE_TYPE_CHOICES = [
        ('free', 'Free (Shop Error)'),
        ('paid', 'Paid (Customer Requested)'),
    ]
    
    rework_number = models.CharField(max_length=50, unique=True, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='reworks'
    )
    original_garment_type = models.CharField(max_length=200)
    original_customer_name = models.CharField(max_length=200)
    
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    reason_description = models.TextField()
    charge_type = models.CharField(max_length=20, choices=CHARGE_TYPE_CHOICES, default='free')
    additional_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Additional cost for paid reworks"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Materials tracking
    fabric_used = models.ForeignKey(
        Fabric,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rework_fabric_used'
    )
    fabric_meters_used = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    notes = models.TextField(blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_reworks'
    )
    
    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    started_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reworks'
    )
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = "Rework"
        verbose_name_plural = "Reworks"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"{self.rework_number} - {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.rework_number:
            self.rework_number = f"RWK-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @classmethod
    def create_from_delivered_order(cls, order, reason, reason_description, charge_type='free',
                                   additional_cost=Decimal('0.00'), created_by=None):
        """Create a rework request from a delivered order"""
        rework = cls.objects.create(
            order=order,
            original_garment_type=order.garment_type.name,
            original_customer_name=order.customer.name,
            reason=reason,
            reason_description=reason_description,
            charge_type=charge_type,
            additional_cost=additional_cost,
            created_by=created_by
        )
        
        # Update order status to for_adjustment
        order.status = 'for_adjustment'
        order.save()
        
        return rework


class ReworkMaterial(models.Model):
    """Materials used for rework (accessories beyond fabric)"""
    rework = models.ForeignKey(
        Rework,
        on_delete=models.CASCADE,
        related_name='materials'
    )
    accessory = models.ForeignKey(
        Accessory,
        on_delete=models.CASCADE
    )
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Rework Material"
        verbose_name_plural = "Rework Materials"
    
    def __str__(self):
        return f"{self.rework.rework_number} - {self.accessory.name}"


class Notification(models.Model):
    """In-app notification system for tailors and admins"""
    TYPE_CHOICES = [
        ('task_assigned', 'Task Assigned'),
        ('task_started', 'Task Started'),
        ('task_completed', 'Task Completed'),
        ('task_approved', 'Order Completed'),
        ('order_created', 'Order Created'),
        ('payment_received', 'Payment Received'),
        ('low_stock', 'Low Stock Alert'),
        ('rework_assigned', 'Rework Assigned'),
        ('rework_completed', 'Rework Completed'),
        ('general', 'General'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )
    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default='general'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    
    # Related objects (optional)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    task = models.ForeignKey(
        'TailoringTask',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # URL for action (e.g., link to task or order)
    action_url = models.CharField(max_length=500, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @classmethod
    def get_unread_count(cls, user):
        """Get count of unread notifications for a user"""
        return cls.objects.filter(recipient=user, is_read=False).count()
    
    @classmethod
    def get_recent_notifications(cls, user, limit=10):
        """Get recent notifications for a user"""
        return cls.objects.filter(recipient=user).select_related(
            'sender', 'order', 'task'
        )[:limit]
    
    @classmethod
    def create_notification(cls, recipient, title, message, notification_type='general',
                           sender=None, order=None, task=None, action_url='', priority='normal'):
        """Helper method to create a notification"""
        return cls.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            order=order,
            task=task,
            action_url=action_url
        )
    
    @classmethod
    def notify_tailors_task_assigned(cls, task, sender=None):
        """Notify tailor when a new task is assigned"""
        if task.tailor:
            return cls.create_notification(
                recipient=task.tailor,
                title='New Task Assigned',
                message=f'You have been assigned a new task for order {task.order.order_number}. '
                       f'Customer: {task.order.customer.name}. '
                       f'Garment: {task.order.garment_type.name}.',
                notification_type='task_assigned',
                sender=sender,
                order=task.order,
                task=task,
                action_url=f'/tasks/{task.pk}/',
                priority='high'
            )
        return None
    
    @classmethod
    def notify_admins_task_completed(cls, task, sender=None):
        """Notify all admins when a task is marked as completed"""
        from .models import UserProfile
        notifications = []
        admin_profiles = UserProfile.objects.filter(role='admin').select_related('user')
        
        for profile in admin_profiles:
            notification = cls.create_notification(
                recipient=profile.user,
                title='Task Completed - Ready for Order Completion',
                message=f'Task for order {task.order.order_number} has been marked as completed by '
                       f'{task.tailor.get_full_name() or task.tailor.username}. '
                       f'Customer: {task.order.customer.name}. '
                       f'Garment: {task.order.garment_type.name}. '
                       f'Please complete the order.',
                notification_type='task_completed',
                sender=sender,
                order=task.order,
                task=task,
                action_url=f'/tasks/{task.pk}/',
                priority='high'
            )
            notifications.append(notification)
        
        return notifications
    
    @classmethod
    def notify_tailor_task_approved(cls, task, sender=None):
        """Notify tailor when their task is approved"""
        if task.tailor:
            return cls.create_notification(
                recipient=task.tailor,
                title='Order Completed',
                message=f'Your task for order {task.order.order_number} has been approved. '
                       f'The order is now complete.',
                notification_type='task_approved',
                sender=sender,
                order=task.order,
                task=task,
                action_url=f'/tasks/{task.pk}/',
                priority='normal'
            )
        return None
    
    @classmethod
    def notify_admins_task_started(cls, task, sender=None):
        """Notify all admins when a task is started by tailor"""
        from .models import UserProfile
        notifications = []
        admin_profiles = UserProfile.objects.filter(role='admin').select_related('user')
        
        # Only notify if there are admins and a sender is specified
        if admin_profiles.exists() and sender:
            for profile in admin_profiles:
                notification = cls.create_notification(
                    recipient=profile.user,
                    title='Task Started',
                    message=f'Task for order {task.order.order_number} has been started by '
                           f'{task.tailor.get_full_name() or task.tailor.username}.',
                    notification_type='task_started',
                    sender=sender,
                    order=task.order,
                    task=task,
                    action_url=f'/tasks/{task.pk}/',
                    priority='normal'
                )
                notifications.append(notification)
        
        return notifications
