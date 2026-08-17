# 🍽️ Cafeteria Pre-Order System

A web-based application that allows students to pre-order meals from the school cafeteria, reducing waiting time, improving efficiency, and enabling better food management.

---

## 🚀 Features

* 🔐 **Secure User Authentication**

  * Login & registration using hashed passwords (Scrypt/Werkzeug)

* 🛒 **Smart Cart System**

  * Add, remove, increase, or decrease item quantities
  * Real-time total calculation

* 🧾 **Automated PDF Invoice Generation**

  * Generates e-bill with order details
  * Downloadable receipt after checkout

* 🆔 **Order Management**

  * Unique Order ID and Token Number for each order
  * Used for food collection

* 🧑‍🍳 **Cafeteria Dashboard**

  * Staff can view and manage orders
  * Mark orders as delivered

* ☁️ **Persistent Database (MongoDB)**

  * No data loss on restart
  * Supports multiple users and scalability

---

## 🏗️ Tech Stack

### Frontend

* HTML
* CSS
* Jinja2 Templates

### Backend

* Python
* Flask

### Database

* MongoDB (via PyMongo)

### Other Libraries

* ReportLab (for PDF generation)
* Werkzeug (for authentication security)

---

## 📁 Project Structure

```
preorder_app/
│
├── run.py
├── requirements.txt
├── wsgi.py
│
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── routes/
│   ├── services/
│   └── utils/
│
├── templates/
├── static/
└── data/ (legacy - no longer used)
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/preorder-app.git
cd preorder-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

```bash
export MONGO_URI=your_mongodb_connection_string
export DB_NAME=cafeteria_app
export SECRET_KEY=your_secret_key
export GMAIL_SMTP_EMAIL=preorderapp.tis@gmail.com
export GMAIL_APP_PASSWORD=your_16_digit_google_app_password
export EMAIL_FROM=preorderapp.tis@gmail.com
```

(For Windows, use `set` instead of `export`)

### Email broadcasts

Administrators can send an announcement from **Admin Dashboard → Compose
Email**. Delivery uses Gmail SMTP with a private Google App Password. The app
sends one separate email to each registered user, so recipients do not see one
another's email addresses.

### 4. Run the Application

```bash
python run.py
```

---

## 🌐 Deployment

The app can be deployed using platforms like:

* Render
* Railway
* Heroku (with MongoDB Atlas)

### Render configuration

This repository is deployed with `preorder_app` as the Render **Root
Directory**. In the existing Render service, set the following under
**Environment** and choose **Save and deploy**:

| Key | Value |
| --- | --- |
| `MONGO_URI` | Your MongoDB Atlas connection string |
| `DB_NAME` | `cafeteria_app` (or your chosen database name) |
| `SECRET_KEY` | A long, random private value |
| `GMAIL_SMTP_EMAIL` | `preorderapp.tis@gmail.com` |
| `GMAIL_APP_PASSWORD` | A 16-digit Google App Password (not your normal Gmail password) |
| `EMAIL_FROM` | `preorderapp.tis@gmail.com` |
| `PYTHON_VERSION` | `3.13.5` |

Use `pip install -r requirements.txt` as the build command and
`gunicorn wsgi:app` as the start command. Before deploying, enable 2-Step
Verification for `preorderapp.tis@gmail.com`, create an App Password in Google
Account security, and copy it to `GMAIL_APP_PASSWORD` without spaces. Then
deploy this change and send a broadcast to a test registered user. SMTP
configuration and delivery failures are logged without exposing the password.

---

## 🧠 How It Works

1. Users register/login securely
2. Browse menu and add items to cart
3. Checkout generates:

   * Order ID
   * Token Number
   * PDF Invoice
4. Order is stored in MongoDB
5. Cafeteria staff processes the order
6. Student collects food using token/invoice

---

## 🔮 Future Enhancements

* 💳 Online Payment Integration (UPI, Cards)
* 📱 Mobile App (Android/iOS)
* 🤖 AI-Based Meal Recommendations
* 📡 RFID / QR Code Pickup System
* 📊 Admin Analytics Dashboard
* 📩 Email Invoice Delivery

---

## 📌 Key Advantages

* Eliminates long queues
* Reduces food wastage
* Improves efficiency
* Enables digital record keeping
* Scalable and reliable system

---

## ⚠️ Limitations

* Requires internet connection
* Dependent on digital access for users

---

## 👨‍💻 Author

**Shaunak Mohotra**
Class XI – C

---

## 📄 License

This project is developed for educational purposes.

---

## 🙌 Acknowledgements

* Flask Documentation
* MongoDB Documentation
* ReportLab Library
* Open-source community resources

---

## ⭐ Final Note

This project demonstrates how technology can streamline everyday processes like cafeteria management by combining secure authentication, real-time ordering, and persistent cloud storage.

---
