from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from decimal import Decimal
import json
import requests

from .models import (
    UserProfile, Customer, Fabric, Accessory, 
    GarmentType, GarmentTypeAccessory, Order, 
    OrderAccessory, TailoringTask, Payment, 
    InventoryLog, SMSLog, Notification, TailorCommission
)
from .forms import (
    LoginForm, UserRegistrationForm, CustomerForm, 
    FabricForm, AccessoryForm, GarmentTypeForm,
    GarmentTypeAccessoryForm, OrderForm, 
    TailoringTaskUpdateForm, PaymentForm, StockAddForm
)
from django.conf import settings


# ============== Decorators ==============

def admin_required(view_func):
    """Decorator to require admin role"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
            messages.error(request, 'Admin access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def tailor_required(view_func):
    """Decorator to require tailor role"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or not request.user.profile.is_tailor:
            messages.error(request, 'Tailor access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ============== Landing Page ==============

def home_view(request):
    """Landing page view"""
    return render(request, 'home.html')


# ============== Authentication ==============

def register_view(request):
    """Registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Default to tailor if not specified (though form has role field)
            role = form.cleaned_data.get('role', 'tailor')
            UserProfile.objects.create(
                user=user,
                role=role,
                phone=form.cleaned_data.get('phone', '')
            )
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """Login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


# ============== Dashboard ==============

@login_required
def dashboard(request):
    """Main dashboard - redirects based on role"""
    if hasattr(request.user, 'profile'):
        if request.user.profile.is_admin:
            return admin_dashboard(request)
        else:
            return tailor_dashboard(request)
    return render(request, 'dashboard/main.html')


@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard with overview stats"""
    today = timezone.now().date()
    
    # Statistics
    stats = {
        'total_customers': Customer.objects.count(),
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'in_progress_orders': Order.objects.filter(status='in_progress').count(),
        'completed_orders': Order.objects.filter(status='completed').count(),
        'today_orders': Order.objects.filter(order_date__date=today).count(),
        'pending_tasks': TailoringTask.objects.filter(status__in=['assigned', 'in_progress']).count(),
        'awaiting_approval': TailoringTask.objects.filter(status='completed').count(),
    }
    
    # Revenue stats
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    today_revenue = Payment.objects.filter(
        status='completed',
        payment_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    stats['total_revenue'] = total_revenue
    stats['today_revenue'] = today_revenue
    
    # Recent orders
    recent_orders = Order.objects.select_related(
        'customer', 'garment_type', 'fabric'
    ).order_by('-created_at')[:10]
    
    # Low stock alerts
    low_stock_fabrics = Fabric.objects.filter(stock_meters__lt=5)
    low_stock_accessories = Accessory.objects.filter(stock_quantity__lt=10)
    
    # Tasks awaiting approval
    pending_approvals = TailoringTask.objects.filter(
        status='completed'
    ).select_related('order', 'order__customer', 'tailor')[:5]
    
    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'low_stock_fabrics': low_stock_fabrics,
        'low_stock_accessories': low_stock_accessories,
        'pending_approvals': pending_approvals,
    }
    
    return render(request, 'dashboard/admin.html', context)


@login_required
@tailor_required
def tailor_dashboard(request):
    """Tailor dashboard with assigned tasks"""
    tasks = TailoringTask.objects.filter(
        tailor=request.user
    ).exclude(
        status='approved'
    ).select_related(
        'order', 'order__customer', 'order__garment_type', 'order__fabric'
    ).order_by('-created_at')
    
    completed_tasks = TailoringTask.objects.filter(
        tailor=request.user,
        status='approved'
    ).count()
    
    context = {
        'tasks': tasks,
        'completed_tasks': completed_tasks,
        'pending_count': tasks.filter(status='assigned').count(),
        'in_progress_count': tasks.filter(status='in_progress').count(),
    }
    
    return render(request, 'dashboard/tailor.html', context)


# ============== Customer Management ==============

@login_required
@admin_required
def customer_list(request):
    """List all customers"""
    search = request.GET.get('search', '')
    customers = Customer.objects.all()
    
    if search:
        customers = customers.filter(
            Q(name__icontains=search) | 
            Q(contact_number__icontains=search)
        )
    
    paginator = Paginator(customers, 20)
    page = request.GET.get('page', 1)
    customers = paginator.get_page(page)
    
    if request.headers.get('HX-Request'):
        return render(request, 'customers/partials/customer_table.html', {'customers': customers})
    
    return render(request, 'customers/list.html', {'customers': customers, 'search': search})


@login_required
@admin_required
def customer_create(request):
    """Create new customer"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.name}" created successfully.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    status=204,
                    headers={'HX-Trigger': 'customerCreated', 'HX-Redirect': '/customers/'}
                )
            return redirect('customer_list')
    else:
        form = CustomerForm()
    
    template = 'customers/partials/customer_form.html' if request.headers.get('HX-Request') else 'customers/create.html'
    return render(request, template, {'form': form, 'customer': None})


@login_required
@admin_required
def customer_edit(request, pk):
    """Edit customer"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Customer "{customer.name}" updated successfully.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    status=204,
                    headers={'HX-Trigger': 'customerUpdated', 'HX-Redirect': '/customers/'}
                )
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    
    template = 'customers/partials/customer_form.html' if request.headers.get('HX-Request') else 'customers/edit.html'
    return render(request, template, {'form': form, 'customer': customer})


@login_required
@admin_required
def customer_detail(request, pk):
    """Customer detail view"""
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.orders.all().order_by('-created_at')[:10]
    
    return render(request, 'customers/detail.html', {
        'customer': customer,
        'orders': orders
    })


@login_required
@admin_required  
def customer_delete(request, pk):
    """Delete customer"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        if customer.orders.exists():
            messages.error(request, 'Cannot delete customer with existing orders.')
        else:
            customer.delete()
            messages.success(request, 'Customer deleted successfully.')
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Redirect': '/customers/'})
        return redirect('customer_list')
    
    return render(request, 'customers/delete_confirm.html', {'customer': customer})


# ============== Inventory Management ==============

@login_required
@admin_required
def inventory_dashboard(request):
    """Inventory overview"""
    fabrics = Fabric.objects.all()
    accessories = Accessory.objects.all()
    
    # Recent inventory logs
    recent_logs = InventoryLog.objects.select_related(
        'fabric', 'accessory', 'order', 'created_by'
    ).order_by('-created_at')[:20]
    
    context = {
        'fabrics': fabrics,
        'accessories': accessories,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'inventory/dashboard.html', context)


# Fabric CRUD
@login_required
@admin_required
def fabric_list(request):
    """List all fabrics"""
    fabrics = Fabric.objects.all()
    return render(request, 'inventory/fabric_list.html', {'fabrics': fabrics})


@login_required
@admin_required
def fabric_create(request):
    """Create new fabric"""
    if request.method == 'POST':
        form = FabricForm(request.POST)
        if form.is_valid():
            fabric = form.save()
            
            # Log the addition
            InventoryLog.objects.create(
                item_type='fabric',
                fabric=fabric,
                action='add',
                quantity=fabric.stock_meters,
                previous_stock=0,
                new_stock=fabric.stock_meters,
                notes='Initial stock',
                created_by=request.user
            )
            
            messages.success(request, f'Fabric "{fabric.name}" created successfully.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Redirect': '/inventory/'})
            return redirect('inventory_dashboard')
    else:
        form = FabricForm()
    
    template = 'inventory/partials/fabric_form.html' if request.headers.get('HX-Request') else 'inventory/fabric_create.html'
    return render(request, template, {'form': form})


