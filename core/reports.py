"""
ReportLab PDF Report Generation Utilities
Provides styled and visually appealing reports for the tailoring system.
"""

from io import BytesIO
from decimal import Decimal
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    HRFlowable,
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend


# Color scheme matching the tailoring system theme (brown and cream)
COLORS = {
    "brown_dark": colors.HexColor("#3D2917"),
    "brown": colors.HexColor("#6D4A2A"),
    "brown_light": colors.HexColor("#8B5E34"),
    "cream": colors.HexColor("#FFFDF7"),
    "cream_dark": colors.HexColor("#F0E6D8"),
    "gold": colors.HexColor("#C9A97C"),
    "success": colors.HexColor("#10B981"),
    "warning": colors.HexColor("#F59E0B"),
    "danger": colors.HexColor("#EF4444"),
    "info": colors.HexColor("#3B82F6"),
}


def get_custom_styles():
    """Create custom paragraph styles for reports"""
    styles = getSampleStyleSheet()

    # Title style
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=20,
            textColor=COLORS["brown_dark"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        )
    )

    # Subtitle style
    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            fontSize=12,
            spaceAfter=15,
            textColor=COLORS["brown"],
            alignment=TA_CENTER,
            fontName="Helvetica",
        )
    )

    # Section header
    styles.add(
        ParagraphStyle(
            name="SectionHeader",
            parent=styles["Heading2"],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=COLORS["brown_dark"],
            fontName="Helvetica-Bold",
            borderPadding=5,
        )
    )

    # Normal text with custom color
    styles.add(
        ParagraphStyle(
            name="CustomBodyText",
            parent=styles["Normal"],
            fontSize=10,
            textColor=COLORS["brown_dark"],
            fontName="Helvetica",
        )
    )

    # Right aligned text
    styles.add(
        ParagraphStyle(
            name="RightAligned",
            parent=styles["Normal"],
            fontSize=10,
            textColor=COLORS["brown_dark"],
            alignment=TA_RIGHT,
            fontName="Helvetica",
        )
    )

    # Currency style
    styles.add(
        ParagraphStyle(
            name="Currency",
            parent=styles["Normal"],
            fontSize=10,
            textColor=COLORS["brown_dark"],
            alignment=TA_RIGHT,
            fontName="Helvetica-Bold",
        )
    )

    # Footer style
    styles.add(
        ParagraphStyle(
            name="Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=COLORS["brown"],
            alignment=TA_CENTER,
            fontName="Helvetica-Oblique",
        )
    )

    # Summary total style
    styles.add(
        ParagraphStyle(
            name="SummaryTotal",
            parent=styles["Normal"],
            fontSize=14,
            textColor=COLORS["brown_dark"],
            fontName="Helvetica-Bold",
            alignment=TA_RIGHT,
        )
    )

    return styles


def create_header(shop_name="El Senior Original Tailoring"):
    """Create a report header"""
    elements = []
    styles = get_custom_styles()

    # Shop name
    elements.append(Paragraph(shop_name, styles["ReportTitle"]))

    # Decorative line
    elements.append(
        HRFlowable(
            width="100%",
            thickness=2,
            color=COLORS["brown"],
            spaceBefore=5,
            spaceAfter=10,
        )
    )

    return elements


def create_summary_table(data, title=None):
    """Create a styled summary table"""
    styles = get_custom_styles()
    elements = []

    if title:
        elements.append(Paragraph(title, styles["SectionHeader"]))

    table = Table(data, colWidths=[3 * inch, 2 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), COLORS["brown"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("TOPPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), COLORS["cream"]),
                ("TEXTCOLOR", (0, 1), (-1, -1), COLORS["brown_dark"]),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, COLORS["brown_light"]),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLORS["cream"], colors.white]),
                ("TOPPADDING", (0, 1), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
            ]
        )
    )

    elements.append(table)
    return elements


