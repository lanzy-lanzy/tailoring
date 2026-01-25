from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from decimal import Decimal
from .models import (
    UserProfile, Customer, Fabric, FabricColor, FabricMaterial, Accessory,
    GarmentType, GarmentTypeAccessory, Order,
    TailoringTask, Payment, Rework, TailorGarmentCommission
)


class LoginForm(AuthenticationForm):
    """Custom login form with styling"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent',
            'placeholder': 'Password'
        })
    )


class UserRegistrationForm(UserCreationForm):
    """Form for creating new users (Admin/Tailor)"""
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Email'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Phone Number'
        })
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Confirm Password'
        })


class CustomerForm(forms.ModelForm):
    """Form for creating/editing customers"""
    class Meta:
        model = Customer
        fields = ['name', 'contact_number', 'address', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Customer Name'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Contact Number (e.g., 09171234567)'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Address',
                'rows': 3
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Email (optional)'
            }),
        }


class FabricForm(forms.ModelForm):
    """Form for managing fabrics"""
    material = forms.ModelChoiceField(
        queryset=FabricMaterial.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
        })
    )
    color = forms.ModelChoiceField(
        queryset=FabricColor.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
        })
    )
    
    class Meta:
        model = Fabric
        fields = ['material', 'color', 'stock_meters', 'price_per_meter', 'description']
        widgets = {
            'stock_meters': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Stock (meters)',
                'step': '0.01',
                'min': '0'
            }),
            'price_per_meter': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Price per meter',
                'step': '0.01',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Description',
                'rows': 3
            }),
        }



class AccessoryForm(forms.ModelForm):
    """Form for managing accessories"""
    class Meta:
        model = Accessory
        fields = ['name', 'unit', 'stock_quantity', 'price_per_unit', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Accessory Name'
            }),
            'unit': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Stock Quantity',
                'step': '0.01',
                'min': '0'
            }),
            'price_per_unit': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Price per unit',
                'step': '0.01',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Description',
                'rows': 3
            }),
        }



class GarmentTypeForm(forms.ModelForm):
    """Form for managing garment types"""
    class Meta:
        model = GarmentType
        fields = ['name', 'description', 'garment_category', 'estimated_fabric_meters', 'base_price', 'default_tailor']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Garment Type Name'
            }),
            'garment_category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Description',
                'rows': 3
            }),
            'estimated_fabric_meters': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Estimated Fabric (meters)',
                'step': '0.01',
                'min': '0'
            }),
            'base_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Base Price',
                'step': '0.01',
                'min': '0'
            }),
            'default_tailor': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show tailors in the default_tailor dropdown
        self.fields['default_tailor'].queryset = User.objects.filter(
            profile__role='tailor'
        )
        self.fields['default_tailor'].required = False


class GarmentTypeAccessoryForm(forms.ModelForm):
    """Form for adding accessories to garment types"""
    class Meta:
        model = GarmentTypeAccessory
        fields = ['accessory', 'quantity_required']
        widgets = {
            'accessory': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
            }),
            'quantity_required': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Quantity Required',
                'step': '0.01',
                'min': '0'
            }),
        }


class OrderForm(forms.ModelForm):
    """Form for creating orders"""
    
    # Measurement fields
    chest = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Chest (inches)',
            'step': '0.25'
        })
    )
    waist = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Waist (inches)',
            'step': '0.25'
        })
    )
    hips = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Hips (inches)',
            'step': '0.25'
        })
    )
    shoulder = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Shoulder (inches)',
            'step': '0.25'
        })
    )
    sleeve_length = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Sleeve Length (inches)',
            'step': '0.25'
        })
    )
    arm_hole = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Arm Hole (inches)',
            'step': '0.25'
        })
    )
    cuff = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Cuff (inches)',
            'step': '0.25'
        })
    )
    body_length = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Body Length (inches)',
            'step': '0.25'
        })
    )
    inseam = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Inseam (inches)',
            'step': '0.25'
        })
    )
    outseam = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Outseam (inches)',
            'step': '0.25'
        })
    )
    thigh = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Thigh (inches)',
            'step': '0.25'
        })
    )
    knee = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Knee (inches)',
            'step': '0.25'
        })
    )
    hem = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Hem (inches)',
            'step': '0.25'
        })
    )
    rise = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Rise (inches)',
            'step': '0.25'
        })
    )
    neck = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Neck (inches)',
            'step': '0.25'
        })
    )

    class Meta:
        model = Order
        fields = ['customer', 'garment_type', 'fabric', 'quantity', 'total_price', 'due_date', 'special_instructions']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
            }),
            'garment_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'x-on:change': 'updateRequirements()'
            }),
            'fabric': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'min': '1',
                'value': '1',
                'x-on:change': 'updateRequirements()'
            }),
            'total_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Total Price',
                'step': '0.01',
                'min': '0',
                'x-model': 'totalPrice',
                'x-on:input': 'calculateDeposit()'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'type': 'date'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Special Instructions',
                'rows': 3
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        # Collect measurements into a dict
        measurements = {}
        measurement_fields = ['chest', 'waist', 'hips', 'shoulder', 'sleeve_length', 'arm_hole', 'cuff', 'body_length', 'inseam', 'outseam', 'thigh', 'knee', 'hem', 'rise', 'neck']
        for field in measurement_fields:
            value = cleaned_data.get(field)
            if value:
                measurements[field] = float(value)
        cleaned_data['measurements'] = measurements
        return cleaned_data


class OrderQuickCustomerForm(forms.Form):
    """Quick form for creating customer during order"""
    new_customer_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Customer Name'
        })
    )
    new_customer_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Phone Number'
        })
    )


class TailoringTaskUpdateForm(forms.ModelForm):
    """Form for tailors to update task status"""
    class Meta:
        model = TailoringTask
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Notes',
                'rows': 3
            }),
        }


class PaymentForm(forms.ModelForm):
    """Form for recording payments"""
    class Meta:
        model = Payment
        fields = ['amount', 'payment_type', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Amount',
                'step': '0.01',
                'min': '0'
            }),
            'payment_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Notes',
                'rows': 2
            }),
        }


class StockAddForm(forms.Form):
    """Form for adjustment of stock in inventory"""
    ACTION_CHOICES = [
        ('add', 'Add Stock'),
        ('remove', 'Remove Stock'),
    ]
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        initial='add',
        widget=forms.RadioSelect(attrs={'class': 'sr-only'})
    )
    quantity = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500 font-bold text-center',
            'placeholder': 'Quantity',
            'step': 'any',
            'min': '0'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Notes (optional)',
            'rows': 2
        })
    )


class ReworkCreateForm(forms.Form):
    """Form for creating rework request from delivered order"""
    reason = forms.ChoiceField(
        choices=Rework.REASON_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
        })
    )
    reason_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Detailed description of the issue',
            'rows': 4
        })
    )
    charge_type = forms.ChoiceField(
        choices=Rework.CHARGE_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'x-on:change': 'toggleAdditionalCost()'
        })
    )
    additional_cost = forms.DecimalField(
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Additional Cost',
            'step': '0.01',
            'min': '0'
        })
    )
    fabric_used = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
        })
    )
    fabric_meters_used = forms.DecimalField(
        required=False,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Fabric Meters Used',
            'step': '0.01',
            'min': '0'
        })
    )
    assigned_to = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
            'placeholder': 'Additional notes',
            'rows': 3
        })
    )


class ReworkUpdateForm(forms.ModelForm):
    """Form for updating rework status"""
    class Meta:
        model = Rework
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Notes',
                'rows': 3
            }),
        }


class TailorGarmentCommissionForm(forms.ModelForm):
    """Form for managing tailor garment commission rates"""
    class Meta:
        model = TailorGarmentCommission
        fields = ['commission_rate', 'is_active']
        widgets = {
            'commission_rate': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-amber-300 rounded-lg focus:ring-2 focus:ring-amber-500',
                'placeholder': 'Commission Rate (%)',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-amber-600 rounded border-amber-300 focus:ring-amber-500'
            }),
        }
    
    def clean_commission_rate(self):
        rate = self.cleaned_data.get('commission_rate')
        if rate is not None and (rate < 0 or rate > 100):
            raise forms.ValidationError('Commission rate must be between 0 and 100.')
        return rate