@login_required
@admin_required
def fabric_edit(request, pk):
    """Edit fabric"""
    fabric = get_object_or_404(Fabric, pk=pk)
    
    if request.method == 'POST':
        old_stock = fabric.stock_meters
        form = FabricForm(request.POST, instance=fabric)
        if form.is_valid():
            fabric = form.save()
            
            # Log if stock changed
            if old_stock != fabric.stock_meters:
                InventoryLog.objects.create(
                    item_type='fabric',
                    fabric=fabric,
                    action='adjust',
                    quantity=abs(fabric.stock_meters - old_stock),
                    previous_stock=old_stock,
                    new_stock=fabric.stock_meters,
                    notes='Manual adjustment',
                    created_by=request.user
                )
            
            messages.success(request, f'Fabric "{fabric.name}" updated successfully.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Redirect': '/inventory/'})
            return redirect('inventory_dashboard')
    else:
        form = FabricForm(instance=fabric)
    
    template = 'inventory/partials/fabric_form.html' if request.headers.get('HX-Request') else 'inventory/fabric_edit.html'
    return render(request, template, {'form': form, 'fabric': fabric})


@login_required
@admin_required
def fabric_add_stock(request, pk):
    """Add stock to fabric"""
    fabric = get_object_or_404(Fabric, pk=pk)
    
    if request.method == 'POST':
        form = StockAddForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']
            
            old_stock = fabric.stock_meters
            fabric.stock_meters += quantity
            fabric.save()
            
            InventoryLog.objects.create(
                item_type='fabric',
                fabric=fabric,
                action='add',
                quantity=quantity,
                previous_stock=old_stock,
                new_stock=fabric.stock_meters,
                notes=notes,
                created_by=request.user
            )
            
            messages.success(request, f'Added {quantity}m to {fabric.name}.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Trigger': 'stockUpdated'})
            return redirect('inventory_dashboard')
    else:
        form = StockAddForm()
    
    return render(request, 'inventory/partials/add_stock_form.html', {
        'form': form,
        'item': fabric,
        'item_type': 'fabric'
    })


@login_required
@admin_required
def fabric_delete(request, pk):
    """Delete fabric"""
    fabric = get_object_or_404(Fabric, pk=pk)
    
    if request.method == 'POST':
        fabric.delete()
        messages.success(request, 'Fabric deleted successfully.')
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Redirect': '/inventory/'})
        return redirect('inventory_dashboard')
    
    return render(request, 'inventory/delete_confirm.html', {'item': fabric, 'item_type': 'Fabric'})


# Accessory CRUD
@login_required
@admin_required
def accessory_list(request):
    """List all accessories"""
    accessories = Accessory.objects.all()
    return render(request, 'inventory/accessory_list.html', {'accessories': accessories})


@login_required
@admin_required
def accessory_create(request):
    """Create new accessory"""
    if request.method == 'POST':
        form = AccessoryForm(request.POST)
        if form.is_valid():
            accessory = form.save()
            
            InventoryLog.objects.create(
                item_type='accessory',
                accessory=accessory,
                action='add',
                quantity=accessory.stock_quantity,
                previous_stock=0,
                new_stock=accessory.stock_quantity,
                notes='Initial stock',
                created_by=request.user
            )
            
            messages.success(request, f'Accessory "{accessory.name}" created successfully.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Redirect': '/inventory/'})
            return redirect('inventory_dashboard')
    else:
        form = AccessoryForm()
    
    template = 'inventory/partials/accessory_form.html' if request.headers.get('HX-Request') else 'inventory/accessory_create.html'
    return render(request, template, {'form': form})


@login_required
@admin_required
def accessory_edit(request, pk):
    """Edit accessory"""
    accessory = get_object_or_404(Accessory, pk=pk)
    
    if request.method == 'POST':
        old_stock = accessory.stock_quantity
        form = AccessoryForm(request.POST, instance=accessory)
        if form.is_valid():
            accessory = form.save()
            
            if old_stock != accessory.stock_quantity:
                InventoryLog.objects.create(
                    item_type='accessory',
                    accessory=accessory,
                    action='adjust',
                    quantity=abs(accessory.stock_quantity - old_stock),
                    previous_stock=old_stock,
                    new_stock=accessory.stock_quantity,
                    notes='Manual adjustment',
                    created_by=request.user
                )
            
            messages.success(request, f'Accessory "{accessory.name}" updated successfully.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Redirect': '/inventory/'})
            return redirect('inventory_dashboard')
    else:
        form = AccessoryForm(instance=accessory)
    
    template = 'inventory/partials/accessory_form.html' if request.headers.get('HX-Request') else 'inventory/accessory_edit.html'
    return render(request, template, {'form': form, 'accessory': accessory})


@login_required
@admin_required
def accessory_add_stock(request, pk):
    """Add stock to accessory"""
    accessory = get_object_or_404(Accessory, pk=pk)
    
    if request.method == 'POST':
        form = StockAddForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']
            
            old_stock = accessory.stock_quantity
            accessory.stock_quantity += quantity
            accessory.save()
            
            InventoryLog.objects.create(
                item_type='accessory',
                accessory=accessory,
                action='add',
                quantity=quantity,
                previous_stock=old_stock,
                new_stock=accessory.stock_quantity,
                notes=notes,
                created_by=request.user
            )
            
            messages.success(request, f'Added {quantity} to {accessory.name}.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Trigger': 'stockUpdated'})
            return redirect('inventory_dashboard')
    else:
        form = StockAddForm()
    
    return render(request, 'inventory/partials/add_stock_form.html', {
        'form': form,
        'item': accessory,
        'item_type': 'accessory'
    })


@login_required
@admin_required
def accessory_delete(request, pk):
    """Delete accessory"""
    accessory = get_object_or_404(Accessory, pk=pk)
    
    if request.method == 'POST':
        accessory.delete()
        messages.success(request, 'Accessory deleted successfully.')
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Redirect': '/inventory/'})
        return redirect('inventory_dashboard')
    
    return render(request, 'inventory/delete_confirm.html', {'item': accessory, 'item_type': 'Accessory'})


@login_required
@admin_required
def inventory_logs(request):
    """View inventory logs"""
    logs = InventoryLog.objects.select_related(
        'fabric', 'accessory', 'order', 'created_by'
    ).order_by('-created_at')
    
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    logs = paginator.get_page(page)
    
    return render(request, 'inventory/logs.html', {'logs': logs})


# ============== Garment Type Management ==============

@login_required
@admin_required
def garment_type_list(request):
    """List all garment types"""
    garment_types = GarmentType.objects.prefetch_related('required_accessories__accessory').all()
    return render(request, 'garments/list.html', {'garment_types': garment_types})


@login_required
@admin_required
def garment_type_create(request):
    """Create new garment type"""
    if request.method == 'POST':
        form = GarmentTypeForm(request.POST)
        if form.is_valid():
            garment_type = form.save()
            messages.success(request, f'Garment type "{garment_type.name}" created successfully.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Redirect': '/garments/'})
            return redirect('garment_type_list')
    else:
        form = GarmentTypeForm()
    
    template = 'garments/partials/garment_form.html' if request.headers.get('HX-Request') else 'garments/create.html'
    return render(request, template, {'form': form})


@login_required
@admin_required
def garment_type_edit(request, pk):
    """Edit garment type"""
    garment_type = get_object_or_404(GarmentType, pk=pk)
    
    if request.method == 'POST':
        form = GarmentTypeForm(request.POST, instance=garment_type)
        if form.is_valid():
            form.save()
            messages.success(request, f'Garment type "{garment_type.name}" updated successfully.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Redirect': '/garments/'})
            return redirect('garment_type_list')
    else:
        form = GarmentTypeForm(instance=garment_type)
    
    template = 'garments/partials/garment_form.html' if request.headers.get('HX-Request') else 'garments/edit.html'
    return render(request, template, {'form': form, 'garment_type': garment_type})


