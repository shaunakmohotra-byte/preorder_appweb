import os
import datetime
import uuid
import json
import smtplib
import threading
from email.message import EmailMessage
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .store import load_json, save_json, ITEMS_FILE, CARTS_FILE, ORDERS_FILE, USERS_FILE

# Initialize Blueprint
bp = Blueprint('main', __name__)

# -----------------------
# EMAIL CONFIGURATION
# -----------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "preorder.apptis@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "bzmf ugav dbcy podq")

# -----------------------
# Helper Functions
# -----------------------

def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    users = load_json(USERS_FILE, [])
    return next((u for u in users if u['id'] == uid), None)

def load_orders():
    data = load_json(ORDERS_FILE, [])
    return data if isinstance(data, list) else []

def save_orders(data):
    save_json(ORDERS_FILE, data)

def send_email_thread(user_email, user_name, order):
    """Background task to send email without making the user wait."""
    try:
        msg = EmailMessage()
        msg["Subject"] = "Cafeteria Order Confirmation"
        msg["From"] = SMTP_EMAIL
        msg["To"] = user_email

        items_text = ""
        for item in order.get("items", []):
            items_text += f"- {item['name']} x {item['qty']} (Rs.{item['price']})\n"

        body = f"Hi {user_name},\n\nYour order {order['id']} is confirmed!\nTotal: Rs.{order['total']}\n\nItems:\n{items_text}\nThank you!"
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {user_email}")
    except Exception as e:
        print(f"Email error: {e}")

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

@bp.route('/cart')
def view_cart():
    user = current_user()
    if not user:
        flash('Login to view cart')
        return redirect(url_for('main.login'))

    carts = load_json(CARTS_FILE, {})
    # SAFE LOAD: Ignore items without IDs to prevent KeyError
    items = {i.get('id'): i for i in load_json(ITEMS_FILE, []) if i.get('id')}
    user_cart = carts.get(user['id'], [])

    cart_details = []
    total = 0
    for c in user_cart:
        it = items.get(c['item_id'])
        if it:
            subtotal = it['price'] * c['qty']
            total += subtotal
            cart_details.append({'item': it, 'qty': c['qty'], 'subtotal': subtotal})

    return render_template('cart.html', cart_details=cart_details, total=total, user=user)

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

    items = {i.get('id'): i for i in load_json(ITEMS_FILE, []) if i.get('id')}
    cart_details = []
    total = 0

    for c in user_cart:
        it = items.get(c['item_id'])
        if it and 'price' in it:
            subtotal = it['price'] * c['qty']
            total += subtotal
            cart_details.append({
                'name': it.get('name', 'Unknown'),
                'price': it['price'],
                'qty': c['qty'],
                'subtotal': subtotal,
                'item_id': c['item_id'] # Needed for order processing
            })

    return render_template("checkout.html", cart_details=cart_details, total=total, user=user)

