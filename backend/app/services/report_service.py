"""Report generation service (PDF, CSV, Excel)."""

from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from openpyxl import Workbook

from app.models.reconciliation import Reconciliation
from app.models.discrepancy import Discrepancy


def generate_pdf_report(reconciliation: Reconciliation, discrepancies: list) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle("CustomTitle", parent=styles["Heading1"], fontSize=18, spaceAfter=30)
    elements.append(Paragraph(f"Reconciliation Report: {reconciliation.name}", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Total Items: {reconciliation.total_items}", styles["Normal"]))
    elements.append(Paragraph(f"Matched: {reconciliation.matched_items}", styles["Normal"]))
    elements.append(Paragraph(f"Discrepancies: {reconciliation.discrepancies_found}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    if discrepancies:
        elements.append(Paragraph("Discrepancies Found", styles["Heading2"]))
        header = [["SKU", "Item", "System Qty", "Source Qty", "Difference", "Type", "Severity", "Explanation"]]
        rows = [
            [
                d.item_sku or "-",
                d.item_name,
                str(d.system_quantity),
                str(d.source_quantity),
                str(d.quantity_difference),
                d.discrepancy_type,
                d.severity.upper(),
                d.explanation[:100] + "..." if len(d.explanation) > 100 else d.explanation,
            ]
            for d in discrepancies
        ]
        t = Table(header + rows)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), (0.5, 0.5, 0.5)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), (1, 1, 1)),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [(0.95, 0.95, 0.95), (1, 1, 1)]),
                    ("GRID", (0, 0), (-1, -1), 0.5, (0.5, 0.5, 0.5)),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(t)
    doc.build(elements)
    return buf.getvalue()


def generate_csv_report(discrepancies: list) -> bytes:
    buf = BytesIO()
    buf.write("item_name,sku,system_quantity,source_quantity,difference,type,severity,explanation,resolved\n".encode())
    for d in discrepancies:
        line = f"{d.item_name},{d.item_sku or ''},{d.system_quantity},{d.source_quantity},{d.quantity_difference},{d.discrepancy_type},{d.severity},{d.explanation},{d.resolved}\n"
        buf.write(line.encode())
    buf.seek(0)
    return buf.getvalue()


def generate_excel_report(reconciliation: Reconciliation, discrepancies: list) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Discrepancies"
    ws.append(["Item Name", "SKU", "System Qty", "Source Qty", "Difference", "Type", "Severity", "Explanation", "Resolved"])
    for d in discrepancies:
        ws.append([
            d.item_name, d.item_sku or "", d.system_quantity, d.source_quantity,
            d.quantity_difference, d.discrepancy_type, d.severity, d.explanation, d.resolved,
        ])
    ws2 = wb.create_sheet("Summary")
    ws2.append(["Field", "Value"])
    ws2.append(["Name", reconciliation.name])
    ws2.append(["Total Items", reconciliation.total_items])
    ws2.append(["Matched", reconciliation.matched_items])
    ws2.append(["Discrepancies", reconciliation.discrepancies_found])
    ws2.append(["Status", reconciliation.status])
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()
