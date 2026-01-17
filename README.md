# El Senior Original Tailoring - Tailoring Management System

A comprehensive web-based tailoring management system built with Django, Tailwind CSS, HTMX, and Alpine.js.

## Features

- **User Management**: Admin and Tailor roles with different access levels
- **Customer Management**: Create, edit, and manage customer profiles
- **Garment Types**: Define garment types with fabric requirements and accessories
- **Inventory Management**: Track fabrics and accessories with auto-deduction
- **Order Management**: Create orders with automatic inventory deduction
- **Tailoring Tasks**: Assign and track tailoring work
- **Payment System**: 50% deposit required, balance tracking
- **Receipt Printing**: Printable receipts for payments and orders
- **SMS Notifications**: Send SMS via Semaphore when orders are ready

## Tech Stack

- **Backend**: Django 4.2+
- **Frontend**: 
  - Tailwind CSS (CDN)
  - HTMX for dynamic interactions
  - Alpine.js for lightweight state management
- **Database**: SQLite (can be changed to PostgreSQL/MySQL)
- **Theme**: Cream & Brown color scheme

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Set up initial data:
   ```bash
   python manage.py setup_initial_data
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Open http://localhost:8000 in your browser

## Default Login Credentials

- **Admin**: username=`admin`, password=`admin123`
- **Tailor**: username=`tailor1`, password=`tailor123`

## SMS Notifications (Semaphore)

To enable SMS notifications:

1. Get an API key from https://semaphore.co/
2. Set the environment variable:
   ```bash
   export SEMAPHORE_API_KEY=your_api_key_here
   ```

## Project Structure

```
tailoring_system/
├── core/                    # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── forms.py            # Django forms
│   ├── admin.py            # Admin configuration
│   └── management/         # Custom management commands
├── templates/              # HTML templates
│   ├── base.html          # Base template with sidebar
│   ├── auth/              # Login templates
│   ├── dashboard/         # Dashboard templates
│   ├── customers/         # Customer management
│   ├── inventory/         # Inventory management
│   ├── garments/          # Garment types
│   ├── orders/            # Order management
│   ├── tasks/             # Tailoring tasks
│   ├── payments/          # Payment & receipts
│   ├── users/             # User management
│   └── reports/           # Reports & analytics
├── static/                # Static files
├── media/                 # User uploads
└── tailoring_system/      # Django project settings
```

## Workflow Summary

1. Admin creates customer
2. Admin creates order (selects customer, garment type, fabric, quantity, measurements)
3. System auto-deducts fabric and accessories from inventory
4. Order auto-assigns to a tailor
5. Tailor marks task as in-progress, then completed
6. Admin approves completed task
7. SMS notification sent to customer
8. Payments tracked with 50% deposit
9. Receipt printed for payments

## License

MIT License
