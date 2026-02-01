import os
import datetime
import uuid
import json
import smtplib
from email.message import EmailMessage
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .store import load_json, save_json, ITEMS_FILE, CARTS_FILE, ORDERS_FILE, USERS_FILE
from utils.repair import repair_json  # Assuming this exists based on your snippet
import threading  # <--- Add this
import smtplib
from email.message import EmailMessage
# ... (rest of your imports)
bp = Blueprint('main', __name__)

# -----------------------
# EMAIL CONFIGURATION
# -----------------------
# REPLACE these with your actual details or use environment variables
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', 'preorder.apptis@gmail.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'bzmf ugav dbcy podq') 
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# -----------------------
# Helper Functions
# -----------------------

def load_json(path, default):
    """Load JSON with repair capability."""
    try:
        repaired = repair_json(path, type(default))
        return repaired
    except Exception:
        return default

def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    
    users = load_json(USERS_FILE, [])
    return next((u for u in users if u['id'] == uid), None)

def load_orders():
    try:
        data = load_json(ORDERS_FILE, [])
        if isinstance(data, list):
            return data
        else:
            return []     # safety reset
    except:
        return []

def save_orders(data):
    save_json(ORDERS_FILE, data)

def send_order_email(user_email, user_name, order):
    msg = EmailMessage()
    msg["Subject"] = "Cafeteria Order Confirmation"
    msg["From"] = SMTP_EMAIL
    msg["To"] = user_email

    body = f"""
Hi {user_name},

Your order has been successfully placed.

Order ID: {order['id']}
Total Amount: ₹{order['total']}

Items:
"""

    for item in order["items"]:
        body += f"- {item['name']} × {item['qty']} (₹{item['price']})\n"

    body += "\nThank you for ordering!\nCafeteria Team"

    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)

def get_user_by_id(user_id):
    users = load_json(USERS_FILE, [])
    for user in users:
        if user.get("id") == user_id:
            return user
    return None

# -----------------------
# Main Routes
# -----------------------

@bp.route('/')
def index():
    return redirect(url_for('main.menu'))

@bp.route('/menu')
def menu():
    items = load_json(ITEMS_FILE, [])
    return render_template('menu.html', items=items, user=current_user())

@bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user = current_user()
    if not user:
        flash('Please login to add to cart')
        return redirect(url_for('main.login'))

    item_id = request.form['item_id']
    qty = int(request.form.get('qty', 1))

    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(user['id'], [])

    existing = next((c for c in user_cart if c['item_id'] == item_id), None)
    if existing:
        existing['qty'] += qty
    else:
        user_cart.append({'item_id': item_id, 'qty': qty})

    carts[user['id']] = user_cart
    save_json(CARTS_FILE, carts)

    flash('Added to cart')
    return redirect(url_for('main.menu'))

@bp.route('/cart')
def view_cart():
    user = current_user()
    if not user:
        flash('Login to view cart')
        return redirect(url_for('main.login'))

    carts = load_json(CARTS_FILE, {})
    items = {i['id']: i for i in load_json(ITEMS_FILE, [])}
    user_cart = carts.get(user['id'], [])

    cart_details = []
    total = 0

    for c in user_cart:
        it = items.get(c['item_id'])
        if not it:
            continue
        subtotal = it['price'] * c['qty']
        total += subtotal
        cart_details.append({
            'item': it,
            'qty': c['qty'],
            'subtotal': subtotal
        })

    return render_template('cart.html', cart_details=cart_details, total=total, user=user)

@bp.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    user = current_user()
    if not user:
        return redirect(url_for('main.login'))

    item_id = request.form['item_id']

    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(user['id'], [])

    user_cart = [c for c in user_cart if c['item_id'] != item_id]
    carts[user['id']] = user_cart
    save_json(CARTS_FILE, carts)

    flash('Removed')
    return redirect(url_for('main.view_cart'))

@bp.route('/cart/increase', methods=['POST'])
def cart_increase():
    user = current_user()
    if not user:
        return redirect(url_for('main.login'))

    item_id = request.form['item_id']

    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(user['id'], [])

    for c in user_cart:
        if c['item_id'] == item_id:
            c['qty'] += 1
            break

    carts[user['id']] = user_cart
    save_json(CARTS_FILE, carts)

    return redirect(url_for('main.view_cart'))

@bp.route('/cart/decrease', methods=['POST'])
def cart_decrease():
    user = current_user()
    if not user:
        return redirect(url_for('main.login'))

    item_id = request.form['item_id']

    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(user['id'], [])

    for c in user_cart:
        if c['item_id'] == item_id:
            if c['qty'] > 1:
                c['qty'] -= 1
            else:
                # If quantity becomes 0, remove it
                user_cart = [x for x in user_cart if x['item_id'] != item_id]
            break

    carts[user['id']] = user_cart
    save_json(CARTS_FILE, carts)

    return redirect(url_for('main.view_cart'))

@bp.route('/checkout')
def checkout():
    user = current_user()
    if not user:
        flash('Login to checkout')
        return redirect(url_for('main.login'))

    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(user['id'], [])

    if not user_cart:
        flash('Cart empty')
        return redirect(url_for('main.view_cart'))

    # Change this line in the checkout() function:
    items = {i.get('id'): i for i in load_json(ITEMS_FILE, []) if i.get('id')}

    cart_details = []
    total = 0

    for c in user_cart:
        it = items.get(c['item_id'])
        # Check if item exists AND has a price
        if not it or 'price' not in it:
            continue
            
        subtotal = it['price'] * c['qty']
        total += subtotal
        cart_details.append({
            'name': it.get('name', 'Unknown Item'), # Use .get for safety
            'price': it['price'],
            'qty': c['qty'],
            'subtotal': subtotal
        })

    return render_template(
        "checkout.html",
        cart_details=cart_details,
        total=total,
        user=user
    )

def send_order_email(user_email, user_name, order):
    # ... (Keep your existing message setup code) ...
    
    msg.set_content(body)

    print(f"Connecting to SMTP server: {SMTP_SERVER}:{SMTP_PORT}...")
    
    # --- UPDATED CODE BLOCK ---
    try:
        # We add timeout=10 so it doesn't hang forever
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            # server.set_debuglevel(1)  # Uncomment this line if you need deep debugging logs
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
            print(f"Email sent successfully to {user_email}")
            
    except Exception as e:
        # This catch block will now actually work because we set a timeout
        print(f"FAILED to send email: {e}")
        # We do NOT raise the error again, so the user's checkout flow finishes successfully.
    # --------------------------


@bp.route('/cafeteria')
def cafeteria():
    orders = load_orders()
    # HARD SAFETY CHECK
    if not isinstance(orders, list):
        orders = []
    return render_template("cafeteria.html", orders=orders)

@bp.route('/cafeteria/mark_paid/<order_id>', methods=['POST'])
def mark_order_paid(order_id):
    orders = load_orders()
    # If this route is intended to 'finish' an order, you might want to delete it or change status
    # Currently, this logic removes it from the list entirely
    orders = [o for o in orders if o['id'] != order_id]
    save_orders(orders)
    flash("Order marked as delivered")
    return redirect(url_for('main.cafeteria'))