@bp.route('/pay_now', methods=['POST'])
def pay_now():
    user = current_user()
    if not user: return redirect(url_for('main.login'))

    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(user['id'], [])
    if not user_cart: return redirect(url_for('main.menu'))

    items_map = {i.get('id'): i for i in load_json(ITEMS_FILE, []) if i.get('id')}
    
    order_items = []
    total = 0
    for c in user_cart:
        it = items_map.get(c['item_id'])
        if it:
            total += it['price'] * c['qty']
            order_items.append({'name': it['name'], 'qty': c['qty'], 'price': it['price']})

    order = {
        'id': str(uuid.uuid4())[:8],
        'user_name': user['name'],
        'total': total,
        'items': order_items,
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    # Save order
    orders = load_orders()
    orders.append(order)
    save_orders(orders)

    # Clear cart
    carts[user['id']] = []
    save_json(CARTS_FILE, carts)

    # Send Email in Background
    if user.get('email'):
        threading.Thread(target=send_email_thread, args=(user['email'], user['name'], order)).start()

    flash("Payment Successful!")
    return redirect(url_for('main.menu'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        users = load_json(USERS_FILE, [])
        # Find the user by email
        user = next((u for u in users if u.get('email') == email), None)

        # IMPORTANT: We use 'password_hash' to match your store.py
        if user and check_password_hash(user.get('password_hash', ''), password):
            session.clear()
            session['user_id'] = user['id']
            flash(f"Welcome back, {user.get('name')}!")
            return redirect(url_for('main.menu'))
        else:
            flash("Invalid email or password.")
            return redirect(url_for('main.login'))

    return render_template('login.html')

# (Add your add_to_cart, remove_from_cart, etc. below this...)
# -----------------------
# Cart Management Routes
# -----------------------

@bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user = current_user()
    if not user:
        flash('Please login to add to cart')
        return redirect(url_for('main.login'))

    item_id = request.form.get('item_id')
    qty = int(request.form.get('qty', 1))

    carts = load_json(CARTS_FILE, {})
    user_id = str(user['id'])
    user_cart = carts.get(user_id, [])

    existing = next((c for c in user_cart if c['item_id'] == item_id), None)
    if existing:
        existing['qty'] += qty
    else:
        user_cart.append({'item_id': item_id, 'qty': qty})

    carts[user_id] = user_cart
    save_json(CARTS_FILE, carts)

    flash('Added to cart')
    return redirect(url_for('main.menu'))

@bp.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    user = current_user()
    if not user:
        return redirect(url_for('main.login'))

    item_id = request.form.get('item_id')
    carts = load_json(CARTS_FILE, {})
    user_id = str(user['id'])
    
    user_cart = carts.get(user_id, [])
    user_cart = [c for c in user_cart if c['item_id'] != item_id]
    
    carts[user_id] = user_cart
    save_json(CARTS_FILE, carts)

    flash('Item removed')
    return redirect(url_for('main.view_cart'))

@bp.route('/cart/increase', methods=['POST'])
def cart_increase():
    user = current_user()
    if not user: return redirect(url_for('main.login'))

    item_id = request.form.get('item_id')
    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(str(user['id']), [])

    for c in user_cart:
        if c['item_id'] == item_id:
            c['qty'] += 1
            break

    save_json(CARTS_FILE, carts)
    return redirect(url_for('main.view_cart'))

@bp.route('/cart/decrease', methods=['POST'])
def cart_decrease():
    user = current_user()
    if not user: return redirect(url_for('main.login'))

    item_id = request.form.get('item_id')
    carts = load_json(CARTS_FILE, {})
    user_id = str(user['id'])
    user_cart = carts.get(user_id, [])

    for c in user_cart:
        if c['item_id'] == item_id:
            if c['qty'] > 1:
                c['qty'] -= 1
            else:
                user_cart = [x for x in user_cart if x['item_id'] != item_id]
            break

    carts[user_id] = user_cart
    save_json(CARTS_FILE, carts)
    return redirect(url_for('main.view_cart'))

# -----------------------
# Admin/Cafeteria Routes
# -----------------------

@bp.route('/cafeteria')
def cafeteria():
    orders = load_orders()
    return render_template("cafeteria.html", orders=orders)

@bp.route('/cafeteria/mark_paid/<order_id>', methods=['POST'])
def mark_order_paid(order_id):
    orders = load_orders()
    # Remove the order once delivered/paid
    orders = [o for o in orders if str(o.get('id')) != str(order_id)]
    save_orders(orders)
    flash("Order completed!")
    return redirect(url_for('main.cafeteria'))


# -----------------------
# Authentication Routes
# -----------------------

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        users = load_json(USERS_FILE, [])

        # Check if user already exists
        if any(u['email'] == email for u in users):
            flash('Email already registered')
            return redirect(url_for('main.register'))

        # Create new user with hashed password
        new_user = {
            'id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'password_hash': generate_password_hash(password)
        }

        users.append(new_user)
        save_json(USERS_FILE, users)

        flash('Registration successful! Please login.')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('main.menu'))
