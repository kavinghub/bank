from django.db import models
from django.utils import timezone


class BankUser(models.Model):
    """Custom user model — does NOT use Django's auth system so we manage
    password/PIN hashing ourselves with bcrypt."""

    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    account_number = models.CharField(max_length=20, unique=True)
    password_hash = models.CharField(max_length=255)
    pin_hash = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'bank_users'
        verbose_name = 'Bank User'

    def __str__(self):
        return f"{self.name} ({self.account_number})"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]

    user = models.ForeignKey(
        BankUser,
        on_delete=models.CASCADE,
        related_name='transactions',
        db_column='user_id',
    )
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date_time = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        db_table = 'bank_transactions'
        ordering = ['-date_time']
        verbose_name = 'Transaction'

    def __str__(self):
        return f"{self.type.title()} ₹{self.amount} — {self.user.account_number}"
