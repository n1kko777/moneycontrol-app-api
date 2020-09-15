from django.db import transaction


def make_transfer(from_account, to_account, transfer_amount, **args):

    if from_account == to_account:
        raise ValueError('Выберите другой счет')

    from_company = from_account.profile.company
    to_company = to_account.profile.company

    if from_company != to_company:
        raise ValueError('To_account is not in your company!')

    with transaction.atomic():
        from_balance = from_account.balance - transfer_amount
        from_account.balance = from_balance
        from_account.save()

        to_balance = to_account.balance + transfer_amount
        to_account.balance = to_balance
        to_account.save()
