import os
import uuid
from werkzeug.security import generate_password_hash

# Path Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

USERS_FILE = os.path.join(DATA_DIR, 'users.json')
ITEMS_FILE = os.path.join(DATA_DIR, 'items.json')
CARTS_FILE = os.path.join(DATA_DIR, 'carts.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def init_default_data():
    """Run this on startup to ensure files exist and admin is created."""
    # Initialize Users
    if not any(u.get('email') == 'admin@example.com' for u in users):
        admin = {
            'id': str(uuid.uuid4()),
            'name': 'Admin User',
            'email': 'admin@example.com',
            'password_hash': generate_password_hash('admin123'),
            'is_admin': True
        }
        users.append(admin)
        
    # Initialize Items
   if not items:
        default_items = [
            {'id': '1', 'name': 'Veg Burger', 'price': 70},
            {'id': '2', 'name': 'Chicken Sandwich', 'price': 120},
            {'id': '3', 'name': 'Hot Coffee', 'price': 40}
        ]
