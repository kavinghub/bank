# VaultX — Bank Management System

A full-stack Django bank management system with MySQL, bcrypt security, PIN-protected transactions, and a dark financial dashboard UI.

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3.10+ / Django 4.2         |
| Frontend  | HTML5, CSS3 (custom), JavaScript  |
| Database  | MySQL 8.0+                        |
| Security  | bcrypt (passwords + PINs)         |
| Sessions  | Django server-side sessions       |

---

## Features

- **Registration** — Name, Email, Phone, auto-generated Account Number, bcrypt-hashed Password & PIN  
- **Login** — Email or Account Number + Password  
- **Session Management** — 1-hour server-side sessions with session fixation protection  
- **Dashboard** — Account info, live clock, recent transactions, quick action cards  
- **Deposit** — PIN-verified, atomic DB update, transaction record stored  
- **Withdraw** — PIN-verified, balance check, atomic deduction, transaction record  
- **Check Balance** — PIN-verified balance reveal (also via modal on dashboard)  
- **Transaction History** — Full table, filter by type, deposit/withdrawal totals  
- **Logout** — Full session flush  
- **Security** — bcrypt hashing, CSRF protection, `select_for_update()` for race-condition-safe transactions, input validation, SQL injection prevention via ORM  

---

## Folder Structure

```
bank_system/
├── manage.py
├── requirements.txt
├── setup_database.sql          ← Run this first in MySQL
│
├── bank_project/               ← Django project config
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── banking_app/                ← Main Django app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               ← BankUser, Transaction
│   ├── views.py                ← All request handlers
│   ├── urls.py                 ← App URL routes
│   └── utils.py                ← bcrypt helpers, validators
│
├── templates/
│   └── banking_app/
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── _sidebar.html       ← Shared sidebar partial
│       ├── dashboard.html
│       ├── deposit.html
│       ├── withdraw.html
│       ├── balance.html
│       └── transactions.html
│
└── static/
    └── banking_app/
        ├── css/main.css        ← Full design system
        └── js/main.js          ← Global JS utilities
```

---

## Prerequisites

Make sure these are installed on your machine:

- Python 3.10 or higher  
- MySQL 8.0 or higher  
- pip  
- (Optional but recommended) virtualenv  

---

## Step-by-Step Setup

### Step 1 — Clone / Download the project

```bash
# If using git:
git clone <repo-url> bank_system
cd bank_system

# Or just navigate to the extracted folder:
cd bank_system
```

---

### Step 2 — Create a Python virtual environment

```bash
python -m venv venv

# Activate it:
# On macOS / Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

---

### Step 3 — Install Python dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `mysqlclient` requires MySQL development headers.  
> - **Ubuntu/Debian:** `sudo apt-get install default-libmysqlclient-dev`  
> - **macOS (Homebrew):** `brew install mysql-client` then `export PKG_CONFIG_PATH="/opt/homebrew/opt/mysql-client/lib/pkgconfig"`  
> - **Windows:** Use `pip install mysqlclient` (pre-compiled wheels available) or install MySQL Connector.

---

### Step 4 — Set up the MySQL database

Open your MySQL shell (or a GUI like MySQL Workbench / TablePlus) and run:

```bash
mysql -u root -p
```

Then paste and execute the entire contents of `setup_database.sql`:

```sql
SOURCE /path/to/bank_system/setup_database.sql;
```

Or copy-paste the file content directly. This creates:
- `bank_db` database  
- `bank_users` table  
- `bank_transactions` table  

---

### Step 5 — Configure database credentials

Open `bank_project/settings.py` and update the `DATABASES` section:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bank_db',
        'USER': 'root',           # ← Your MySQL username
        'PASSWORD': 'yourpassword',  # ← Your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

---

### Step 6 — Run Django migrations

Django needs to create its own internal tables (sessions, admin, etc.):

```bash
python manage.py migrate
```

Expected output includes lines like:
```
Applying banking_app.0001_initial... OK
Applying sessions.0001_initial... OK
```

---

### Step 7 — Collect static files (optional for development)

```bash
python manage.py collectstatic --noinput
```

> In development (`DEBUG=True`), Django serves static files automatically — you can skip this step.

---

### Step 8 — (Optional) Create a Django superuser for admin panel

```bash
python manage.py createsuperuser
```

Access the admin panel at: `http://127.0.0.1:8000/admin/`