@login_required
@admin_required
def garment_type_detail(request, pk):
    """Garment type detail with accessories"""
    garment_type = get_object_or_404(GarmentType, pk=pk)
    required_accessories = garment_type.required_accessories.select_related('accessory').all()
    
    return render(request, 'garments/detail.html', {
        'garment_type': garment_type,
        'required_accessories': required_accessories
    })


@login_required
@admin_required
def garment_type_add_accessory(request, pk):
    """Add accessory requirement to garment type"""
    garment_type = get_object_or_404(GarmentType, pk=pk)
    
    if request.method == 'POST':
        form = GarmentTypeAccessoryForm(request.POST)
        if form.is_valid():
            gta = form.save(commit=False)
            gta.garment_type = garment_type
            gta.save()
            messages.success(request, 'Accessory requirement added.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Trigger': 'accessoryAdded'})
            return redirect('garment_type_detail', pk=pk)
    else:
        form = GarmentTypeAccessoryForm()
    
    return render(request, 'garments/partials/add_accessory_form.html', {
        'form': form,
        'garment_type': garment_type
    })


@login_required
@admin_required
def garment_type_remove_accessory(request, pk, accessory_pk):
    """Remove accessory requirement from garment type"""
    gta = get_object_or_404(GarmentTypeAccessory, garment_type_id=pk, accessory_id=accessory_pk)
    gta.delete()
    messages.success(request, 'Accessory requirement removed.')
    
    if request.headers.get('HX-Request'):
        return HttpResponse(status=204, headers={'HX-Trigger': 'accessoryRemoved'})
    return redirect('garment_type_detail', pk=pk)


@login_required
@admin_required
def garment_type_delete(request, pk):
    """Delete garment type"""
    garment_type = get_object_or_404(GarmentType, pk=pk)
    
    if request.method == 'POST':
        garment_type.delete()
        messages.success(request, 'Garment type deleted successfully.')
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Redirect': '/garments/'})
        return redirect('garment_type_list')
    
    return render(request, 'garments/delete_confirm.html', {'garment_type': garment_type})


# ============== Order Management ==============

@login_required
@admin_required
def order_list(request):
    """List all orders"""
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    orders = Order.objects.select_related(
        'customer', 'garment_type', 'fabric', 'created_by'
    ).prefetch_related('payments')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(customer__name__icontains=search)
        )
    
    orders = orders.order_by('-created_at')
    
    paginator = Paginator(orders, 20)
    page = request.GET.get('page', 1)
    orders = paginator.get_page(page)
    
    if request.headers.get('HX-Request'):
        return render(request, 'orders/partials/order_table.html', {'orders': orders})
    
    return render(request, 'orders/list.html', {
        'orders': orders,
        'status_filter': status_filter,
        'search': search,
        'status_choices': Order.STATUS_CHOICES
    })


@login_required
@admin_required
def order_create(request):
    """Create new order with inventory deduction"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        # Check for new customer creation
        create_new_customer = request.POST.get('create_new_customer') == 'true'
        customer = None
        
        if create_new_customer:
            customer_name = request.POST.get('new_customer_name')
            customer_phone = request.POST.get('new_customer_phone')
            if customer_name and customer_phone:
                customer = Customer.objects.create(
                    name=customer_name,
                    contact_number=customer_phone
                )
        else:
            customer_id = request.POST.get('customer')
            if customer_id:
                customer = Customer.objects.filter(pk=customer_id).first()
        
        if not customer:
            error_msg = 'Please select or create a customer.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return render(request, 'orders/create.html', {
                'form': OrderForm(),
                'customers': Customer.objects.all().order_by('name'),
                'garment_types': GarmentType.objects.all(),
                'fabrics': Fabric.objects.all()
            })
        
        # Get garment type and fabric
        garment_type_id = request.POST.get('garment_type')
        fabric_id = request.POST.get('fabric')
        
        try:
            garment_type = GarmentType.objects.get(pk=garment_type_id)
            fabric = Fabric.objects.get(pk=fabric_id)
        except (GarmentType.DoesNotExist, Fabric.DoesNotExist):
            error_msg = 'Invalid garment type or fabric selection.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('order_create')
        
        quantity = int(request.POST.get('quantity', 1))
        total_price = Decimal(request.POST.get('total_price', 0))
        due_date = request.POST.get('due_date')
        special_instructions = request.POST.get('special_instructions', '')
        
        # Calculate fabric needed
        fabric_needed = garment_type.estimated_fabric_meters * quantity
        
        # Check fabric availability
        if not fabric.has_sufficient_stock(fabric_needed):
            error_msg = f'Insufficient fabric stock. Need {fabric_needed}m, available {fabric.stock_meters}m.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('order_create')
        
        # Check accessory availability
        required_accessories = garment_type.required_accessories.all()
        for req in required_accessories:
            needed = req.quantity_required * quantity
            if not req.accessory.has_sufficient_stock(needed):
                error_msg = f'Insufficient {req.accessory.name} stock. Need {needed}, available {req.accessory.stock_quantity}.'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg})
                messages.error(request, error_msg)
                return redirect('order_create')
        
        # Collect measurements
        measurements = {}
        measurement_fields = ['chest', 'waist', 'hips', 'shoulder', 'sleeve_length', 'body_length', 'inseam', 'neck']
        for field in measurement_fields:
            value = request.POST.get(field)
            if value:
                try:
                    measurements[field] = float(value)
                except ValueError:
                    pass
        
        try:
            with transaction.atomic():
                # Get payment option (default to deposit for 50%)
                payment_option = request.POST.get('payment_option', 'deposit')
                
                # Calculate deposit based on payment option
                if payment_option == 'full':
                    deposit_amount = total_price
                    balance_amount = Decimal('0')
                else:
                    deposit_amount = total_price * Decimal('0.5')
                    balance_amount = total_price - deposit_amount
                
                # Create order
                order = Order.objects.create(
                    customer=customer,
                    garment_type=garment_type,
                    fabric=fabric,
                    quantity=quantity,
                    fabric_meters_used=fabric_needed,
                    measurements=measurements,
                    special_instructions=special_instructions,
                    total_price=total_price,
                    deposit_amount=deposit_amount,
                    balance_amount=balance_amount,
                    due_date=due_date if due_date else None,
                    created_by=request.user
                )
                
                # Deduct fabric
                old_fabric_stock = fabric.stock_meters
                fabric.deduct_stock(fabric_needed)
                InventoryLog.objects.create(
                    item_type='fabric',
                    fabric=fabric,
                    action='deduct',
                    quantity=fabric_needed,
                    previous_stock=old_fabric_stock,
                    new_stock=fabric.stock_meters,
                    order=order,
                    notes=f'Order {order.order_number}',
                    created_by=request.user
                )
                
                # Deduct accessories
                for req in required_accessories:
                    needed = req.quantity_required * quantity
                    old_stock = req.accessory.stock_quantity
                    req.accessory.deduct_stock(needed)
                    
                    # Record order accessory
                    OrderAccessory.objects.create(
                        order=order,
                        accessory=req.accessory,
                        quantity_used=needed
                    )
                    
                    # Log inventory change
                    InventoryLog.objects.create(
                        item_type='accessory',
                        accessory=req.accessory,
                        action='deduct',
                        quantity=needed,
                        previous_stock=old_stock,
                        new_stock=req.accessory.stock_quantity,
                        order=order,
                        notes=f'Order {order.order_number}',
                        created_by=request.user
                    )
                
                # Auto-assign to tailor
                tailor = garment_type.default_tailor
                if not tailor:
                    # Assign to tailor with least tasks
                    from django.contrib.auth.models import User
                    tailors = User.objects.filter(profile__role='tailor').annotate(
                        task_count=Count('assigned_tasks', filter=Q(assigned_tasks__status__in=['assigned', 'in_progress']))
                    ).order_by('task_count').first()
                    tailor = tailors
                
                if tailor:
                    task = TailoringTask.objects.create(
                        order=order,
                        tailor=tailor,
                        status='assigned'
                    )
                    # Send in-app notification to tailor
                    Notification.notify_tailors_task_assigned(task, sender=request.user)
                
                # Create initial payment based on payment option
                payment_type = 'full' if payment_option == 'full' else 'deposit'
                Payment.objects.create(
                    order=order,
                    amount=deposit_amount,
                    payment_type=payment_type,
                    payment_method='cash',
                    status='completed',
                    received_by=request.user
                )
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'order_id': order.pk,
                        'order_number': order.order_number,
                        'payment_option': payment_option,
                        'message': f'Order {order.order_number} created successfully.'
                    })
                
                messages.success(request, f'Order {order.order_number} created successfully.')
                return redirect('order_detail', pk=order.pk)
                
        except Exception as e:
            error_msg = f'An error occurred: {str(e)}'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('order_create')
    
    # GET request
    form = OrderForm()
    return render(request, 'orders/create.html', {
        'form': form,
        'customers': Customer.objects.all().order_by('name'),
        'garment_types': GarmentType.objects.all(),
        'fabrics': Fabric.objects.all()
    })


@login_required
@admin_required
def order_detail(request, pk):
    """Order detail view"""
    order = get_object_or_404(
        Order.objects.select_related(
            'customer', 'garment_type', 'fabric', 'created_by'
        ).prefetch_related('payments', 'order_accessories__accessory'),
        pk=pk
    )
    
    try:
        task = order.tailoring_task
    except TailoringTask.DoesNotExist:
        task = None
    
    return render(request, 'orders/detail.html', {
        'order': order,
        'task': task
    })


@login_required
@admin_required
def order_cancel(request, pk):
    """Cancel order"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        if order.status in ['completed', 'delivered']:
            messages.error(request, 'Cannot cancel completed or delivered orders.')
        else:
            order.status = 'cancelled'
            order.save()
            messages.success(request, f'Order {order.order_number} cancelled.')
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Redirect': f'/orders/{pk}/'})
        return redirect('order_detail', pk=pk)
    
    return render(request, 'orders/cancel_confirm.html', {'order': order})


