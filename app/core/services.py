from .models import Account, Transfer
from django.db import transaction
from django.core.exceptions import ValidationError


def make_transfer(from_account, to_account, amount):

    if from_account.balance < amount:
        raise(ValueError('Not enough money'))
    if from_account == to_account:
        raise(ValueError('Chose another account'))

    with transaction.atomic():
        from_balance = from_account.balance - amount
        from_account.balance = from_balance
        from_account.save()

        to_balance = to_account.balance + amount
        to_account.balance = to_balance
        to_account.save()

        transfer = Transfer.objects.create(
            from_account=from_account,
            to_account=to_account,
            amount=amount
        )

    return transfer


def filter_user_account(user, account_id):
    try:
        account = Account.objects.filter(
            user=user).get(pk=account_id)
    except (Account.DoesNotExist):
        raise ValidationError("Account doesn't exist")

    return account


def check_account_exists(account_id):
    try:
        account = Account.objects.get(pk=account_id)
    except Exception as e:
        print(e)
        raise ValueError('No such account')

    return account
