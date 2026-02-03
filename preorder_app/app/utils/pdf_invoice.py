import os
from flask import current_app
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import grey, black
from datetime import datetime


def generate_invoice_pdf(order_id, user, order_items, total):
    invoices_dir = os.path.join(current_app.root_path, "invoices")
    os.makedirs(invoices_dir, exist_ok=True)

    file_path = os.path.join(invoices_dir, f"invoice_{order_id}.pdf")

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 2 * cm

    # =================================================
    # HEADER
    # =================================================
    c.setFont("Helvetica-Bold", 22)
    c.drawString(2 * cm, y, "CAFETERIA E-BILL")
    y -= 1.2 * cm

    logo_path = os.path.join(current_app.root_path, "static", "logo.png")
if os.path.exists(logo_path):
    c.drawImage(logo_path, 2*cm, height-3*cm, width=3*cm, height=3*cm, preserveAspectRatio=True)

    
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, "Tagore International School – Cafeteria")
    c.drawRightString(
        width - 2 * cm,
        y,
        f"Invoice No: {order_id}"
    )

    y -= 0.6 * cm
    c.drawRightString(
        width - 2 * cm,
        y,
        datetime.now().strftime("%d %b %Y, %I:%M %p")
    )

    # Divider
    y -= 0.8 * cm
    c.setStrokeColor(grey)
    c.line(2 * cm, y, width - 2 * cm, y)

    # =================================================
    # CUSTOMER DETAILS
    # =================================================
    y -= 1.2 * cm
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(black)
    c.drawString(2 * cm, y, "Billed To:")

    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, user.get("username", "Student"))
    y -= 0.5 * cm
    c.drawString(2 * cm, y, user.get("email", ""))

    # =================================================
    # ORDER TABLE HEADER
    # =================================================
    y -= 1.4 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Item")
    c.drawRightString(12 * cm, y, "Qty")
    c.drawRightString(15 * cm, y, "Price")
    c.drawRightString(18 * cm, y, "Subtotal")

    y -= 0.3 * cm
    c.line(2 * cm, y, width - 2 * cm, y)

    # =================================================
    # ORDER ITEMS
    # =================================================
    c.setFont("Helvetica", 10)
    y -= 0.7 * cm

    for item in order_items:
        c.drawString(2 * cm, y, item["name"])
        c.drawRightString(12 * cm, y, str(item["qty"]))
        c.drawRightString(15 * cm, y, f"Rs {item['price']}")
        c.drawRightString(18 * cm, y, f"Rs {item['subtotal']}")
        y -= 0.6 * cm

        # Page break safety
        if y < 6 * cm:
            c.showPage()
            y = height - 3 * cm

    # =================================================
    # TOTAL SECTION
    # =================================================
    y -= 0.8 * cm
    c.line(12 * cm, y, width - 2 * cm, y)

    y -= 1 * cm
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(15 * cm, y, "TOTAL AMOUNT:")
    c.drawRightString(18 * cm, y, f"Rs {total}")

    # =================================================
    # PAYMENT INFO (EXTENDS PAGE)
    # =================================================
    y -= 2 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Payment Information")

    y -= 0.7 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, "Payment Mode: Mock Digital Payment")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, "Payment Status: Successful")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, "Transaction Type: Cafeteria Pre-Order")

    # =================================================
    # TERMS & NOTES (FILLS A4)
    # =================================================
    y -= 1.8 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Notes & Terms")

    y -= 0.7 * cm
    c.setFont("Helvetica", 9)
    terms = [
        "• This receipt is system-generated and does not require a signature.",
        "• Items once ordered cannot be cancelled after preparation.",
        "• Payments shown here are part of a prototype cafeteria system.",
        "• This invoice is generated for academic and demonstration purposes.",
        "• Please contact cafeteria staff in case of any discrepancy.",
    ]

    for t in terms:
        c.drawString(2 * cm, y, t)
        y -= 0.5 * cm

    # =================================================
    # FOOTER (BOTTOM OF A4)
    # =================================================
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(grey)
    c.drawCentredString(
        width / 2,
        2 * cm,
        "Thank you for using the Cafeteria Pre-Order System"
    )

    c.showPage()
    c.save()

    return file_path