@login_required
@admin_required
def order_edit(request, pk):
    """Edit existing order"""
    order = get_object_or_404(Order, pk=pk)
    
    # Prevent editing completed or delivered orders
    if order.status in ['completed', 'delivered', 'cancelled']:
        messages.error(request, f'Cannot edit orders with status: {order.get_status_display()}')
        return redirect('order_detail', pk=pk)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        
        if form.is_valid():
            with transaction.atomic():
                # Get old values for inventory recalculation
                old_quantity = order.quantity
                old_fabric = order.fabric
                old_fabric_needed = order.garment_type.estimated_fabric_meters * old_quantity
                
                # Get new values
                garment_type = form.cleaned_data['garment_type']
                fabric = form.cleaned_data['fabric']
                quantity = form.cleaned_data['quantity']
                
                # Calculate new fabric needed
                new_fabric_needed = garment_type.estimated_fabric_meters * quantity
                
                # Handle fabric changes
                if fabric != old_fabric or quantity != old_quantity:
                    # Restore old fabric
                    old_fabric.add_stock(old_fabric_needed)
                    InventoryLog.objects.create(
                        item_type='fabric',
                        fabric=old_fabric,
                        action='add',
                        quantity=old_fabric_needed,
                        previous_stock=old_fabric.stock_meters - old_fabric_needed,
                        new_stock=old_fabric.stock_meters,
                        order=order,
                        notes=f'Order {order.order_number} edited - restoring old fabric',
                        created_by=request.user
                    )
                    
                    # Check new fabric availability
                    if not fabric.has_sufficient_stock(new_fabric_needed):
                        messages.error(
                            request,
                            f'Insufficient fabric stock. Need {new_fabric_needed}m, available {fabric.stock_meters}m.'
                        )
                        return render(request, 'orders/edit.html', {
                            'form': form,
                            'order': order,
                            'customers': Customer.objects.all(),
                            'garment_types': GarmentType.objects.all(),
                            'fabrics': Fabric.objects.all()
                        })
                    
                    # Deduct new fabric
                    old_stock = fabric.stock_meters
                    fabric.deduct_stock(new_fabric_needed)
                    InventoryLog.objects.create(
                        item_type='fabric',
                        fabric=fabric,
                        action='deduct',
                        quantity=new_fabric_needed,
                        previous_stock=old_stock,
                        new_stock=fabric.stock_meters,
                        order=order,
                        notes=f'Order {order.order_number} edited',
                        created_by=request.user
                    )
                
                # Update order
                order = form.save(commit=False)
                order.fabric_meters_used = new_fabric_needed
                order.save()
                
                messages.success(request, f'Order {order.order_number} updated successfully.')
                return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
    
    return render(request, 'orders/edit.html', {
        'form': form,
        'order': order,
        'customers': Customer.objects.all().order_by('name'),
        'garment_types': GarmentType.objects.all(),
        'fabrics': Fabric.objects.all()
    })


@login_required
@admin_required
def get_garment_requirements(request, pk):
    """HTMX endpoint to get garment type requirements"""
    garment_type = get_object_or_404(GarmentType, pk=pk)
    accessories = garment_type.required_accessories.select_related('accessory').all()
    
    data = {
        'estimated_fabric': float(garment_type.estimated_fabric_meters),
        'base_price': float(garment_type.base_price),
        'accessories': [
            {
                'name': a.accessory.name,
                'quantity': float(a.quantity_required),
                'available': float(a.accessory.stock_quantity)
            }
            for a in accessories
        ]
    }
    
    return JsonResponse(data)


# ============== Tailoring Task Management ==============

@login_required
@admin_required
def task_create(request):
    """Create or reassign a task to a tailor"""
    order_pk = request.GET.get('order')
    order = get_object_or_404(Order, pk=order_pk) if order_pk else None
    
    if request.method == 'POST':
        tailor_pk = request.POST.get('tailor')
        tailor = get_object_or_404(User, pk=tailor_pk, profile__role='tailor')
        
        with transaction.atomic():
            # Check if task already exists for this order
            task, created = TailoringTask.objects.get_or_create(
                order=order,
                defaults={
                    'tailor': tailor,
                    'status': 'assigned'
                }
            )
            
            # If task existed, update the tailor
            if not created:
                task.tailor = tailor
                task.status = 'assigned'
                task.save()
                action = f'reassigned to {tailor.get_full_name() or tailor.username}'
            else:
                action = f'assigned to {tailor.get_full_name() or tailor.username}'
            
            # Notify the tailor about the assignment
            Notification.notify_tailors_task_assigned(task, sender=request.user)
            
            messages.success(request, f'Task {action}.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Redirect': f'/orders/{order.pk}/'})
            return redirect('order_detail', pk=order.pk)
    
    # Get available tailors
    tailors = User.objects.filter(profile__role='tailor', is_active=True).order_by('first_name')
    
    # Get current task if it exists
    current_task = TailoringTask.objects.filter(order=order).first() if order else None
    
    return render(request, 'tasks/create.html', {
        'order': order,
        'tailors': tailors,
        'current_task': current_task
    })


@login_required
def task_list(request):
    """List tasks (filtered by role)"""
    if hasattr(request.user, 'profile') and request.user.profile.is_tailor:
        tasks = TailoringTask.objects.filter(tailor=request.user)
    else:
        tasks = TailoringTask.objects.all()
    
    tasks = tasks.select_related(
        'order', 'order__customer', 'order__garment_type', 'tailor'
    ).order_by('-created_at')
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    paginator = Paginator(tasks, 20)
    page = request.GET.get('page', 1)
    tasks = paginator.get_page(page)
    
    return render(request, 'tasks/list.html', {
        'tasks': tasks,
        'status_filter': status_filter,
        'status_choices': TailoringTask.STATUS_CHOICES
    })


