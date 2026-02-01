import os, datetime, uuid, threading
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .store import load_json, save_json, ITEMS_FILE, CARTS_FILE, ORDERS_FILE, USERS_FILE

bp = Blueprint('main', __name__)

def current_user():
    uid = session.get('user_id')
    if not uid: return None
    users = load_json(USERS_FILE, [])
    return next((u for u in users if u.get('id') == uid), None)

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
        flash('Please login to view cart')
        return redirect(url_for('auth.login'))

    carts = load_json(CARTS_FILE, {})
    items_map = {i.get('id'): i for i in load_json(ITEMS_FILE, []) if i.get('id')}
    user_cart = carts.get(str(user['id']), [])

    cart_details = []
    total = 0
    for c in user_cart:
        it = items_map.get(c['item_id'])
        if it:
            subtotal = it['price'] * c['qty']
            total += subtotal
            cart_details.append({'item': it, 'qty': c['qty'], 'subtotal': subtotal})

    return render_template('cart.html', cart_details=cart_details, total=total, user=user)

@bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user = current_user()
    if not user:
        flash('Please login first')
        return redirect(url_for('auth.login'))

    item_id = request.form.get('item_id')
    carts = load_json(CARTS_FILE, {})
    user_id = str(user['id'])
    user_cart = carts.get(user_id, [])

    existing = next((c for c in user_cart if c['item_id'] == item_id), None)
    if existing:
        existing['qty'] += 1
    else:
        user_cart.append({'item_id': item_id, 'qty': 1})

    carts[user_id] = user_cart
    save_json(CARTS_FILE, carts)
    flash('Added to cart')
    return redirect(url_for('main.menu'))

@bp.route('/checkout')
def checkout():
    user = current_user()
    if not user: return redirect(url_for('auth.login'))
    
    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(str(user['id']), [])
    if not user_cart: return redirect(url_for('main.menu'))

    items_map = {i.get('id'): i for i in load_json(ITEMS_FILE, []) if i.get('id')}
    cart_details = []
    total = 0
    for c in user_cart:
        it = items_map.get(c['item_id'])
        if it:
            subtotal = it['price'] * c['qty']
            total += subtotal
            cart_details.append({'name': it['name'], 'qty': c['qty'], 'subtotal': subtotal})

    return render_template("checkout.html", cart_details=cart_details, total=total, user=user)

@bp.route('/pay_now', methods=['POST'])
def pay_now():
    user = current_user()
    if not user: return redirect(url_for('auth.login'))
    
    carts = load_json(CARTS_FILE, {})
    user_id = str(user['id'])
    user_cart = carts.get(user_id, [])
    
    # Process order... (Simplified for brevity)
    orders = load_json(ORDERS_FILE, [])
    orders.append({'id': str(uuid.uuid4())[:8], 'user': user['name'], 'status': 'Paid'})
    save_json(ORDERS_FILE, orders)
    
    carts[user_id] = []
    save_json(CARTS_FILE, carts)
    flash("Order Placed!")
    return redirect(url_for('main.menu'))