def create_detailed_table(headers, data, col_widths=None):
    """Create a detailed data table with styling"""
    all_data = [headers] + data

    if not col_widths:
        col_widths = [1.5 * inch] * len(headers)

    table = Table(all_data, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                # Header styling
                ("BACKGROUND", (0, 0), (-1, 0), COLORS["brown"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                # Data rows styling
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), COLORS["brown_dark"]),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("ALIGN", (0, 1), (-1, -1), "LEFT"),
                (
                    "ALIGN",
                    (-1, 1),
                    (-1, -1),
                    "RIGHT",
                ),  # Right align last column (usually amounts)
                (
                    "ALIGN",
                    (-2, 1),
                    (-2, -1),
                    "RIGHT",
                ),  # Right align second-to-last column
                # Borders and spacing
                ("GRID", (0, 0), (-1, -1), 0.5, COLORS["brown_light"]),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLORS["cream"]]),
                ("TOPPADDING", (0, 1), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    return table


def create_footer(page_num, total_pages, generated_by=None):
    """Create report footer text"""
    footer_text = f"Page {page_num} of {total_pages}"
    if generated_by:
        footer_text = f"Generated by: {generated_by} | {footer_text}"
    footer_text += (
        f" | Generated on: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}"
    )
    return footer_text


def generate_tailor_commission_report(
    tailor, commissions, start_date, end_date, summary, report_type="weekly"
):
    """Generate a styled PDF commission report for a tailor"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    elements = []
    styles = get_custom_styles()

    # Header
    elements.extend(create_header())

    # Report title
    report_title = f"{report_type.capitalize()} Commission Report"
    elements.append(Paragraph(report_title, styles["ReportTitle"]))

    # Tailor info and date range
    tailor_name = tailor.get_full_name() or tailor.username
    elements.append(
        Paragraph(f"<b>Tailor:</b> {tailor_name}", styles["CustomBodyText"])
    )
    elements.append(
        Paragraph(
            f"<b>Period:</b> {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
            styles["CustomBodyText"],
        )
    )
    elements.append(Spacer(1, 15))

    # Decorative line
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=COLORS["gold"],
            spaceBefore=5,
            spaceAfter=15,
        )
    )

    # Summary section
    summary_data = [
        ["Summary", "Value"],
        ["Total Tasks Completed", str(summary.get("total_tasks", 0))],
        ["Total Order Value", f"PHP {summary.get('total_orders_value', 0):,.2f}"],
        ["Total Commission Earned", f"PHP {summary.get('total_commissions', 0):,.2f}"],
    ]
    elements.extend(create_summary_table(summary_data, "Commission Summary"))
    elements.append(Spacer(1, 20))

    # Detailed commission records
    if commissions:
        elements.append(
            Paragraph("Detailed Commission Records", styles["SectionHeader"])
        )
        elements.append(Spacer(1, 10))

        headers = [
            "Date",
            "Order #",
            "Customer",
            "Garment",
            "Qty",
            "Order Value",
            "Commission",
        ]
        data = []

        for c in commissions:
            data.append(
                [
                    c.earned_date.strftime("%m/%d/%Y"),
                    c.order.order_number if c.order else "N/A",
                    c.customer_name[:20] + "..."
                    if len(c.customer_name) > 20
                    else c.customer_name,
                    c.garment_type[:15] + "..."
                    if len(c.garment_type) > 15
                    else c.garment_type,
                    str(c.quantity),
                    f"PHP {c.order_amount:,.2f}",
                    f"PHP {c.commission_amount:,.2f}",
                ]
            )

        col_widths = [
            0.8 * inch,
            0.9 * inch,
            1.2 * inch,
            1.0 * inch,
            0.4 * inch,
            1.0 * inch,
            0.9 * inch,
        ]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)

        # Total row
        elements.append(Spacer(1, 10))
        total_text = (
            f"<b>Total Commission: PHP {summary.get('total_commissions', 0):,.2f}</b>"
        )
        elements.append(Paragraph(total_text, styles["SummaryTotal"]))
    else:
        elements.append(
            Paragraph(
                "No commission records found for this period.", styles["CustomBodyText"]
            )
        )

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=COLORS["brown"],
            spaceBefore=20,
            spaceAfter=10,
        )
    )
    elements.append(
        Paragraph(
            f"Report generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles["Footer"],
        )
    )
    elements.append(
        Paragraph(
            "El Senior Original Tailoring - Commission Management System",
            styles["Footer"],
        )
    )

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def generate_admin_commission_report(
    commissions,
    tailors_summary,
    start_date,
    end_date,
    report_type="comprehensive",
    generated_by=None,
):
    """Generate a comprehensive admin commission report"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    elements = []
    styles = get_custom_styles()

    # Header
    elements.extend(create_header())

    # Report title
    elements.append(Paragraph("Comprehensive Commission Report", styles["ReportTitle"]))
    elements.append(
        Paragraph(
            f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
            styles["ReportSubtitle"],
        )
    )

    if generated_by:
        elements.append(Paragraph(f"Generated by: {generated_by}", styles["Footer"]))

    elements.append(Spacer(1, 15))

    # Overall summary
    total_commissions = sum(t.get("total_commission", 0) for t in tailors_summary)
    total_orders = sum(t.get("task_count", 0) for t in tailors_summary)
    total_order_value = sum(t.get("total_order_value", 0) for t in tailors_summary)

    overall_summary = [
        ["Metric", "Value"],
        ["Total Tailors with Commissions", str(len(tailors_summary))],
        ["Total Tasks Completed", str(total_orders)],
        ["Total Order Value", f"PHP {total_order_value:,.2f}"],
        ["Total Commissions Paid", f"PHP {total_commissions:,.2f}"],
    ]

    if total_order_value > 0:
        avg_rate = (total_commissions / total_order_value) * 100
        overall_summary.append(["Average Commission Rate", f"{avg_rate:.2f}%"])

    elements.extend(create_summary_table(overall_summary, "Overall Summary"))
    elements.append(Spacer(1, 25))

    # Per-tailor breakdown
    elements.append(Paragraph("Commission by Tailor", styles["SectionHeader"]))
    elements.append(Spacer(1, 10))

    if tailors_summary:
        headers = ["Tailor Name", "Tasks", "Order Value", "Commission", "Avg Rate"]
        data = []

        for t in tailors_summary:
            avg_rate = 0
            if t.get("total_order_value", 0) > 0:
                avg_rate = (
                    t.get("total_commission", 0) / t.get("total_order_value", 1)
                ) * 100

            data.append(
                [
                    t.get("tailor_name", "Unknown"),
                    str(t.get("task_count", 0)),
                    f"PHP {t.get('total_order_value', 0):,.2f}",
                    f"PHP {t.get('total_commission', 0):,.2f}",
                    f"{avg_rate:.1f}%",
                ]
            )

        col_widths = [2 * inch, 0.8 * inch, 1.3 * inch, 1.3 * inch, 0.8 * inch]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)
    else:
        elements.append(
            Paragraph(
                "No commission data found for this period.", styles["CustomBodyText"]
            )
        )

    elements.append(Spacer(1, 25))

    # Detailed transactions (if provided)
    if commissions and len(commissions) > 0:
        elements.append(PageBreak())
        elements.append(
            Paragraph("Detailed Commission Transactions", styles["SectionHeader"])
        )
        elements.append(Spacer(1, 10))

        headers = [
            "Date",
            "Order #",
            "Tailor",
            "Customer",
            "Garment",
            "Amount",
            "Commission",
        ]
        data = []

        for c in commissions[:100]:  # Limit to 100 records for PDF performance
            tailor_name = (
                c.tailor.get_full_name() or c.tailor.username if c.tailor else "N/A"
            )
            data.append(
                [
                    c.earned_date.strftime("%m/%d/%y"),
                    c.order.order_number[:12] if c.order else "N/A",
                    tailor_name[:15] + "..." if len(tailor_name) > 15 else tailor_name,
                    c.customer_name[:12] + "..."
                    if len(c.customer_name) > 12
                    else c.customer_name,
                    c.garment_type[:10] + "..."
                    if len(c.garment_type) > 10
                    else c.garment_type,
                    f"P{c.order_amount:,.0f}",
                    f"P{c.commission_amount:,.0f}",
                ]
            )

        col_widths = [
            0.7 * inch,
            0.85 * inch,
            1.0 * inch,
            0.9 * inch,
            0.8 * inch,
            0.8 * inch,
            0.8 * inch,
        ]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)

        if len(commissions) > 100:
            elements.append(Spacer(1, 10))
            elements.append(
                Paragraph(
                    f"Showing 100 of {len(commissions)} records. Export to see all records.",
                    styles["Footer"],
                )
            )

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=COLORS["brown"],
            spaceBefore=20,
            spaceAfter=10,
        )
    )
    elements.append(
        Paragraph(
            f"Report generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles["Footer"],
        )
    )
    elements.append(
        Paragraph(
            "El Senior Original Tailoring - Commission Management System",
            styles["Footer"],
        )
    )

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def generate_garment_production_report(
    garment_stats, start_date, end_date, generated_by=None
):
    """Generate garment production report with commission data"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    elements = []
    styles = get_custom_styles()

    # Header
    elements.extend(create_header())

    # Report title
    elements.append(
        Paragraph("Garment Production & Commission Report", styles["ReportTitle"])
    )
    elements.append(
        Paragraph(
            f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
            styles["ReportSubtitle"],
        )
    )
    elements.append(Spacer(1, 20))

    if garment_stats:
        headers = ["Garment Type", "Quantity", "Revenue", "Commissions Paid"]
        data = []

        total_qty = 0
        total_revenue = 0
        total_commission = 0

        for stat in garment_stats:
            data.append(
                [
                    stat.get("garment_type", "Unknown"),
                    str(stat.get("quantity", 0)),
                    f"PHP {stat.get('revenue', 0):,.2f}",
                    f"PHP {stat.get('commission', 0):,.2f}",
                ]
            )
            total_qty += stat.get("quantity", 0)
            total_revenue += stat.get("revenue", 0)
            total_commission += stat.get("commission", 0)

        # Add totals row
        data.append(
            [
                "TOTAL",
                str(total_qty),
                f"PHP {total_revenue:,.2f}",
                f"PHP {total_commission:,.2f}",
            ]
        )

        col_widths = [2.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch]
        table = create_detailed_table(headers, data, col_widths)

        # Style the totals row
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, -1), (-1, -1), COLORS["brown_light"]),
                    ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ]
            )
        )

        elements.append(table)
    else:
        elements.append(
            Paragraph(
                "No production data found for this period.", styles["CustomBodyText"]
            )
        )

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=COLORS["brown"],
            spaceBefore=20,
            spaceAfter=10,
        )
    )
    elements.append(
        Paragraph(
            f"Report generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles["Footer"],
        )
    )

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def generate_tailor_performance_report(
    tailors_data, start_date, end_date, generated_by=None
):
    """Generate comprehensive tailor performance report"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    elements = []
    styles = get_custom_styles()

    # Header
    elements.extend(create_header())

    # Report title
    elements.append(Paragraph("Tailor Performance Report", styles["ReportTitle"]))
    elements.append(
        Paragraph(
            f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
            styles["ReportSubtitle"],
        )
    )
    elements.append(Spacer(1, 20))

    if tailors_data:
        headers = [
            "Tailor",
            "Tasks Completed",
            "Avg Completion Time",
            "Revenue Generated",
            "Commission Earned",
        ]
        data = []

        for t in tailors_data:
            data.append(
                [
                    t.get("name", "Unknown"),
                    str(t.get("tasks_completed", 0)),
                    t.get("avg_completion_time", "N/A"),
                    f"PHP {t.get('revenue', 0):,.2f}",
                    f"PHP {t.get('commission', 0):,.2f}",
                ]
            )

        col_widths = [1.5 * inch, 1.0 * inch, 1.2 * inch, 1.3 * inch, 1.2 * inch]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)
    else:
        elements.append(
            Paragraph(
                "No performance data found for this period.", styles["CustomBodyText"]
            )
        )

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=COLORS["brown"],
            spaceBefore=20,
            spaceAfter=10,
        )
    )
    elements.append(
        Paragraph(
            f"Report generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles["Footer"],
        )
    )

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def generate_sales_analytics_report(
    stats,
    daily_orders,
    popular_garments,
    top_customers,
    order_status_breakdown,
    start_date,
    end_date,
    generated_by=None,
):
    """Generate comprehensive sales analytics PDF report"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    elements = []
    styles = get_custom_styles()

    # Header
    elements.extend(create_header())

    # Report title
    elements.append(Paragraph("Sales Analytics Report", styles["ReportTitle"]))
    elements.append(
        Paragraph(
            f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
            styles["ReportSubtitle"],
        )
    )
    if generated_by:
        elements.append(Paragraph(f"Generated by: {generated_by}", styles["Footer"]))
    elements.append(Spacer(1, 20))

    # Financial Summary Section
    summary_data = [
        ["Financial Metric", "Value"],
        ["Total Revenue", f"PHP {float(stats.get('total_revenue', 0)):,.2f}"],
        ["Payments Collected", f"PHP {float(stats.get('payments_collected', 0)):,.2f}"],
        [
            "Outstanding Balance",
            f"PHP {float(stats.get('outstanding_balance', 0)):,.2f}",
        ],
        ["Average Order Value", f"PHP {float(stats.get('avg_order_value', 0)):,.2f}"],
        ["Total Orders", str(stats.get("order_count", 0))],
        ["Completed Orders", str(stats.get("completed_orders", 0))],
        ["Pending Orders", str(stats.get("pending_orders", 0))],
    ]
    elements.extend(create_summary_table(summary_data, "Financial Summary"))
    elements.append(Spacer(1, 25))

    # Order Status Breakdown
    elements.append(Paragraph("Order Status Breakdown", styles["SectionHeader"]))
    elements.append(Spacer(1, 10))

    if order_status_breakdown:
        headers = ["Status", "Count", "Percentage"]
        data = []
        for status in order_status_breakdown:
            data.append(
                [
                    status.get("status", "Unknown").replace("_", " ").title(),
                    str(status.get("count", 0)),
                    f"{status.get('percentage', 0):.1f}%",
                ]
            )
        col_widths = [2.5 * inch, 1.5 * inch, 1.5 * inch]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)
    else:
        elements.append(Paragraph("No order data available.", styles["CustomBodyText"]))

    elements.append(Spacer(1, 25))

    # Popular Garments
    elements.append(Paragraph("Popular Garment Types", styles["SectionHeader"]))
    elements.append(Spacer(1, 10))

    if popular_garments:
        headers = ["Rank", "Garment Type", "Orders", "Revenue"]
        data = []
        for i, garment in enumerate(popular_garments, 1):
            data.append(
                [
                    str(i),
                    garment.get("name", "Unknown"),
                    str(garment.get("order_count", 0)),
                    f"PHP {float(garment.get('total_revenue', 0)):,.2f}",
                ]
            )
        col_widths = [0.6 * inch, 2.5 * inch, 1.0 * inch, 1.5 * inch]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)
    else:
        elements.append(
            Paragraph("No garment data available.", styles["CustomBodyText"])
        )

    elements.append(PageBreak())
    elements.extend(create_header())

    # Top Customers
    elements.append(Paragraph("Top Customers by Spending", styles["SectionHeader"]))
    elements.append(Spacer(1, 10))

    if top_customers:
        headers = ["Rank", "Customer Name", "Orders", "Total Spent"]
        data = []
        for i, customer in enumerate(top_customers, 1):
            data.append(
                [
                    str(i),
                    customer.get("name", "Unknown"),
                    str(customer.get("order_count", 0)),
                    f"PHP {float(customer.get('total_spent', 0)):,.2f}",
                ]
            )
        col_widths = [0.6 * inch, 2.5 * inch, 1.0 * inch, 1.5 * inch]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)
    else:
        elements.append(
            Paragraph("No customer data available.", styles["CustomBodyText"])
        )

    elements.append(Spacer(1, 25))

    # Daily Orders Trend
    elements.append(Paragraph("Daily Orders Trend", styles["SectionHeader"]))
    elements.append(Spacer(1, 10))

    if daily_orders:
        headers = ["Date", "Orders"]
        data = []
        for day in daily_orders[-14:]:  # Last 14 days
            data.append(
                [
                    day.get("date").strftime("%b %d, %Y")
                    if hasattr(day.get("date"), "strftime")
                    else str(day.get("date")),
                    str(day.get("count", 0)),
                ]
            )
        col_widths = [3 * inch, 2 * inch]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=COLORS["brown"],
            spaceBefore=20,
            spaceAfter=10,
        )
    )
    elements.append(
        Paragraph(
            f"Report generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles["Footer"],
        )
    )
    elements.append(
        Paragraph(
            "El Senior Original Tailoring - Sales Analytics Report", styles["Footer"]
        )
    )

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def generate_inventory_report(
    fabrics,
    accessories,
    low_stock_fabrics,
    low_stock_accessories,
    inventory_logs,
    start_date,
    end_date,
    generated_by=None,
):
    """Generate comprehensive inventory PDF report"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    elements = []
    styles = get_custom_styles()

    # Header
    elements.extend(create_header())

    # Report title
    elements.append(Paragraph("Inventory Report", styles["ReportTitle"]))
    elements.append(
        Paragraph(f"As of {end_date.strftime('%B %d, %Y')}", styles["ReportSubtitle"])
    )
    if generated_by:
        elements.append(Paragraph(f"Generated by: {generated_by}", styles["Footer"]))
    elements.append(Spacer(1, 20))

    # Summary Statistics
    total_fabric_value = sum(f.stock_meters * f.price_per_meter for f in fabrics)
    total_accessory_value = sum(
        a.stock_quantity * a.price_per_unit for a in accessories
    )

    summary_data = [
        ["Inventory Metric", "Value"],
        ["Total Fabric Types", str(fabrics.count())],
        ["Total Fabric Stock Value", f"PHP {float(total_fabric_value):,.2f}"],
        ["Total Accessory Types", str(accessories.count())],
        ["Total Accessory Stock Value", f"PHP {float(total_accessory_value):,.2f}"],
        [
            "Total Inventory Value",
            f"PHP {float(total_fabric_value + total_accessory_value):,.2f}",
        ],
        ["Low Stock Fabrics", str(len(low_stock_fabrics))],
        ["Low Stock Accessories", str(len(low_stock_accessories))],
    ]
    elements.extend(create_summary_table(summary_data, "Inventory Summary"))
    elements.append(Spacer(1, 25))

    # Low Stock Alerts
    if low_stock_fabrics or low_stock_accessories:
        elements.append(Paragraph("Low Stock Alerts", styles["SectionHeader"]))
        elements.append(Spacer(1, 10))

        if low_stock_fabrics:
            elements.append(Paragraph("Fabrics Running Low:", styles["CustomBodyText"]))
            headers = ["Fabric Name", "Color", "Current Stock", "Unit Price"]
            data = []
            for fabric in low_stock_fabrics:
                data.append(
                    [
                        fabric.name,
                        fabric.color or "N/A",
                        f"{float(fabric.stock_meters):.2f} m",
                        f"PHP {float(fabric.price_per_meter):,.2f}/m",
                    ]
                )
            col_widths = [2 * inch, 1.2 * inch, 1.3 * inch, 1.5 * inch]
            table = create_detailed_table(headers, data, col_widths)
            elements.append(table)
            elements.append(Spacer(1, 15))

        if low_stock_accessories:
            elements.append(
                Paragraph("Accessories Running Low:", styles["CustomBodyText"])
            )
            headers = ["Accessory Name", "Unit", "Current Stock", "Unit Price"]
            data = []
            for acc in low_stock_accessories:
                data.append(
                    [
                        acc.name,
                        acc.unit,
                        f"{float(acc.stock_quantity):.2f}",
                        f"PHP {float(acc.price_per_unit):,.2f}",
                    ]
                )
            col_widths = [2 * inch, 1.2 * inch, 1.3 * inch, 1.5 * inch]
            table = create_detailed_table(headers, data, col_widths)
            elements.append(table)

        elements.append(Spacer(1, 25))

    # Full Fabric Inventory
    elements.append(PageBreak())
    elements.extend(create_header())
    elements.append(Paragraph("Full Fabric Inventory", styles["SectionHeader"]))
    elements.append(Spacer(1, 10))

    if fabrics:
        headers = ["Name", "Color", "Stock (m)", "Price/m", "Total Value"]
        data = []
        for fabric in fabrics:
            total_val = fabric.stock_meters * fabric.price_per_meter
            data.append(
                [
                    fabric.name[:25] + "..." if len(fabric.name) > 25 else fabric.name,
                    fabric.color[:15] + "..."
                    if len(fabric.color) > 15
                    else fabric.color or "N/A",
                    f"{float(fabric.stock_meters):.2f}",
                    f"P{float(fabric.price_per_meter):,.0f}",
                    f"P{float(total_val):,.0f}",
                ]
            )
        col_widths = [1.8 * inch, 1.0 * inch, 0.9 * inch, 0.9 * inch, 1.0 * inch]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)
    else:
        elements.append(
            Paragraph("No fabric inventory data.", styles["CustomBodyText"])
        )

    elements.append(Spacer(1, 25))

    # Full Accessory Inventory
    elements.append(Paragraph("Full Accessory Inventory", styles["SectionHeader"]))
    elements.append(Spacer(1, 10))

    if accessories:
        headers = ["Name", "Unit", "Stock", "Price", "Total Value"]
        data = []
        for acc in accessories:
            total_val = acc.stock_quantity * acc.price_per_unit
            data.append(
                [
                    acc.name[:25] + "..." if len(acc.name) > 25 else acc.name,
                    acc.unit,
                    f"{float(acc.stock_quantity):.2f}",
                    f"P{float(acc.price_per_unit):,.0f}",
                    f"P{float(total_val):,.0f}",
                ]
            )
        col_widths = [1.8 * inch, 0.8 * inch, 1.0 * inch, 0.9 * inch, 1.0 * inch]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)
    else:
        elements.append(
            Paragraph("No accessory inventory data.", styles["CustomBodyText"])
        )

    # Recent Inventory Logs
    if inventory_logs:
        elements.append(PageBreak())
        elements.extend(create_header())
        elements.append(
            Paragraph("Recent Inventory Transactions", styles["SectionHeader"])
        )
        elements.append(Spacer(1, 10))

        headers = ["Date", "Item", "Action", "Qty", "Prev Stock", "New Stock"]
        data = []
        for log in inventory_logs[:50]:
            item_name = ""
            if log.fabric:
                item_name = f"[F] {log.fabric.name[:15]}"
            elif log.accessory:
                item_name = f"[A] {log.accessory.name[:15]}"
            data.append(
                [
                    log.created_at.strftime("%m/%d/%y"),
                    item_name,
                    log.action.replace("_", " ").title(),
                    f"{float(log.quantity):.2f}",
                    f"{float(log.previous_stock):.2f}",
                    f"{float(log.new_stock):.2f}",
                ]
            )
        col_widths = [
            0.75 * inch,
            1.3 * inch,
            1.0 * inch,
            0.7 * inch,
            0.9 * inch,
            0.9 * inch,
        ]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=COLORS["brown"],
            spaceBefore=20,
            spaceAfter=10,
        )
    )
    elements.append(
        Paragraph(
            f"Report generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles["Footer"],
        )
    )
    elements.append(
        Paragraph(
            "El Senior Original Tailoring - Inventory Management Report",
            styles["Footer"],
        )
    )

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def generate_customer_report(
    customers_data,
    start_date,
    end_date,
    total_customers,
    new_customers,
    top_spenders,
    generated_by=None,
):
    """Generate comprehensive customer analytics PDF report"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    elements = []
    styles = get_custom_styles()

    # Header
    elements.extend(create_header())

    # Report title
    elements.append(Paragraph("Customer Analytics Report", styles["ReportTitle"]))
    elements.append(
        Paragraph(
            f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
            styles["ReportSubtitle"],
        )
    )
    if generated_by:
        elements.append(Paragraph(f"Generated by: {generated_by}", styles["Footer"]))
    elements.append(Spacer(1, 20))

    # Summary Statistics
    summary_data = [
        ["Customer Metric", "Value"],
        ["Total Customers", str(total_customers)],
        ["New Customers (in period)", str(new_customers)],
        [
            "Total Revenue from Top 10",
            f"PHP {sum(c.get('total_spent', 0) for c in top_spenders):,.2f}",
        ],
    ]
    elements.extend(create_summary_table(summary_data, "Customer Summary"))
    elements.append(Spacer(1, 25))

    # Top Spenders
    elements.append(Paragraph("Top Spending Customers", styles["SectionHeader"]))
    elements.append(Spacer(1, 10))

    if top_spenders:
        headers = ["Rank", "Customer Name", "Contact", "Orders", "Total Spent"]
        data = []
        for i, customer in enumerate(top_spenders, 1):
            data.append(
                [
                    str(i),
                    customer.get("name", "Unknown")[:20],
                    customer.get("contact", "N/A")[:15],
                    str(customer.get("order_count", 0)),
                    f"PHP {float(customer.get('total_spent', 0)):,.2f}",
                ]
            )
        col_widths = [0.5 * inch, 1.5 * inch, 1.2 * inch, 0.8 * inch, 1.3 * inch]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)
    else:
        elements.append(
            Paragraph("No customer data available.", styles["CustomBodyText"])
        )

    elements.append(Spacer(1, 25))

    # All Customers with Activity
    if customers_data:
        elements.append(
            Paragraph("Customers with Orders in Period", styles["SectionHeader"])
        )
        elements.append(Spacer(1, 10))

        headers = ["Customer Name", "Contact", "Orders", "Total Spent", "Last Order"]
        data = []
        for customer in customers_data[:50]:  # Limit to 50 for PDF
            data.append(
                [
                    customer.get("name", "Unknown")[:20],
                    customer.get("contact", "N/A")[:12],
                    str(customer.get("order_count", 0)),
                    f"PHP {float(customer.get('total_spent', 0)):,.2f}",
                    customer.get("last_order", "N/A"),
                ]
            )
        col_widths = [1.4 * inch, 1.0 * inch, 0.7 * inch, 1.2 * inch, 1.0 * inch]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)

        if len(customers_data) > 50:
            elements.append(Spacer(1, 10))
            elements.append(
                Paragraph(
                    f"Showing 50 of {len(customers_data)} customers.", styles["Footer"]
                )
            )

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=COLORS["brown"],
            spaceBefore=20,
            spaceAfter=10,
        )
    )
    elements.append(
        Paragraph(
            f"Report generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles["Footer"],
        )
    )
    elements.append(
        Paragraph(
            "El Senior Original Tailoring - Customer Analytics Report", styles["Footer"]
        )
    )

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def generate_orders_report(orders, stats, start_date, end_date, generated_by=None):
    """Generate comprehensive orders PDF report"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    elements = []
    styles = get_custom_styles()

    # Header
    elements.extend(create_header())

    # Report title
    elements.append(Paragraph("Orders Report", styles["ReportTitle"]))
    elements.append(
        Paragraph(
            f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
            styles["ReportSubtitle"],
        )
    )
    if generated_by:
        elements.append(Paragraph(f"Generated by: {generated_by}", styles["Footer"]))
    elements.append(Spacer(1, 20))

    # Summary Statistics
    summary_data = [
        ["Order Metric", "Value"],
        ["Total Orders", str(stats.get("total_orders", 0))],
        ["Total Value", f"PHP {float(stats.get('total_value', 0)):,.2f}"],
        ["Completed Orders", str(stats.get("completed", 0))],
        ["In Progress", str(stats.get("in_progress", 0))],
        ["Pending", str(stats.get("pending", 0))],
        ["Claimed", str(stats.get("delivered", 0))],
        ["Cancelled", str(stats.get("cancelled", 0))],
    ]
    elements.extend(create_summary_table(summary_data, "Orders Summary"))
    elements.append(Spacer(1, 25))

    # Order Details
    elements.append(Paragraph("Order Details", styles["SectionHeader"]))
    elements.append(Spacer(1, 10))

    if orders:
        headers = ["Order #", "Date", "Customer", "Garment", "Qty", "Status", "Total"]
        data = []
        for order in orders[:100]:  # Limit to 100 orders
            data.append(
                [
                    order.order_number[:12]
                    if len(order.order_number) > 12
                    else order.order_number,
                    order.order_date.strftime("%m/%d/%y"),
                    order.customer.name[:12] + "..."
                    if len(order.customer.name) > 12
                    else order.customer.name,
                    order.garment_type.name[:10] + "..."
                    if len(order.garment_type.name) > 10
                    else order.garment_type.name,
                    str(order.quantity),
                    order.status.replace("_", " ").title()[:10],
                    f"P{float(order.total_price):,.0f}",
                ]
            )
        col_widths = [
            1.0 * inch,
            0.7 * inch,
            1.0 * inch,
            0.9 * inch,
            0.4 * inch,
            0.8 * inch,
            0.8 * inch,
        ]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)

        if len(orders) > 100:
            elements.append(Spacer(1, 10))
            elements.append(
                Paragraph(f"Showing 100 of {len(orders)} orders.", styles["Footer"])
            )
    else:
        elements.append(
            Paragraph("No orders found in this period.", styles["CustomBodyText"])
        )

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=COLORS["brown"],
            spaceBefore=20,
            spaceAfter=10,
        )
    )
    elements.append(
        Paragraph(
            f"Report generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles["Footer"],
        )
    )
    elements.append(
        Paragraph("El Senior Original Tailoring - Orders Report", styles["Footer"])
    )

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def generate_payments_report(payments, stats, start_date, end_date, generated_by=None):
    """Generate comprehensive payments PDF report"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    elements = []
    styles = get_custom_styles()

    # Header
    elements.extend(create_header())

    # Report title
    elements.append(Paragraph("Payments Report", styles["ReportTitle"]))
    elements.append(
        Paragraph(
            f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
            styles["ReportSubtitle"],
        )
    )
    if generated_by:
        elements.append(Paragraph(f"Generated by: {generated_by}", styles["Footer"]))
    elements.append(Spacer(1, 20))

    # Summary Statistics
    summary_data = [
        ["Payment Metric", "Value"],
        ["Total Payments", str(stats.get("total_payments", 0))],
        ["Total Amount Collected", f"PHP {float(stats.get('total_amount', 0)):,.2f}"],
        ["Deposit Payments", str(stats.get("deposits", 0))],
        ["Balance Payments", str(stats.get("balance_payments", 0))],
        ["Cash Payments", str(stats.get("cash", 0))],
        ["GCash Payments", str(stats.get("gcash", 0))],
        ["Bank Transfer", str(stats.get("bank_transfer", 0))],
    ]
    elements.extend(create_summary_table(summary_data, "Payments Summary"))
    elements.append(Spacer(1, 25))

    # Payment Details
    elements.append(Paragraph("Payment Transactions", styles["SectionHeader"]))
    elements.append(Spacer(1, 10))

    if payments:
        headers = [
            "Payment #",
            "Date",
            "Order #",
            "Customer",
            "Type",
            "Method",
            "Amount",
        ]
        data = []
        for payment in payments[:100]:  # Limit to 100
            data.append(
                [
                    payment.payment_number[:10]
                    if len(payment.payment_number) > 10
                    else payment.payment_number,
                    payment.payment_date.strftime("%m/%d/%y"),
                    payment.order.order_number[:8]
                    if len(payment.order.order_number) > 8
                    else payment.order.order_number,
                    payment.order.customer.name[:10] + ".."
                    if len(payment.order.customer.name) > 10
                    else payment.order.customer.name,
                    payment.payment_type.title()[:7],
                    payment.payment_method.replace("_", " ").title()[:8],
                    f"P{float(payment.amount):,.0f}",
                ]
            )
        col_widths = [
            0.9 * inch,
            0.65 * inch,
            0.7 * inch,
            0.9 * inch,
            0.6 * inch,
            0.7 * inch,
            0.75 * inch,
        ]
        table = create_detailed_table(headers, data, col_widths)
        elements.append(table)

        if len(payments) > 100:
            elements.append(Spacer(1, 10))
            elements.append(
                Paragraph(f"Showing 100 of {len(payments)} payments.", styles["Footer"])
            )
    else:
        elements.append(
            Paragraph("No payments found in this period.", styles["CustomBodyText"])
        )

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=COLORS["brown"],
            spaceBefore=20,
            spaceAfter=10,
        )
    )
    elements.append(
        Paragraph(
            f"Report generated on {timezone.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles["Footer"],
        )
    )
    elements.append(
        Paragraph("El Senior Original Tailoring - Payments Report", styles["Footer"])
    )

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf
