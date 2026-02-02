from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os
from datetime import datetime

def generate_invoice_pdf(order_id, user, order_items, total):
    invoices_dir = "invoices"
    os.makedirs(invoices_dir, exist_ok=True)

    file_path = f"{invoices_dir}/invoice_{order_id}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 2 * cm

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "E-BILL / RECEIPT")
    y -= 1.2 * cm

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Order ID: {order_id}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Customer: {user['username']}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Email: {user['email']}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    y -= 1.2 * cm

    # Table header
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Item")
    c.drawString(11 * cm, y, "Qty")
    y -= 0.5 * cm

    c.setFont("Helvetica", 10)

    for item in order_items:
        c.drawString(2 * cm, y, item["name"])
        c.drawString(11 * cm, y, str(item["qty"]))
        y -= 0.5 * cm

    y -= 0.8 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, f"Total Amount: ₹{total}")

    c.showPage()
    c.save()

    return file_path
