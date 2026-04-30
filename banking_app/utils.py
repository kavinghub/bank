"""
utils.py — Security helpers for password/PIN hashing and validation.
Uses bcrypt for all sensitive data. Never stores raw passwords or PINs.
"""
import bcrypt
import re
import random
import string


# ─── Hashing ────────────────────────────────────────────────────────────────

def hash_password(raw_password: str) -> str:
    """Hash a plaintext password with bcrypt. Returns the hash as a string."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def check_password(raw_password: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(raw_password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def hash_pin(raw_pin: str) -> str:
    """Hash a 4–6 digit PIN with bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(raw_pin.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def check_pin(raw_pin: str, hashed: str) -> bool:
    """Verify a plaintext PIN against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(raw_pin.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


# ─── Account Number Generator ────────────────────────────────────────────────

def generate_account_number() -> str:
    """Generate a unique 12-digit account number."""
    return ''.join(random.choices(string.digits, k=12))


# ─── Input Validators ────────────────────────────────────────────────────────

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    pattern = r'^\+?[\d\s\-]{7,15}$'
    return bool(re.match(pattern, phone.strip()))


def validate_pin(pin: str) -> bool:
    """PIN must be exactly 4–6 digits."""
    return bool(re.match(r'^\d{4,6}$', pin))


def validate_password(password: str) -> tuple[bool, str]:
    """
    Password rules:
      - At least 8 characters
      - At least one uppercase letter
      - At least one digit
    Returns (is_valid, error_message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    return True, ""


def validate_amount(amount_str: str) -> tuple[bool, float, str]:
    """
    Validate a transaction amount string.
    Returns (is_valid, amount_as_float, error_message).
    """
    try:
        amount = float(amount_str)
    except (ValueError, TypeError):
        return False, 0, "Please enter a valid numeric amount."
    if amount <= 0:
        return False, 0, "Amount must be greater than zero."
    if amount > 1_000_000:
        return False, 0, "Amount cannot exceed ₹10,00,000 per transaction."
    # Round to 2 decimal places to avoid floating-point surprises
    amount = round(amount, 2)
    return True, amount, ""