@login_required
def task_detail(request, pk):
    """Task detail view"""
    task = get_object_or_404(
        TailoringTask.objects.select_related(
            'order', 'order__customer', 'order__garment_type', 
            'order__fabric', 'tailor', 'approved_by'
        ),
        pk=pk
    )
    
    # Check access
    if hasattr(request.user, 'profile') and request.user.profile.is_tailor:
        if task.tailor != request.user:
            messages.error(request, 'You do not have access to this task.')
            return redirect('task_list')
    
    return render(request, 'tasks/detail.html', {'task': task})


@login_required
def task_update_status(request, pk):
    """Update task status (for tailors)"""
    task = get_object_or_404(TailoringTask, pk=pk)
    
    # Tailors can only update their own tasks
    if hasattr(request.user, 'profile') and request.user.profile.is_tailor:
        if task.tailor != request.user:
            messages.error(request, 'You can only update your own tasks.')
            return redirect('task_list')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status == 'in_progress' and task.status == 'assigned':
            task.status = 'in_progress'
            task.started_date = timezone.now()
        elif new_status == 'completed' and task.status == 'in_progress':
            task.status = 'completed'
            task.completed_date = timezone.now()
            # Notify all admins that task is completed and awaiting approval
            Notification.notify_admins_task_completed(task, sender=request.user)
        
        task.notes = notes
        task.save()
        
        messages.success(request, 'Task updated successfully.')
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Trigger': 'taskUpdated'})
        return redirect('task_detail', pk=pk)
    
    return render(request, 'tasks/partials/update_form.html', {'task': task})


@login_required
def task_update_notes(request, pk):
    """Update task notes"""
    task = get_object_or_404(TailoringTask, pk=pk)
    
    # Check access - tailors can update their own tasks, admins can update any
    if hasattr(request.user, 'profile') and request.user.profile.is_tailor:
        if task.tailor != request.user:
            messages.error(request, 'You can only update notes on your own tasks.')
            return redirect('task_list')
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        task.notes = notes
        task.save()
        
        messages.success(request, 'Notes updated successfully.')
        
        if request.headers.get('HX-Request'):
            # Return updated notes section
            return render(request, 'tasks/partials/notes_section.html', {'task': task})
        return redirect('task_detail', pk=pk)
    
    return render(request, 'tasks/detail.html', {'task': task})


@login_required
@admin_required
def task_approve(request, pk):
    """Admin approves completed task"""
    task = get_object_or_404(TailoringTask, pk=pk)
    
    if task.status != 'completed':
        messages.error(request, 'Can only approve completed tasks.')
        return redirect('task_detail', pk=pk)
    
    if request.method == 'POST':
        with transaction.atomic():
            task.status = 'approved'
            task.approved_date = timezone.now()
            task.approved_by = request.user
            task.save()
            
            # Update order status
            task.order.status = 'completed'
            task.order.completed_date = timezone.now()
            task.order.save()
            
            # Send in-app notification to tailor about approval
            Notification.notify_tailor_task_approved(task, sender=request.user)
            
            # Send SMS notification
            send_order_ready_sms(task.order)
            
            messages.success(request, f'Task approved. SMS notification sent to {task.order.customer.name}.')
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Redirect': f'/tasks/{pk}/'})
        return redirect('task_detail', pk=pk)
    
    return render(request, 'tasks/approve_confirm.html', {'task': task})


# ============== Payment Management ==============

@login_required
@admin_required
def payment_list(request):
    """List all payments"""
    payments = Payment.objects.select_related(
        'order', 'order__customer', 'received_by'
    ).order_by('-created_at')
    
    paginator = Paginator(payments, 30)
    page = request.GET.get('page', 1)
    payments = paginator.get_page(page)
    
    return render(request, 'payments/list.html', {'payments': payments})


@login_required
@admin_required
def payment_create(request, order_pk):
    """Create payment for an order"""
    order = get_object_or_404(Order, pk=order_pk)
    
    if order.remaining_balance <= 0:
        messages.info(request, 'This order is already fully paid.')
        return redirect('order_detail', pk=order_pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            payment.payment_method = 'cash'
            payment.received_by = request.user
            
            # Determine payment type
            if payment.amount >= order.remaining_balance:
                payment.amount = order.remaining_balance
                payment.payment_type = 'balance'
            
            payment.save()
            
            messages.success(request, f'Payment of ₱{payment.amount} recorded.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Redirect': f'/orders/{order_pk}/'})
            return redirect('order_detail', pk=order_pk)
    else:
        form = PaymentForm(initial={
            'amount': order.remaining_balance,
            'payment_type': 'balance'
        })
    
    return render(request, 'payments/create.html', {
        'form': form,
        'order': order
    })


@login_required
@admin_required
def payment_receipt(request, pk):
    """Alias for receipt_print using pk parameter"""
    return receipt_print(request, payment_pk=pk)


@login_required
@admin_required
def receipt_print(request, payment_pk):
    """Print receipt for payment"""
    payment = get_object_or_404(
        Payment.objects.select_related('order', 'order__customer', 'received_by'),
        pk=payment_pk
    )
    
    return render(request, 'payments/receipt.html', {'payment': payment})


@login_required
@admin_required
def order_receipt(request, order_pk):
    """Print full order receipt"""
    order = get_object_or_404(
        Order.objects.select_related('customer', 'garment_type', 'fabric')
        .prefetch_related('payments'),
        pk=order_pk
    )
    
    return render(request, 'payments/order_receipt.html', {'order': order})


# ============== SMS Notification ==============

def send_order_ready_sms(order):
    """Send SMS notification via Semaphore"""
    api_key = getattr(settings, 'SEMAPHORE_API_KEY', None)
    sender_name = getattr(settings, 'SEMAPHORE_SENDER_NAME', None)
    
    if not api_key:
        # Log but don't fail
        SMSLog.objects.create(
            customer=order.customer,
            order=order,
            phone_number=order.customer.contact_number,
            message='API key not configured',
            status='failed',
            response='SEMAPHORE_API_KEY not set in settings'
        )
        return False
    
    # Build message with balance info if applicable
    balance = order.remaining_balance
    if balance > 0:
        balance_info = f"Please bring the remaining balance of P{balance:.2f} upon pickup. "
    else:
        balance_info = "Your order is fully paid. "
    
    message = (
        f"Good day, {order.customer.name}! "
        f"Great news from El Senior Original Tailoring - your {order.garment_type.name} "
        f"(Order #{order.order_number}) is now ready for pickup! "
        f"{balance_info}"
        f"Thank you for trusting us! - El Senior Team"
    )
    
    phone = order.customer.contact_number
    # Clean phone number
    phone = phone.replace(' ', '').replace('-', '')
    if not phone.startswith('+63') and not phone.startswith('63'):
        if phone.startswith('0'):
            phone = '63' + phone[1:]
    
    # Create log entry
    sms_log = SMSLog.objects.create(
        customer=order.customer,
        order=order,
        phone_number=phone,
        message=message,
        status='pending'
    )
    
    try:
        # Build request data
        data = {
            'apikey': api_key,
            'number': phone,
            'message': message
        }
        
        # Add sender name if configured
        if sender_name:
            data['sendername'] = sender_name
        
        response = requests.post(
            'https://api.semaphore.co/api/v4/messages',
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            sms_log.status = 'sent'
            sms_log.sent_at = timezone.now()
        else:
            sms_log.status = 'failed'
        
        sms_log.response = response.text
        sms_log.save()
        
        return response.status_code == 200
        
    except Exception as e:
        sms_log.status = 'failed'
        sms_log.response = str(e)
        sms_log.save()
        return False


# ============== User Management ==============

@login_required
@admin_required
def user_list(request):
    """List all users"""
    from django.contrib.auth.models import User
    users = User.objects.select_related('profile').all()
    return render(request, 'users/list.html', {'users': users})


@login_required
@admin_required
def user_create(request):
    """Create new user"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                phone=form.cleaned_data.get('phone', '')
            )
            messages.success(request, f'User "{user.username}" created successfully.')
            
            if request.headers.get('HX-Request'):
                return HttpResponse(status=204, headers={'HX-Redirect': '/users/'})
            return redirect('user_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/create.html', {'form': form})


@login_required
@admin_required
def user_edit(request, pk):
    """Edit user details"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        
        # Update profile
        profile = user.profile
        profile.phone = request.POST.get('phone', '')
        profile.role = request.POST.get('role', profile.role)
        
        user.save()
        profile.save()
        
        messages.success(request, f'User "{user.username}" updated successfully.')
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Redirect': '/users/'})
        return redirect('user_list')
    
    return render(request, 'users/edit.html', {'edit_user': user})


@login_required
@admin_required
def user_toggle_active(request, pk):
    """Toggle user active status"""
    from django.contrib.auth.models import User
    user = get_object_or_404(User, pk=pk)
    
    if user == request.user:
        messages.error(request, 'You cannot deactivate yourself.')
    else:
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.username} has been {status}.')
    
    if request.headers.get('HX-Request'):
        return HttpResponse(status=204, headers={'HX-Trigger': 'userUpdated'})
    return redirect('user_list')


