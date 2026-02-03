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

    # ===============================
    # HEADER
    # ===============================
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(black)
    c.drawString(2 * cm, y, "CAFETERIA E-BILL")

    y -= 0.8 * cm
    c.setFont("Helvetica", 10)
    c.setFillColor(grey)
    c.drawString(2 * cm, y, "Tagore International School – Cafeteria")

    c.setFillColor(black)
    c.drawRightString(width - 2 * cm, y, f"Invoice No: {order_id}")

    y -= 0.6 * cm
    c.setFont("Helvetica", 9)
    c.drawRightString(
        width - 2 * cm,
        y,
        datetime.now().strftime("%d %b %Y, %I:%M %p")
    )

    # ===============================
    # CUSTOMER DETAILS
    # ===============================
    y -= 1.4 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Billed To")

    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, user.get("username", "Student"))

    y -= 0.4 * cm
    c.drawString(2 * cm, y, user.get("email", ""))

    # ===============================
    # ITEMS LIST (NO BOXES)
    # ===============================
    y -= 1.5 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Item")
    c.drawRightString(12 * cm, y, "Qty")
    c.drawRightString(15 * cm, y, "Price")
    c.drawRightString(18 * cm, y, "Amount")

    y -= 0.6 * cm
    c.setFont("Helvetica", 10)

    for item in order_items:
        c.drawString(2 * cm, y, item["name"])
        c.drawRightString(12 * cm, y, str(item["qty"]))
        c.drawRightString(15 * cm, y, f"Rs {item['price']}")
        c.drawRightString(18 * cm, y, f"Rs {item['subtotal']}")
        y -= 0.5 * cm

        if y < 5 * cm:
            c.showPage()
            y = height - 3 * cm
            c.setFont("Helvetica", 10)

    # ===============================
    # TOTAL
    # ===============================
    y -= 1 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(15 * cm, y, "Total Amount")
    c.drawRightString(18 * cm, y, f"Rs {total}")

    # ===============================
    # PAYMENT INFO
    # ===============================
    y -= 2 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Payment Information")

    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, "Payment Mode: Mock Digital Payment")
    y -= 0.4 * cm
    c.drawString(2 * cm, y, "Payment Status: Successful")
    y -= 0.4 * cm
    c.drawString(2 * cm, y, "Transaction Type: Cafeteria Pre-Order")

    # ===============================
    # FOOTER
    # ===============================
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(grey)
    c.drawCentredString(
        width / 2,
        2 * cm,
        "This is a system-generated receipt for academic demonstration purposes."
    )

    c.showPage()
    c.save()

    return file_path

