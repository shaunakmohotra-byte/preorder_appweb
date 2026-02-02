import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .store import load_json, save_json, USERS_FILE

bp = Blueprint('auth', __name__)

def get_current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    users = load_json(USERS_FILE, [])
    return next((u for u in users if u.get('id') == uid), None)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        pwd = request.form.get('password')
        
        users = load_json(USERS_FILE, [])
        if any(u.get('email') == email for u in users):
            flash('Email already registered')
            return redirect(url_for('auth.register'))
            
        new_user = {
            'id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'password_hash': generate_password_hash(pwd),
            'is_admin': False
        }
        
        users.append(new_user)
        save_json(USERS_FILE, users)
        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html', user=get_current_user())

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('password')
        
        users = load_json(USERS_FILE, [])
        user = next((u for u in users if u.get('email') == email), None)
        
        # Verify password against 'password_hash' key
        if user and check_password_hash(user.get('password_hash', ''), pwd):
            session.clear()
            session['user_id'] = user['id']
            session['is_admin'] = user.get('is_admin', False)
            flash(f'Welcome, {user["name"]}!')
            return redirect(url_for('main.menu'))
        
        flash('Invalid email or password')
        return redirect(url_for('auth.login'))
        
    return render_template('login.html', user=get_current_user())

@bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('main.menu'))
