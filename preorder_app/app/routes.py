import os, datetime, uuid, threading
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .store import load_json, save_json, ITEMS_FILE, CARTS_FILE, ORDERS_FILE, USERS_FILE
from utils.pdf_invoice import generate_invoice_pdf
from flask import send_file

bp = Blueprint('main', __name__)

def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    users = load_json(USERS_FILE, [])
    return next((u for u in users if str(u.get('id')) == str(uid)), None)


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

    # Load carts safely
    carts = load_json(CARTS_FILE, {})
    if not isinstance(carts, dict):
        carts = {}

    # Load all items
    items = load_json(ITEMS_FILE, [])
    items_map = {str(i['id']): i for i in items if 'id' in i}

    user_id = str(user['id'])
    user_cart = carts.get(user_id, [])

    cart_details = []
    total = 0

    for c in user_cart:
        item_id = str(c.get('item_id'))
        qty = int(c.get('qty', 0))

        item = items_map.get(item_id)
        if not item or qty <= 0:
            continue

        price = int(item.get('price', 0))
        subtotal = price * qty
        total += subtotal

        cart_details.append({
            'item_id': item_id,
            'name': item.get('name', 'Unknown Item'),
            'qty': qty,
            'subtotal': subtotal
        })

    return render_template(
        'cart.html',
        cart_details=cart_details,
        total=total,
        user=user
    )

@bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user = current_user()
    if not user:
        flash('Please login first')
        return redirect(url_for('auth.login'))

    item_id = request.form.get('item_id')
    if not item_id:
        flash('Invalid item')
        return redirect(url_for('main.menu'))

    carts = load_json(CARTS_FILE, {})
    if not isinstance(carts, dict):
        carts = {}

    user_id = str(user['id'])
    user_cart = carts.get(user_id, [])

    for c in user_cart:
        if str(c.get('item_id')) == str(item_id):
            c['qty'] += 1
            break
    else:
        user_cart.append({'item_id': item_id, 'qty': 1})

    carts[user_id] = user_cart
    save_json(CARTS_FILE, carts)

    flash('Added to cart')
    return redirect(url_for('main.menu'))


@bp.route('/cart/increase', methods=['POST'])
def cart_increase():
    user = current_user()
    if not user:
        return redirect(url_for('auth.login'))

    item_id = request.form.get('item_id')
    carts = load_json(CARTS_FILE, {})
    if not isinstance(carts, dict):
        carts = {}

    user_id = str(user['id'])
    user_cart = carts.get(user_id, [])

    for c in user_cart:
        if str(c.get('item_id')) == str(item_id):
            c['qty'] += 1
            break

    carts[user_id] = user_cart
    save_json(CARTS_FILE, carts)
    return redirect(url_for('main.view_cart'))

@bp.route('/cart/decrease', methods=['POST'])
def cart_decrease():
    user = current_user()
    if not user:
        return redirect(url_for('auth.login'))

    item_id = request.form.get('item_id')
    carts = load_json(CARTS_FILE, {})
    if not isinstance(carts, dict):
        carts = {}

    user_id = str(user['id'])
    user_cart = carts.get(user_id, [])

    for c in user_cart:
        if str(c.get('item_id')) == str(item_id):
            c['qty'] -= 1
            if c['qty'] <= 0:
                user_cart.remove(c)
            break

    carts[user_id] = user_cart
    save_json(CARTS_FILE, carts)
    return redirect(url_for('main.view_cart'))



@bp.route('/checkout')
def checkout():
    user = current_user()
    if not user:
        flash('Please login to checkout')
        return redirect(url_for('auth.login'))

    # Load data safely
    carts = load_json(CARTS_FILE, {})
    if not isinstance(carts, dict): carts = {}
    
    all_items = load_json(ITEMS_FILE, [])
    # Map items by ID for quick lookup
    items_map = {str(i.get('id')): i for i in all_items if i.get('id')}
    
    user_id = str(user.get('id', ''))
    user_cart = carts.get(user_id, [])

    if not user_cart:
        flash('Your cart is empty')
        return redirect(url_for('main.menu'))

    checkout_details = []
    total = 0
    
    for c in user_cart:
        item_id = str(c.get('item_id', ''))
        it = items_map.get(item_id)
        
        if it:
            qty = c.get('qty', 0)
            price = it.get('price', 0)
            subtotal = price * qty
            total += subtotal
            # We flatten the structure here for easier use in checkout.html
            checkout_details.append({
                'name': it.get('name', 'Unknown Item'),
                'price': price,
                'qty': qty,
                'subtotal': subtotal
            })

    return render_template("checkout.html", 
                           cart_details=checkout_details, 
                           total=total, 
                           user=user)

from .email_utils import send_order_email

@bp.route('/pay_now', methods=['POST'])
def pay_now():
    user = current_user()
    if not user:
        return redirect(url_for('auth.login'))

    carts = load_json(CARTS_FILE, {})
    items = load_json(ITEMS_FILE, [])
    items_map = {str(i["id"]): i for i in items}

    user_id = str(user["id"])
    user_cart = carts.get(user_id, [])

    if not user_cart:
        flash("Cart empty")
        return redirect(url_for('main.menu'))

    order_items = []
    total = 0

    for c in user_cart:
        item = items_map.get(str(c["item_id"]))
        if not item:
            continue
        qty = c["qty"]
        subtotal = item["price"] * qty
        total += subtotal
        order_items.append({
            "name": item["name"],
            "qty": qty
        })

    # Save order
    order_id = str(uuid.uuid4())[:8]
    orders = load_json(ORDERS_FILE, [])
    orders.append({
        "id": order_id,
        "user_name": user["username"],
        "items": order_items,
        "total": total,
        "status": "Paid"
    })
    save_json(ORDERS_FILE, orders)

    # Clear cart
    carts[user_id] = []
    save_json(CARTS_FILE, carts)

    # Generate PDF e-bill
    from app.utils.pdf_invoice import generate_invoice_pdf
    pdf_path = generate_invoice_pdf(
        order_id=order_id,
        user=user,
        order_items=order_items,
        total=total
    )

    flash("Payment successful! Your e-bill is downloading.")
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"invoice_{order_id}.pdf"
    )


