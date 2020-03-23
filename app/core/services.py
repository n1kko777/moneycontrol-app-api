from .models import Transfer
from django.db import transaction


def make_transfer(from_account, to_account, transfer_amount):

    if from_account.balance < transfer_amount:
        raise(ValueError('Not enough money'))
    if from_account == to_account:
        raise(ValueError('Chose another account'))

    from_company = from_account.profile.company
    to_company = to_account.profile.company

    if from_company != to_company:
        raise(ValueError('To_account is not in your company!'))

    with transaction.atomic():
        from_balance = from_account.balance - transfer_amount
        from_account.balance = from_balance
        from_account.save()

        to_balance = to_account.balance + transfer_amount
        to_account.balance = to_balance
        to_account.save()

        transfer = Transfer.objects.create(
            from_account=from_account,
            to_account=to_account,
            transfer_amount=transfer_amount
        )

    return transfer
