
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .db import users_col
import uuid

bp = Blueprint('auth', __name__)


def get_current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return users_col.find_one({'id': uid})

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        pwd = request.form.get('password')
        
        users = (USERS_FILE, [])
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
        (USERS_FILE, users)
        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html', user=get_current_user())



@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        pwd = request.form.get('password')

        if users_col.find_one({'email': email}):
            flash("Email exists")
            return redirect(url_for('auth.register'))

        users_col.insert_one({
            'id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'password_hash': generate_password_hash(pwd),
            'is_admin': False
        })

        flash("Registered")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('main.menu'))
