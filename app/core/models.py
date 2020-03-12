import os
import uuid
from django.db import models, transaction
from django.conf import settings


def customer_image_file_path(instande, filename):
    """Generate file path for new image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('upload/customer/', filename)


class Company(models.Model):

    #  Fields
    company_name = models.CharField(max_length=30)
    company_id = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f'{self.company_name} (pk={self.pk})'


class Profile(models.Model):

    #  Relationships
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='profiles',
        blank=True,
        null=True,
    )

    #  Fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    phone_confirmed = models.BooleanField(default=False)
    image = models.ImageField(null=True, upload_to=customer_image_file_path)
    is_admin = models.BooleanField(default=False)

    company_identificator = models.CharField(
        max_length=255, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name} (id={self.id})'


class Account(models.Model):

    #  Relationships
    profile = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
    )

    #  Fields
    balance = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    account_name = models.CharField(max_length=30)
    account_color = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f'{self.account_name} (pk={self.pk})'


class Action(models.Model):

    #  Relationships
    account = models.ForeignKey(
        'Account',
        on_delete=models.CASCADE,
    )
    tags = models.ManyToManyField("Tag", blank=True)

    #  Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    action_amount = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.pk)


class Transfer(models.Model):

    #  Relationships
    from_account = models.ForeignKey(
        "Account", on_delete=models.CASCADE, related_name='from_account')
    to_account = models.ForeignKey(
        "Account", on_delete=models.CASCADE, related_name='to_account')

    #  Fields
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    transfer_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.pk)


class Transaction(models.Model):

    #  Relationships
    tags = models.ManyToManyField("Tag", blank=True)
    account = models.ForeignKey(
        "Account", on_delete=models.CASCADE,)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)

    #  Fields
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.pk)

    @classmethod
    def make_transaction(cls, transaction_amount, account, category, tags):
        if account.balance < transaction_amount:
            raise(ValueError('Not enough money'))

        with transaction.atomic():
            account.balance -= transaction_amount
            account.save()
            tran = cls.objects.create(
                transaction_amount=transaction_amount,
                account=account,
                category=category,
            )

            tran.tags.set(tags)

        return account, tran


class Category(models.Model):

    #  Relationships
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
    )

    #  Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    category_color = models.CharField(max_length=30)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    caterory_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f'{self.caterory_name} (pk={self.pk})'


class Tag(models.Model):

    #  Relationships
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
    )

    #  Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    tag_color = models.CharField(max_length=30)
    tag_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f'{self.tag_name} (pk={self.pk})'