# ============== Reports ==============

@login_required
@admin_required
def reports_dashboard(request):
    """Reports and analytics"""
    from datetime import timedelta
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Daily orders for the last 7 days
    daily_orders = []
    for i in range(7):
        date = today - timedelta(days=i)
        count = Order.objects.filter(order_date__date=date).count()
        daily_orders.append({'date': date, 'count': count})
    
    # Revenue breakdown
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    monthly_revenue = Payment.objects.filter(
        status='completed',
        payment_date__date__gte=month_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    weekly_revenue = Payment.objects.filter(
        status='completed',
        payment_date__date__gte=week_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Popular garment types
    popular_garments = GarmentType.objects.annotate(
        order_count=Count('order')
    ).order_by('-order_count')[:5]
    
    # Top customers
    top_customers = Customer.objects.annotate(
        order_count=Count('orders'),
        total_spent=Sum('orders__total_price')
    ).order_by('-total_spent')[:10]
    
    context = {
        'daily_orders': daily_orders[::-1],
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'weekly_revenue': weekly_revenue,
        'popular_garments': popular_garments,
        'top_customers': top_customers,
    }
    
    return render(request, 'reports/dashboard.html', context)


# ============== API Endpoints (for HTMX) ==============

@login_required
def api_check_fabric_stock(request):
    """Check fabric stock availability"""
    fabric_id = request.GET.get('fabric_id')
    quantity = request.GET.get('quantity', 1)
    garment_type_id = request.GET.get('garment_type_id')
    
    try:
        fabric = Fabric.objects.get(pk=fabric_id)
        garment_type = GarmentType.objects.get(pk=garment_type_id)
        
        required = garment_type.estimated_fabric_meters * int(quantity)
        available = fabric.stock_meters
        sufficient = available >= required
        
        return JsonResponse({
            'required': float(required),
            'available': float(available),
            'sufficient': sufficient
        })
    except (Fabric.DoesNotExist, GarmentType.DoesNotExist):
        return JsonResponse({'error': 'Invalid selection'}, status=400)


@login_required
def api_customer_search(request):
    """Search customers for autocomplete"""
    q = request.GET.get('q', '')
    customers = Customer.objects.filter(
        Q(name__icontains=q) | Q(contact_number__icontains=q)
    )[:10]
    
    return JsonResponse({
        'customers': [
            {'id': c.id, 'name': c.name, 'phone': c.contact_number}
            for c in customers
        ]
    })


# ============== Claims / Pickup Management ==============

@login_required
@admin_required
def claims_list(request):
    """List orders ready for pickup (completed status)"""
    # Orders that are completed (tailoring done, approved) and ready for pickup
    orders = Order.objects.filter(
        status='completed'
    ).select_related(
        'customer', 'garment_type', 'fabric'
    ).prefetch_related('payments').order_by('-completed_date', '-created_at')
    
    # Also show recently delivered for reference
    recently_delivered = Order.objects.filter(
        status='delivered'
    ).select_related(
        'customer', 'garment_type'
    ).order_by('-updated_at')[:10]
    
    # Stats
    stats = {
        'ready_for_pickup': orders.count(),
        'with_balance': orders.filter(balance_amount__gt=0).count(),
        'fully_paid': orders.filter(balance_amount__lte=0).count(),
    }
    
    # Calculate total pending balance
    total_pending_balance = sum(o.remaining_balance for o in orders)
    stats['total_pending_balance'] = total_pending_balance
    
    context = {
        'orders': orders,
        'recently_delivered': recently_delivered,
        'stats': stats,
    }
    
    return render(request, 'claims/list.html', context)


@login_required
@admin_required
def process_claim(request, pk):
    """Process customer claim/pickup with optional balance payment"""
    order = get_object_or_404(
        Order.objects.select_related(
            'customer', 'garment_type', 'fabric'
        ).prefetch_related('payments', 'order_accessories__accessory'),
        pk=pk
    )
    
    if order.status not in ['completed']:
        messages.error(request, 'This order is not ready for pickup.')
        return redirect('claims_list')
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                remaining = order.remaining_balance
                collect_balance = request.POST.get('collect_balance') == 'true'
                
                # If there's a remaining balance and admin chose to collect it
                if remaining > 0 and collect_balance:
                    # Create balance payment
                    payment = Payment.objects.create(
                        order=order,
                        amount=remaining,
                        payment_type='balance',
                        payment_method='cash',
                        status='completed',
                        notes='Balance collected at pickup',
                        received_by=request.user
                    )
                
                # Credit commission to tailor when order is claimed
                try:
                    task = order.tailoring_task
                    if task and task.tailor and not task.commission_paid:
                        # Create commission record
                        TailorCommission.create_from_task(task)
                        
                        # Send notification to tailor about commission
                        Notification.create_notification(
                            recipient=task.tailor,
                            title='Commission Credited',
                            message=f'You earned a commission of PHP{task.commission_amount:.2f} for completing order {order.order_number}. Great job!',
                            notification_type='general',
                            sender=request.user,
                            order=order,
                            task=task,
                            action_url='/commissions/',
                            priority='normal'
                        )
                except TailoringTask.DoesNotExist:
                    pass
                
                # Update order status to delivered
                order.status = 'delivered'
                order.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'order_id': order.pk,
                        'order_number': order.order_number,
                        'message': f'Order {order.order_number} has been marked as delivered.'
                    })
                
                messages.success(request, f'Order {order.order_number} has been claimed and marked as delivered.')
                return redirect('claim_receipt', pk=order.pk)
                
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f'Error processing claim: {str(e)}')
            return redirect('claims_list')
    
    # GET request - show the claim form
    context = {
        'order': order,
        'remaining_balance': order.remaining_balance,
        'total_paid': order.total_paid,
    }
    
    return render(request, 'claims/process.html', context)


@login_required
@admin_required
def claim_receipt(request, pk):
    """Generate comprehensive claim/delivery receipt"""
    order = get_object_or_404(
        Order.objects.select_related(
            'customer', 'garment_type', 'fabric', 'created_by'
        ).prefetch_related('payments', 'order_accessories__accessory'),
        pk=pk
    )
    
    # Get task info
    try:
        task = order.tailoring_task
    except TailoringTask.DoesNotExist:
        task = None
    
    context = {
        'order': order,
        'task': task,
        'claim_date': timezone.now(),
    }
    
    return render(request, 'claims/receipt.html', context)