---

### Step 9 — Run the development server

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

---

### Step 10 — Open in your browser

| URL                                     | Page                    |
|-----------------------------------------|-------------------------|
| http://127.0.0.1:8000/register/         | Create a new account    |
| http://127.0.0.1:8000/login/            | Sign in                 |
| http://127.0.0.1:8000/dashboard/        | Main dashboard          |
| http://127.0.0.1:8000/deposit/          | Deposit funds           |
| http://127.0.0.1:8000/withdraw/         | Withdraw funds          |
| http://127.0.0.1:8000/balance/          | Check balance           |
| http://127.0.0.1:8000/transactions/     | Transaction history     |
| http://127.0.0.1:8000/admin/            | Django admin panel      |

---

## Security Notes

| Feature                  | Implementation                                           |
|--------------------------|----------------------------------------------------------|
| Password storage         | bcrypt with cost factor 12 (via `bcrypt` library)        |
| PIN storage              | bcrypt (same strength as passwords)                      |
| SQL Injection            | Django ORM (parameterized queries) — no raw SQL          |
| CSRF                     | Django `{% csrf_token %}` on all POST forms              |
| Session fixation         | `request.session.cycle_key()` on login                   |
| Race conditions          | `select_for_update()` wraps all balance mutations         |
| Input validation         | Server-side (utils.py) + client-side (JS)                |
| Sensitive action guard   | PIN required for deposit, withdraw, balance check         |

---

## Troubleshooting

**`django.db.utils.OperationalError: (1045, "Access denied for user...")`**  
→ Wrong MySQL username or password in `settings.py`

**`django.db.utils.OperationalError: (2002, "Can't connect to MySQL server")`**  
→ MySQL service is not running. Start it with `sudo systemctl start mysql` (Linux) or via System Preferences (macOS).

**`ModuleNotFoundError: No module named 'MySQLdb'`**  
→ Run `pip install mysqlclient` and ensure MySQL dev headers are installed.

**Static files not loading (CSS broken)**  
→ Make sure `DEBUG = True` in settings, or run `python manage.py collectstatic`.

**`TemplateDoesNotExist: banking_app/login.html`**  
→ Confirm `'APP_DIRS': True` is set in `TEMPLATES` in `settings.py`.

---

## Database Schema

### `bank_users`

| Column         | Type             | Notes                            |
|----------------|------------------|----------------------------------|
| id             | BIGINT (PK)      | Auto-increment                   |
| name           | VARCHAR(150)     |                                  |
| email          | VARCHAR(254)     | Unique                           |
| phone          | VARCHAR(20)      |                                  |
| account_number | VARCHAR(20)      | Unique, auto-generated 12 digits |
| password_hash  | VARCHAR(255)     | bcrypt hash                      |
| pin_hash       | VARCHAR(255)     | bcrypt hash                      |
| balance        | DECIMAL(15,2)    | Default 0.00                     |
| created_at     | DATETIME         | Auto set on creation             |

### `bank_transactions`

| Column      | Type                        | Notes                  |
|-------------|----------------------------|------------------------|
| id          | BIGINT (PK)                | Auto-increment         |
| user_id     | BIGINT (FK → bank_users)   | Cascade delete         |
| type        | ENUM('deposit','withdraw') |                        |
| amount      | DECIMAL(15,2)              |                        |
| date_time   | DATETIME                   | Auto set on creation   |
| description | VARCHAR(255)               |                        |

---

## Production Checklist

Before deploying to production:

- [ ] Set `DEBUG = False` in `settings.py`
- [ ] Set `SECRET_KEY` from an environment variable (never hardcode)
- [ ] Set `ALLOWED_HOSTS` to your actual domain
- [ ] Use `python-decouple` or `python-dotenv` for `.env` file management
- [ ] Configure a production WSGI server (Gunicorn + Nginx)
- [ ] Enable HTTPS — Django's `SECURE_SSL_REDIRECT = True`
- [ ] Set `SESSION_COOKIE_SECURE = True` and `CSRF_COOKIE_SECURE = True`
- [ ] Run `python manage.py collectstatic` and serve from a CDN or Nginx

---

*Built with Django 4.2 + MySQL 8 + bcrypt. UI: Syne + DM Mono fonts, dark amber theme.*
