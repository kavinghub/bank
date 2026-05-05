"""
views.py — All views for the Bank Management System.
Session key 'user_id' tracks the logged-in BankUser.
"""
import json
from decimal import Decimal
from functools import wraps

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db import transaction as db_transaction
from django.utils import timezone

from .models import BankUser, Transaction
from .utils import (
    hash_password, check_password,
    hash_pin, check_pin,
    generate_account_number,
    validate_email, validate_phone, validate_pin,
    validate_password, validate_amount,
)


# ─── Auth Decorator ─────────────────────────────────────────────────────────

def login_required_custom(view_func):
    """Redirect to login if no valid session exists."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'Please log in to continue.')
            return redirect('login')
        # Verify the user still exists in DB
        try:
            request.bank_user = BankUser.objects.get(pk=request.session['user_id'])
        except BankUser.DoesNotExist:
            request.session.flush()
            messages.error(request, 'Session expired. Please log in again.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Public Views ────────────────────────────────────────────────────────────

def index(request):
    """Root URL — redirect to dashboard or login."""
    if 'user_id' in request.session:
        return redirect('dashboard')
    return redirect('login')


@csrf_protect
def register_view(request):
    if 'user_id' in request.session:
        return redirect('dashboard')

    if request.method == 'GET':
        return render(request, 'banking_app/register.html')

    # POST — process registration
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip().lower()
    phone = request.POST.get('phone', '').strip()
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')
    pin = request.POST.get('pin', '').strip()

    errors = []

    if not name or len(name) < 2:
        errors.append("Full name must be at least 2 characters.")
    if not validate_email(email):
        errors.append("Please enter a valid email address.")
    if not validate_phone(phone):
        errors.append("Please enter a valid phone number.")
    if password != confirm_password:
        errors.append("Passwords do not match.")
    pwd_valid, pwd_error = validate_password(password)
    if not pwd_valid:
        errors.append(pwd_error)
    if not validate_pin(pin):
        errors.append("PIN must be 4–6 digits only.")

    # Uniqueness checks
    if BankUser.objects.filter(email=email).exists():
        errors.append("An account with this email already exists.")

    if errors:
        return render(request, 'banking_app/register.html', {
            'errors': errors,
            'form_data': {'name': name, 'email': email, 'phone': phone},
        })

    # Generate a unique account number
    account_number = generate_account_number()
    while BankUser.objects.filter(account_number=account_number).exists():
        account_number = generate_account_number()

    # Create the user
    user = BankUser.objects.create(
        name=name,
        email=email,
        phone=phone,
        account_number=account_number,
        password_hash=hash_password(password),
        pin_hash=hash_pin(pin),
        balance=Decimal('0.00'),
    )

    messages.success(
        request,
        f'Account created successfully! Your account number is {account_number}. Please log in.'
    )
    return redirect('login')


@csrf_protect
def login_view(request):
    if 'user_id' in request.session:
        return redirect('dashboard')

    if request.method == 'GET':
        return render(request, 'banking_app/login.html')

    identifier = request.POST.get('identifier', '').strip()
    password = request.POST.get('password', '')

    if not identifier or not password:
        return render(request, 'banking_app/login.html', {
            'error': 'Please fill in all fields.',
            'identifier': identifier,
        })

    # Find user by email or account number
    user = None
    if '@' in identifier:
        user = BankUser.objects.filter(email=identifier.lower()).first()
    else:
        user = BankUser.objects.filter(account_number=identifier).first()

    if user is None or not check_password(password, user.password_hash):
        return render(request, 'banking_app/login.html', {
            'error': 'Invalid credentials. Please try again.',
            'identifier': identifier,
        })

    # Successful login — create session
    request.session.cycle_key()          # Prevent session fixation
    request.session['user_id'] = user.pk
    request.session['user_name'] = user.name
    request.session.set_expiry(3600)

    return redirect('dashboard')


def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# ─── Protected Views ─────────────────────────────────────────────────────────

@login_required_custom
def dashboard_view(request):
    user = request.bank_user
    recent_txns = Transaction.objects.filter(user=user).order_by('-date_time')[:5]
    return render(request, 'banking_app/dashboard.html', {
        'user': user,
        'recent_transactions': recent_txns,
    })


@login_required_custom
def deposit_view(request):
    user = request.bank_user

    if request.method == 'GET':
        return render(request, 'banking_app/deposit.html', {'user': user})

    amount_str = request.POST.get('amount', '').strip()
    pin = request.POST.get('pin', '').strip()

    # Validate PIN first
    if not check_pin(pin, user.pin_hash):
        return render(request, 'banking_app/deposit.html', {
            'user': user,
            'error': 'Invalid PIN. Transaction cancelled.',
        })


    # Validate amount
    is_valid, amount, amount_error = validate_amount(amount_str)
    if not is_valid:
        return render(request, 'banking_app/deposit.html', {
            'user': user,
            'error': amount_error,
        })

    # Atomic update
    with db_transaction.atomic():
        user_locked = BankUser.objects.select_for_update().get(pk=user.pk)
        user_locked.balance += Decimal(str(amount))
        user_locked.save(update_fields=['balance'])

        Transaction.objects.create(
            user=user_locked,
            type='deposit',
            amount=Decimal(str(amount)),
            description='Deposit via web portal',
        )
        new_balance = user_locked.balance

    return render(request, 'banking_app/deposit.html', {
        'user': user,
        'success': f'₹{amount:,.2f} deposited successfully! New balance: ₹{new_balance:,.2f}',
        'new_balance': new_balance,
    })


@login_required_custom
def withdraw_view(request):
    user = request.bank_user

    if request.method == 'GET':
        return render(request, 'banking_app/withdraw.html', {'user': user})

    amount_str = request.POST.get('amount', '').strip()
    pin = request.POST.get('pin', '').strip()

    # Validate PIN first
    if not check_pin(pin, user.pin_hash):
        return render(request, 'banking_app/withdraw.html', {
            'user': user,
            'error': 'Invalid PIN. Transaction cancelled.',
        })

    # Validate amount
    is_valid, amount, amount_error = validate_amount(amount_str)
    if not is_valid:
        return render(request, 'banking_app/withdraw.html', {
            'user': user,
            'error': amount_error,
        })

    # Atomic update with balance check
    with db_transaction.atomic():
        user_locked = BankUser.objects.select_for_update().get(pk=user.pk)
        if Decimal(str(amount)) > user_locked.balance:
            return render(request, 'banking_app/withdraw.html', {
                'user': user,
                'error': f'Insufficient balance. Available: ₹{user_locked.balance:,.2f}',
            })

        user_locked.balance -= Decimal(str(amount))
        user_locked.save(update_fields=['balance'])

        Transaction.objects.create(
            user=user_locked,
            type='withdraw',
            amount=Decimal(str(amount)),
            description='Withdrawal via web portal',
        )
        new_balance = user_locked.balance

    return render(request, 'banking_app/withdraw.html', {
        'user': user,
        'success': f'₹{amount:,.2f} withdrawn successfully! New balance: ₹{new_balance:,.2f}',
        'new_balance': new_balance,
    })


@login_required_custom
def check_balance_view(request):
    user = request.bank_user

    if request.method == 'GET':
        return render(request, 'banking_app/balance.html', {'user': user, 'balance_revealed': False})

    pin = request.POST.get('pin', '').strip()
    if not check_pin(pin, user.pin_hash):
        return render(request, 'banking_app/balance.html', {
            'user': user,
            'error': 'Invalid PIN.',
            'balance_revealed': False,
        })

    # Fetch fresh balance from DB
    fresh_user = BankUser.objects.get(pk=user.pk)
    return render(request, 'banking_app/balance.html', {
        'user': fresh_user,
        'balance_revealed': True,
        'balance': fresh_user.balance,
    })


@login_required_custom
def transactions_view(request):
    user = request.bank_user
    txns = Transaction.objects.filter(user=user).order_by('-date_time')

    # Optional filter
    txn_type = request.GET.get('type', '')
    if txn_type in ('deposit', 'withdraw'):
        txns = txns.filter(type=txn_type)

    return render(request, 'banking_app/transactions.html', {
        'user': user,
        'transactions': txns,
        'filter_type': txn_type,
    })


# ─── AJAX / API Endpoints ────────────────────────────────────────────────────

@login_required_custom
@require_POST
def verify_pin_ajax(request):
    """Quick PIN check used by JS before enabling sensitive forms."""
    try:
        data = json.loads(request.body)
        pin = data.get('pin', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'valid': False, 'error': 'Bad request.'}, status=400)

    if not pin:
        return JsonResponse({'valid': False, 'error': 'PIN is required.'})

    user = request.bank_user
    return JsonResponse({'valid': check_pin(pin, user.pin_hash)})
