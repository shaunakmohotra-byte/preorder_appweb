from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .store import load_json, save_json, ITEMS_FILE, USERS_FILE, ORDERS_FILE
import uuid

bp = Blueprint('admin', __name__)

# --- Helper Security Check ---
def is_admin():
    uid = session.get('user_id')
    if not uid:
        return False
    users = load_json(USERS_FILE, [])
    user = next((u for u in users if u.get('id') == uid), None)
    return user and user.get('is_admin') is True

# --- Routes ---

@bp.route('/')
def index():
    if not is_admin():
        flash('Admin access required.')
        return redirect(url_for('auth.login'))
    
    users = load_json(USERS_FILE, [])
    items = load_json(ITEMS_FILE, [])
    orders = load_json(ORDERS_FILE, [])
    
    return render_template('admin.html', 
                           users=users, 
                           items=items, 
                           orders=orders)

@bp.route('/add_item', methods=['POST'])
def add_item():
    if not is_admin(): return redirect(url_for('auth.login'))

    name = request.form.get('name')
    price = request.form.get('price')

    if name and price:
        items = load_json(ITEMS_FILE, [])
        new_item = {
            'id': str(uuid.uuid4())[:8],
            'name': name,
            'price': int(price)
        }
        items.append(new_item)
        save_json(ITEMS_FILE, items)
        flash(f'Added {name}')
    
    return redirect(url_for('admin.index'))

@bp.route('/delete_item/<item_id>', methods=['POST'])
def delete_item(item_id):
    if not is_admin(): return redirect(url_for('auth.login'))
    
    items = load_json(ITEMS_FILE, [])
    items = [it for it in items if it.get('id') != item_id]
    save_json(ITEMS_FILE, items)
    
    flash('Item deleted')
    return redirect(url_for('admin.index'))

@bp.route('/edit_user/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not is_admin(): return redirect(url_for('auth.login'))

    users = load_json(USERS_FILE, [])
    user = next((u for u in users if u.get('id') == user_id), None)
    
    if not user:
        flash('User not found')
        return redirect(url_for('admin.index'))

    if request.method == 'POST':
        user['name'] = request.form.get('name')
        user['email'] = request.form.get('email')
        user['is_admin'] = True if request.form.get('is_admin') else False
        
        save_json(USERS_FILE, users)
        flash('User updated')
        return redirect(url_for('admin.index'))

    return render_template('edit_user.html', user=user)

@bp.route('/delete_user', methods=['POST'])
def delete_user():
    if not is_admin(): return redirect(url_for('auth.login'))

    user_id = request.form.get('user_id')
    users = load_json(USERS_FILE, [])
    
    # Prevent admin from deleting themselves
    if user_id == session.get('user_id'):
        flash("You cannot delete your own account!")
        return redirect(url_for('admin.index'))

    users = [u for u in users if u.get('id') != user_id]
    save_json(USERS_FILE, users)
    flash('User deleted')
    return redirect(url_for('admin.index'))
