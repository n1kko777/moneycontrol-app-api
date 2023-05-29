import os
import uuid
from django.db import models
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
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
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
    is_active = models.BooleanField(default=True)

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
        related_name="accounts",
        on_delete=models.DO_NOTHING,
    )
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
    )

    #  Fields
    balance = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    account_name = models.CharField(max_length=30)
    account_color = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f'{self.account_name} (pk={self.pk})'


class Action(models.Model):

    #  Relationships
    account = models.ForeignKey(
        'Account',
        on_delete=models.DO_NOTHING,
    )
    tags = models.ManyToManyField("Tag", blank=True)
    category = models.ForeignKey(
        "Category", on_delete=models.DO_NOTHING)
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
    )

    #  Fields
    action_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.pk)


class Transfer(models.Model):

    #  Relationships
    from_account = models.ForeignKey(
        "Account", on_delete=models.DO_NOTHING, related_name='from_account')
    to_account = models.ForeignKey(
        "Account", on_delete=models.DO_NOTHING, related_name='to_account')
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
    )

    #  Fields
    transfer_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.pk)


class Transaction(models.Model):

    #  Relationships
    tags = models.ManyToManyField("Tag", blank=True)
    account = models.ForeignKey(
        "Account", on_delete=models.DO_NOTHING,)
    category = models.ForeignKey("Category", on_delete=models.DO_NOTHING)
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
    )

    #  Fields
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.pk)


class Category(models.Model):

    #  Relationships
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
    )

    #  Fields
    category_color = models.CharField(max_length=30, blank=True, null=True)
    category_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f'{self.category_name} (pk={self.pk})'


class Tag(models.Model):

    #  Relationships
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
    )

    #  Fields
    tag_name = models.CharField(max_length=30)
    tag_color = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f'{self.tag_name} (pk={self.pk})'
