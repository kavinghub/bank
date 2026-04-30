from django.contrib import admin
from .models import BankUser, Transaction


@admin.register(BankUser)
class BankUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'account_number', 'balance', 'created_at')
    search_fields = ('name', 'email', 'account_number')
    readonly_fields = ('password_hash', 'pin_hash', 'created_at')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'amount', 'date_time', 'description')
    search_fields = ('user__name', 'user__account_number')
    list_filter = ('type', 'date_time')
    ordering = ('-date_time',)
