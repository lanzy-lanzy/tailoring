from django.urls import path
from . import views

urlpatterns = [
    # Landing Page
    path("", views.home_view, name="home"),
    # Authentication
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    # Customer Management
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/create/", views.customer_create, name="customer_create"),
    path("customers/<int:pk>/", views.customer_detail, name="customer_detail"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    path("customers/<int:pk>/delete/", views.customer_delete, name="customer_delete"),
    # Inventory Management
    path("inventory/", views.inventory_dashboard, name="inventory_dashboard"),
    path("inventory/logs/", views.inventory_logs, name="inventory_logs"),
    # Fabric
    path("inventory/fabrics/", views.fabric_list, name="fabric_list"),
    path("inventory/fabrics/create/", views.fabric_create, name="fabric_create"),
    path("inventory/fabrics/<int:pk>/edit/", views.fabric_edit, name="fabric_edit"),
    path(
        "inventory/fabrics/<int:pk>/add-stock/",
        views.fabric_add_stock,
        name="fabric_add_stock",
    ),
    path(
        "inventory/fabrics/<int:pk>/delete/", views.fabric_delete, name="fabric_delete"
    ),
    # Accessory
    path("inventory/accessories/", views.accessory_list, name="accessory_list"),
    path(
        "inventory/accessories/create/", views.accessory_create, name="accessory_create"
    ),
    path(
        "inventory/accessories/<int:pk>/edit/",
        views.accessory_edit,
        name="accessory_edit",
    ),
    path(
        "inventory/accessories/<int:pk>/add-stock/",
        views.accessory_add_stock,
        name="accessory_add_stock",
    ),
    path(
        "inventory/accessories/<int:pk>/delete/",
        views.accessory_delete,
        name="accessory_delete",
    ),
    # Garment Types
    path("garments/", views.garment_type_list, name="garment_type_list"),
    path("garments/create/", views.garment_type_create, name="garment_type_create"),
    path("garments/<int:pk>/", views.garment_type_detail, name="garment_type_detail"),
    path("garments/<int:pk>/edit/", views.garment_type_edit, name="garment_type_edit"),
    path(
        "garments/<int:pk>/delete/",
        views.garment_type_delete,
        name="garment_type_delete",
    ),
    path(
        "garments/<int:pk>/add-accessory/",
        views.garment_type_add_accessory,
        name="garment_type_add_accessory",
    ),
    path(
        "garments/<int:pk>/remove-accessory/<int:accessory_pk>/",
        views.garment_type_remove_accessory,
        name="garment_type_remove_accessory",
    ),
    # Orders
    path("orders/", views.order_list, name="order_list"),
    path("orders/create/", views.order_create, name="order_create"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("orders/<int:pk>/edit/", views.order_edit, name="order_edit"),
    path("orders/<int:pk>/cancel/", views.order_cancel, name="order_cancel"),
    path("orders/<int:pk>/receipt/", views.order_receipt, name="order_receipt"),
    # Tailoring Tasks
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/create/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/", views.task_detail, name="task_detail"),
    path("tasks/<int:pk>/update/", views.task_update_status, name="task_update_status"),
    path("tasks/<int:pk>/notes/", views.task_update_notes, name="task_update_notes"),
    path("tasks/<int:pk>/approve/", views.task_approve, name="task_approve"),
    # Payments
    path("payments/", views.payment_list, name="payment_list"),
    path("orders/<int:order_pk>/payment/", views.payment_create, name="payment_create"),
    path(
        "payments/<int:payment_pk>/receipt/", views.receipt_print, name="receipt_print"
    ),
    path("payments/<int:pk>/receipt/", views.payment_receipt, name="payment_receipt"),
    # Users
    path("users/", views.user_list, name="user_list"),
    path("users/create/", views.user_create, name="user_create"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path(
        "users/<int:pk>/toggle-active/",
        views.user_toggle_active,
        name="user_toggle_active",
    ),
    # Reports
    path("reports/", views.reports_dashboard, name="reports_dashboard"),
    path(
        "reports/export/sales/",
        views.export_sales_report_pdf,
        name="export_sales_report",
    ),
    path(
        "reports/export/inventory/",
        views.export_inventory_report_pdf,
        name="export_inventory_report",
    ),
    path(
        "reports/export/customers/",
        views.export_customer_report_pdf,
        name="export_customer_report",
    ),
    path(
        "reports/export/orders/",
        views.export_orders_report_pdf,
        name="export_orders_report",
    ),
    path(
        "reports/export/payments/",
        views.export_payments_report_pdf,
        name="export_payments_report",
    ),
    path(
        "reports/export/tailor-performance/",
        views.export_tailor_performance_pdf,
        name="export_tailor_performance",
    ),
    # Claims/Pickup
    path("claims/", views.claims_list, name="claims_list"),
    path("claims/<int:pk>/process/", views.process_claim, name="process_claim"),
    path("claims/<int:pk>/receipt/", views.claim_receipt, name="claim_receipt"),
    # Reworks
    path("reworks/", views.rework_list, name="rework_list"),
    path("reworks/orders/<int:order_pk>/create/", views.rework_create, name="rework_create"),
    path("reworks/<int:pk>/", views.rework_detail, name="rework_detail"),
    path("reworks/<int:pk>/update-status/", views.rework_update_status, name="rework_update_status"),
    path("reworks/<int:pk>/assign/", views.rework_assign, name="rework_assign"),
    path("reworks/<int:pk>/add-material/", views.rework_add_material, name="rework_add_material"),
    path("reworks/<int:pk>/remove-material/<int:material_pk>/", views.rework_remove_material, name="rework_remove_material"),
    path("reworks/ready-for-reclaim/", views.reworks_for_reclaim, name="reworks_for_reclaim"),
    path("reworks/reclaim/<int:order_pk>/process/", views.process_reclaim, name="process_reclaim"),
    # API Endpoints (HTMX)
    path(
        "api/garment-requirements/<int:pk>/",
        views.get_garment_requirements,
        name="get_garment_requirements",
    ),
    path(
        "api/check-fabric-stock/",
        views.api_check_fabric_stock,
        name="api_check_fabric_stock",
    ),
    path("api/customer-search/", views.api_customer_search, name="api_customer_search"),
    # Notifications
    path("notifications/", views.notification_list, name="notification_list"),
    path(
        "notifications/<int:pk>/read/",
        views.notification_mark_read,
        name="notification_mark_read",
    ),
    path(
        "notifications/mark-all-read/",
        views.notification_mark_all_read,
        name="notification_mark_all_read",
    ),
    path(
        "notifications/<int:pk>/delete/",
        views.notification_delete,
        name="notification_delete",
    ),
    path(
        "notifications/clear-all/",
        views.notification_clear_all,
        name="notification_clear_all",
    ),
    path(
        "notifications/dropdown/",
        views.notification_dropdown,
        name="notification_dropdown",
    ),
    path("notifications/count/", views.notification_count, name="notification_count"),
    # Commissions
    path("commissions/", views.commission_dashboard, name="commission_dashboard"),
    path(
        "commissions/report/",
        views.tailor_commission_report,
        name="tailor_commission_report",
    ),
    path("commissions/history/", views.commission_history, name="commission_history"),
    path(
        "commissions/admin/",
        views.admin_commission_report,
        name="admin_commission_report",
    ),
    path(
        "commissions/admin/garment-report/",
        views.admin_garment_report,
        name="admin_garment_report",
    ),
    path(
        "commissions/admin/performance-report/",
        views.admin_tailor_performance_report,
        name="admin_tailor_performance_report",
    ),
]