# ============== Notification Management ==============

@login_required
def notification_list(request):
    """List all notifications for the current user"""
    filter_type = request.GET.get('filter', 'all')
    
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'order', 'task').order_by('-created_at')
    
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)
    
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page', 1)
    notifications = paginator.get_page(page)
    
    # Get counts for filter tabs
    total_count = Notification.objects.filter(recipient=request.user).count()
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    context = {
        'notifications': notifications,
        'filter_type': filter_type,
        'total_count': total_count,
        'unread_count': unread_count,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'notifications/partials/notification_list.html', context)
    
    return render(request, 'notifications/list.html', context)


@login_required
def notification_mark_read(request, pk):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    
    # If it's an HTMX request, return updated notification item
    if request.headers.get('HX-Request'):
        return render(request, 'notifications/partials/notification_item.html', {
            'notification': notification
        })
    
    # If there's an action URL, redirect to it
    if notification.action_url:
        return redirect(notification.action_url)
    
    return redirect('notification_list')


@login_required
def notification_mark_all_read(request):
    """Mark all notifications as read for the current user"""
    if request.method == 'POST':
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        messages.success(request, 'All notifications marked as read.')
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Trigger': 'notificationsUpdated'})
    
    return redirect('notification_list')


@login_required
def notification_delete(request, pk):
    """Delete a notification"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    
    if request.method == 'POST':
        notification.delete()
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Trigger': 'notificationDeleted'})
        
        messages.success(request, 'Notification deleted.')
    
    return redirect('notification_list')


@login_required
def notification_clear_all(request):
    """Clear all notifications for the current user"""
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user).delete()
        messages.success(request, 'All notifications cleared.')
        
        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={'HX-Trigger': 'notificationsCleared'})
    
    return redirect('notification_list')


@login_required
def notification_dropdown(request):
    """HTMX endpoint for notification dropdown content"""
    recent_notifications = Notification.get_recent_notifications(request.user, limit=5)
    unread_count = Notification.get_unread_count(request.user)
    
    return render(request, 'notifications/partials/dropdown.html', {
        'notifications': recent_notifications,
        'unread_count': unread_count,
    })


@login_required
def notification_count(request):
    """HTMX endpoint for notification count badge"""
    unread_count = Notification.get_unread_count(request.user)
    
    if request.headers.get('HX-Request'):
        if unread_count > 0:
            return HttpResponse(f'<span class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">{unread_count if unread_count < 100 else "99+"}</span>')
        return HttpResponse('')
    
    return JsonResponse({'count': unread_count})


# ============== Commission Management ==============

@login_required
def commission_dashboard(request):
    """Commission dashboard - tailors see their own, admins see all"""
    from datetime import timedelta
    from django.db.models import Sum, Count, Avg
    
    today = timezone.now().date()
    
    if hasattr(request.user, 'profile') and request.user.profile.is_tailor:
        # Tailor view - show their commissions
        commissions = TailorCommission.objects.filter(
            tailor=request.user
        ).select_related('order', 'task').order_by('-earned_date')
        
        # Summary stats
        total_earned = commissions.aggregate(total=Sum('commission_amount'))['total'] or Decimal('0')
        total_tasks = commissions.count()
        
        # This week
        week_start = today - timedelta(days=today.weekday())
        week_commissions = commissions.filter(earned_date__date__gte=week_start)
        week_total = week_commissions.aggregate(total=Sum('commission_amount'))['total'] or Decimal('0')
        
        # This month
        month_start = today.replace(day=1)
        month_commissions = commissions.filter(earned_date__date__gte=month_start)
        month_total = month_commissions.aggregate(total=Sum('commission_amount'))['total'] or Decimal('0')
        
        # Pending commissions (tasks approved but order not yet claimed)
        pending_tasks = TailoringTask.objects.filter(
            tailor=request.user,
            status='approved',
            commission_paid=False
        ).select_related('order')
        
        pending_amount = sum(task.commission_amount for task in pending_tasks)
        
        context = {
            'commissions': commissions[:20],
            'total_earned': total_earned,
            'total_tasks': total_tasks,
            'week_total': week_total,
            'month_total': month_total,
            'pending_amount': pending_amount,
            'pending_tasks': pending_tasks,
            'is_tailor_view': True,
        }
        
        return render(request, 'commissions/tailor_dashboard.html', context)
    
    else:
        # Admin view - show all commissions with tailor breakdown
        return redirect('admin_commission_report')


@login_required
def tailor_commission_report(request):
    """Generate PDF commission report for tailor"""
    from datetime import timedelta
    from .reports import generate_tailor_commission_report
    
    # Determine date range based on report type
    report_type = request.GET.get('type', 'weekly')
    today = timezone.now().date()
    
    if report_type == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif report_type == 'monthly':
        start_date = today.replace(day=1)
        end_date = today
    elif report_type == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        # Custom range
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if start_date_str and end_date_str:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            start_date = today - timedelta(days=7)
            end_date = today
    
    # Get tailor (either current user or specified for admin)
    if hasattr(request.user, 'profile') and request.user.profile.is_admin:
        tailor_id = request.GET.get('tailor_id')
        if tailor_id:
            tailor = get_object_or_404(User, pk=tailor_id, profile__role='tailor')
        else:
            tailor = request.user
    else:
        tailor = request.user
    
    # Get commissions
    commissions = TailorCommission.objects.filter(
        tailor=tailor,
        earned_date__date__gte=start_date,
        earned_date__date__lte=end_date
    ).select_related('order', 'task').order_by('-earned_date')
    
    # Get summary
    summary = TailorCommission.get_tailor_summary(tailor, start_date, end_date)
    
    # Generate PDF
    pdf = generate_tailor_commission_report(
        tailor=tailor,
        commissions=list(commissions),
        start_date=start_date,
        end_date=end_date,
        summary=summary,
        report_type=report_type
    )
    
    # Create response
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"commission_report_{tailor.username}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
@admin_required
def admin_commission_report(request):
    """Admin commission report dashboard and PDF generation"""
    from datetime import timedelta
    from django.db.models import Sum, Count
    
    today = timezone.now().date()
    
    # Handle PDF generation request
    if request.GET.get('format') == 'pdf':
        return generate_admin_commission_pdf(request)
    
    # Dashboard view
    report_type = request.GET.get('type', 'monthly')
    
    if report_type == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif report_type == 'monthly':
        start_date = today.replace(day=1)
        end_date = today
    elif report_type == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if start_date_str and end_date_str:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            start_date = today.replace(day=1)
            end_date = today
    
    # Get all commissions in the period
    commissions = TailorCommission.objects.filter(
        earned_date__date__gte=start_date,
        earned_date__date__lte=end_date
    ).select_related('tailor', 'order', 'task')
    
    # Overall summary
    total_commissions = commissions.aggregate(total=Sum('commission_amount'))['total'] or Decimal('0')
    total_orders_value = commissions.aggregate(total=Sum('order_amount'))['total'] or Decimal('0')
    total_tasks = commissions.count()
    
    # Per-tailor breakdown
    tailors_summary = []
    tailors = User.objects.filter(profile__role='tailor').select_related('profile')
    
    for tailor in tailors:
        tailor_commissions = commissions.filter(tailor=tailor)
        summary = tailor_commissions.aggregate(
            total_commission=Sum('commission_amount'),
            total_order_value=Sum('order_amount'),
            task_count=Count('id')
        )
        
        if summary['task_count'] and summary['task_count'] > 0:
            tailors_summary.append({
                'tailor': tailor,
                'tailor_name': tailor.get_full_name() or tailor.username,
                'total_commission': summary['total_commission'] or Decimal('0'),
                'total_order_value': summary['total_order_value'] or Decimal('0'),
                'task_count': summary['task_count'] or 0,
            })
    
    # Sort by total commission descending
    tailors_summary.sort(key=lambda x: x['total_commission'], reverse=True)
    
    # Recent commissions
    recent_commissions = commissions.order_by('-earned_date')[:20]
    
    # Garment type breakdown
    garment_breakdown = commissions.values('garment_type').annotate(
        count=Count('id'),
        total_commission=Sum('commission_amount'),
        total_value=Sum('order_amount')
    ).order_by('-total_commission')[:10]
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'report_type': report_type,
        'total_commissions': total_commissions,
        'total_orders_value': total_orders_value,
        'total_tasks': total_tasks,
        'tailors_summary': tailors_summary,
        'recent_commissions': recent_commissions,
        'garment_breakdown': garment_breakdown,
        'tailors': tailors,
    }
    
    return render(request, 'commissions/admin_dashboard.html', context)


@login_required
@admin_required
def generate_admin_commission_pdf(request):
    """Generate comprehensive admin PDF report"""
    from datetime import timedelta
    from django.db.models import Sum, Count
    from .reports import generate_admin_commission_report
    
    today = timezone.now().date()
    report_type = request.GET.get('type', 'monthly')
    
    if report_type == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif report_type == 'monthly':
        start_date = today.replace(day=1)
        end_date = today
    elif report_type == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if start_date_str and end_date_str:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            start_date = today.replace(day=1)
            end_date = today
    
    # Get all commissions
    commissions = TailorCommission.objects.filter(
        earned_date__date__gte=start_date,
        earned_date__date__lte=end_date
    ).select_related('tailor', 'order')
    
    # Build tailors summary
    tailors_summary = []
    tailors = User.objects.filter(profile__role='tailor')
    
    for tailor in tailors:
        tailor_commissions = commissions.filter(tailor=tailor)
        summary = tailor_commissions.aggregate(
            total_commission=Sum('commission_amount'),
            total_order_value=Sum('order_amount'),
            task_count=Count('id')
        )
        
        if summary['task_count'] and summary['task_count'] > 0:
            tailors_summary.append({
                'tailor_name': tailor.get_full_name() or tailor.username,
                'total_commission': float(summary['total_commission'] or 0),
                'total_order_value': float(summary['total_order_value'] or 0),
                'task_count': summary['task_count'] or 0,
            })
    
    tailors_summary.sort(key=lambda x: x['total_commission'], reverse=True)
    
    # Generate PDF
    pdf = generate_admin_commission_report(
        commissions=list(commissions),
        tailors_summary=tailors_summary,
        start_date=start_date,
        end_date=end_date,
        report_type='comprehensive',
        generated_by=request.user.get_full_name() or request.user.username
    )
    
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"commission_report_admin_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
@admin_required  
def admin_garment_report(request):
    """Generate garment production and commission report"""
    from datetime import timedelta
    from django.db.models import Sum, Count
    from .reports import generate_garment_production_report
    
    today = timezone.now().date()
    report_type = request.GET.get('type', 'monthly')
    
    if report_type == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif report_type == 'monthly':
        start_date = today.replace(day=1)
        end_date = today
    elif report_type == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if start_date_str and end_date_str:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            start_date = today.replace(day=1)
            end_date = today
    
    # Get garment statistics from commissions
    garment_stats = TailorCommission.objects.filter(
        earned_date__date__gte=start_date,
        earned_date__date__lte=end_date
    ).values('garment_type').annotate(
        quantity=Sum('quantity'),
        revenue=Sum('order_amount'),
        commission=Sum('commission_amount')
    ).order_by('-revenue')
    
    garment_list = [
        {
            'garment_type': g['garment_type'],
            'quantity': g['quantity'] or 0,
            'revenue': float(g['revenue'] or 0),
            'commission': float(g['commission'] or 0),
        }
        for g in garment_stats
    ]
    
    pdf = generate_garment_production_report(
        garment_stats=garment_list,
        start_date=start_date,
        end_date=end_date,
        generated_by=request.user.get_full_name() or request.user.username
    )
    
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"garment_production_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
@admin_required
def admin_tailor_performance_report(request):
    """Generate tailor performance report"""
    from datetime import timedelta
    from django.db.models import Sum, Count, Avg, F
    from .reports import generate_tailor_performance_report
    
    today = timezone.now().date()
    report_type = request.GET.get('type', 'monthly')
    
    if report_type == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif report_type == 'monthly':
        start_date = today.replace(day=1)
        end_date = today
    elif report_type == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        if start_date_str and end_date_str:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            start_date = today.replace(day=1)
            end_date = today
    
    tailors_data = []
    tailors = User.objects.filter(profile__role='tailor').select_related('profile')
    
    for tailor in tailors:
        # Get commission data
        commissions = TailorCommission.objects.filter(
            tailor=tailor,
            earned_date__date__gte=start_date,
            earned_date__date__lte=end_date
        )
        
        summary = commissions.aggregate(
            total_commission=Sum('commission_amount'),
            total_revenue=Sum('order_amount'),
            task_count=Count('id')
        )
        
        # Get completed tasks to calculate avg completion time
        tasks = TailoringTask.objects.filter(
            tailor=tailor,
            status='approved',
            approved_date__date__gte=start_date,
            approved_date__date__lte=end_date
        )
        
        avg_time = 'N/A'
        if tasks.exists():
            # Calculate average time from assignment to completion
            total_days = 0
            count = 0
            for task in tasks:
                if task.completed_date and task.assigned_date:
                    delta = task.completed_date - task.assigned_date
                    total_days += delta.days
                    count += 1
            if count > 0:
                avg_days = total_days / count
                avg_time = f"{avg_days:.1f} days"
        
        if summary['task_count'] and summary['task_count'] > 0:
            tailors_data.append({
                'name': tailor.get_full_name() or tailor.username,
                'tasks_completed': summary['task_count'] or 0,
                'avg_completion_time': avg_time,
                'revenue': float(summary['total_revenue'] or 0),
                'commission': float(summary['total_commission'] or 0),
            })
    
    tailors_data.sort(key=lambda x: x['commission'], reverse=True)
    
    pdf = generate_tailor_performance_report(
        tailors_data=tailors_data,
        start_date=start_date,
        end_date=end_date,
        generated_by=request.user.get_full_name() or request.user.username
    )
    
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"tailor_performance_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def commission_history(request):
    """View full commission history with filtering"""
    from django.db.models import Sum
    
    # For tailors, show their own commissions
    if hasattr(request.user, 'profile') and request.user.profile.is_tailor:
        commissions = TailorCommission.objects.filter(
            tailor=request.user
        ).select_related('order', 'task')
    else:
        # Admin sees all
        commissions = TailorCommission.objects.all().select_related(
            'tailor', 'order', 'task'
        )
    
    # Filtering
    status_filter = request.GET.get('status', '')
    if status_filter:
        commissions = commissions.filter(status=status_filter)
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        from datetime import datetime
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        commissions = commissions.filter(earned_date__date__gte=date_from)
    
    if date_to:
        from datetime import datetime
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        commissions = commissions.filter(earned_date__date__lte=date_to)
    
    commissions = commissions.order_by('-earned_date')
    
    # Summary
    summary = commissions.aggregate(
        total=Sum('commission_amount'),
        count=Count('id')
    )
    
    paginator = Paginator(commissions, 30)
    page = request.GET.get('page', 1)
    commissions = paginator.get_page(page)
    
    context = {
        'commissions': commissions,
        'total_amount': summary['total'] or Decimal('0'),
        'total_count': summary['count'] or 0,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'commissions/history.html', context)

