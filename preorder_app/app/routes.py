from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .db import users_col, items_col, carts_col, orders_col
import uuid
from datetime import datetime

from .utils.pdf_invoice import generate_invoice_pdf

bp = Blueprint('main', __name__)


# ===============================
# CURRENT USER
# ===============================
def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return users_col.find_one({'id': uid})


# ===============================
# HOME
# ===============================
@bp.route('/')
def index():
    return redirect(url_for('main.menu'))


# ===============================
# MENU
# ===============================
@bp.route('/menu')
def menu():
    items = list(items_col.find({}, {'_id': 0}))
    return render_template('menu.html', items=items, user=current_user())



# ===============================
# VIEW CART
# ===============================
@bp.route('/cart')
def view_cart():

    user = current_user()

    if not user:
        flash('Please login to view cart')
        return redirect(url_for('auth.login'))

    carts = (CARTS_FILE, {})

    if not isinstance(carts, dict):
        carts = {}

    items = (ITEMS_FILE, [])
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
            'price': price,
            'subtotal': subtotal
        })

    return render_template(
        'cart.html',
        cart_details=cart_details,
        total=total,
        user=user
    )


# ===============================
# ADD TO CART
# ===============================
from .db import carts_col

@bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user = current_user()

    if not user:
        flash('Please login first')
        return redirect(url_for('auth.login'))

    item_id = request.form.get('item_id')
    user_id = user['id']

    cart = carts_col.find_one({'user_id': user_id})

    if not cart:
        carts_col.insert_one({
            'user_id': user_id,
            'items': [{'item_id': item_id, 'qty': 1}]
        })
    else:
        found = False
        for item in cart['items']:
            if item['item_id'] == item_id:
                item['qty'] += 1
                found = True
                break

        if not found:
            cart['items'].append({'item_id': item_id, 'qty': 1})

        carts_col.update_one(
            {'user_id': user_id},
            {'$set': {'items': cart['items']}}
        )

    flash('Added to cart')
    return redirect(url_for('main.menu'))

# ===============================
# INCREASE CART
# ===============================
@bp.route('/cart/increase', methods=['POST'])
def cart_increase():

    user = current_user()

    if not user:
        return redirect(url_for('auth.login'))

    item_id = request.form.get('item_id')

    carts = (CARTS_FILE, {})

    if not isinstance(carts, dict):
        carts = {}

    user_id = str(user['id'])
    user_cart = carts.get(user_id, [])

    for c in user_cart:
        if str(c.get('item_id')) == str(item_id):
            c['qty'] += 1
            break

    carts[user_id] = user_cart
    (CARTS_FILE, carts)

    return redirect(url_for('main.view_cart'))


# ===============================
# DECREASE CART
# ===============================
@bp.route('/cart/decrease', methods=['POST'])
def cart_decrease():

    user = current_user()

    if not user:
        return redirect(url_for('auth.login'))

    item_id = request.form.get('item_id')

    carts = (CARTS_FILE, {})

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
    (CARTS_FILE, carts)

    return redirect(url_for('main.view_cart'))


# ===============================
# CHECKOUT
# ===============================
@bp.route('/checkout')
def checkout():

    user = current_user()

    if not user:
        flash('Please login to checkout')
        return redirect(url_for('auth.login'))

    carts = (CARTS_FILE, {})

    if not isinstance(carts, dict):
        carts = {}

    all_items = (ITEMS_FILE, [])
    items_map = {str(i.get('id')): i for i in all_items if i.get('id')}

    user_id = str(user.get('id'))
    user_cart = carts.get(user_id, [])

    if not user_cart:
        flash('Your cart is empty')
        return redirect(url_for('main.menu'))

    checkout_details = []
    total = 0

    for c in user_cart:

        item_id = str(c.get('item_id'))
        it = items_map.get(item_id)

        if it:

            qty = c.get('qty', 0)
            price = it.get('price', 0)

            subtotal = price * qty

            total += subtotal

            checkout_details.append({
                'name': it.get('name', 'Unknown Item'),
                'price': price,
                'qty': qty,
                'subtotal': subtotal
            })

    return render_template(
        "checkout.html",
        cart_details=checkout_details,
        total=total,
        user=user
    )


# ===============================
# PAY NOW
# ===============================
@bp.route('/pay_now', methods=['POST'])
def pay_now():

    user = current_user()

    if not user:
        flash("Please login first")
        return redirect(url_for('auth.login'))

    carts = (CARTS_FILE, {})
    items = (ITEMS_FILE, [])

    if not isinstance(carts, dict):
        carts = {}

    items_map = {str(i.get("id")): i for i in items if i.get("id")}

    user_id = str(user.get("id"))
    user_cart = carts.get(user_id, [])

    if not user_cart:
        flash("Your cart is empty")
        return redirect(url_for('main.menu'))

    order_items = []
    total = 0

    for c in user_cart:

        item_id = str(c.get("item_id"))
        qty = int(c.get("qty", 0))

        item = items_map.get(item_id)

        if not item or qty <= 0:
            continue

        price = int(item.get("price", 0))
        subtotal = price * qty

        total += subtotal

        order_items.append({
            "name": item.get("name", "Unknown"),
            "qty": qty,
            "price": price,
            "subtotal": subtotal
        })

    order_id = str(uuid.uuid4())[:8]

    orders = (ORDERS_FILE, [])

    if not isinstance(orders, list):
        orders = []

    token_number = max([o.get("token", 0) for o in orders], default=0) + 1

    orders.append({
        "id": order_id,
        "token": token_number,
        "user_name": user.get("username") or user.get("email"),
        "items": order_items,
        "total": total,
        "status": "Paid",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    (ORDERS_FILE, orders)

    carts[user_id] = []
    (CARTS_FILE, carts)

    pdf_path = generate_invoice_pdf(
        order_id=order_id,
        user=user,
        order_items=order_items,
        total=total,
        token=token_number
    )

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"invoice_{order_id}.pdf"
    )


# ===============================
# CAFETERIA DASHBOARD
# ===============================
@bp.route('/cafeteria')
def cafeteria():

    user = current_user()

    orders = (ORDERS_FILE, [])

    return render_template(
        'cafeteria.html',
        orders=orders,
        user=user
    )

# ===============================
# DELETE ORDER AFTER DELAY
# ===============================
def delete_order_after_delay(order_id, delay=60):

    def delete():
        orders = (ORDERS_FILE, [])

        if not isinstance(orders, list):
            orders = []

        orders = [o for o in orders if o.get("id") != order_id]

        (ORDERS_FILE, orders)

    timer = threading.Timer(60, delete)
    timer.start()

# ===============================
# MARK ORDER DELIVERED
# ===============================
@bp.route('/mark_order_delivered/<order_id>', methods=['POST'])
def mark_order_paid(order_id):

    orders = (ORDERS_FILE, [])

    if not isinstance(orders, list):
        orders = []

    for o in orders:
        if o.get("id") == order_id:
            o["status"] = "Delivered"

    (ORDERS_FILE, orders)

    # start auto-delete timer (1 minute)
    delete_order_after_delay(order_id, 60)

    flash("Order marked as delivered. It will be removed in 1 minute.")

    return redirect(url_for('main.cafeteria'))
