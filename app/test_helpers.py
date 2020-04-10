import random
import string

from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from core import models as core_models


def random_string(length=10):
    # Create a random string of length length
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def create_User(**kwargs):
    defaults = {
        "username": "%s_username" % random_string(5),
        "email": "%s_username@tempurl.com" % random_string(5),
    }
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


def create_AbstractUser(**kwargs):
    defaults = {
        "username": "%s_username" % random_string(5),
        "email": "%s_username@tempurl.com" % random_string(5),
    }
    defaults.update(**kwargs)
    return AbstractUser.objects.create(**defaults)


def create_AbstractBaseUser(**kwargs):
    defaults = {
        "username": "%s_username" % random_string(5),
        "email": "%s_username@tempurl.com" % random_string(5),
    }
    defaults.update(**kwargs)
    return AbstractBaseUser.objects.create(**defaults)


def create_Group(**kwargs):
    defaults = {
        "name": "%s_group" % random_string(5),
    }
    defaults.update(**kwargs)
    return Group.objects.create(**defaults)


def create_ContentType(**kwargs):
    defaults = {
    }
    defaults.update(**kwargs)
    return ContentType.objects.create(**defaults)


def create_core_Tag(**kwargs):
    defaults = {}
    defaults["tag_name"] = ""
    defaults["is_active"] = ""
    defaults["tag_color"] = ""
    if "company" not in kwargs:
        defaults["company"] = create_core_Company()
    defaults.update(**kwargs)
    return core_models.Tag.objects.create(**defaults)


def create_core_Profile(**kwargs):
    defaults = {}
    defaults["last_name"] = ""
    defaults["first_name"] = ""
    defaults["is_active"] = ""
    defaults["phone_confirmed"] = ""
    defaults["phone"] = ""
    defaults["is_admin"] = ""
    defaults["image"] = ""
    defaults["company_identificator"] = ""
    if "user" not in kwargs:
        defaults["user"] = create_User()
    if "company" not in kwargs:
        defaults["company"] = create_core_Company()
    defaults.update(**kwargs)
    return core_models.Profile.objects.create(**defaults)


def create_core_Company(**kwargs):
    defaults = {}
    defaults["company_name"] = ""
    defaults.update(**kwargs)
    return core_models.Company.objects.create(**defaults)


def create_core_Account(**kwargs):
    defaults = {}
    defaults["account_color"] = ""
    defaults["balance"] = ""
    defaults["is_active"] = ""
    defaults["account_name"] = ""
    if "profile" not in kwargs:
        defaults["profile"] = create_core_Profile()
    defaults.update(**kwargs)
    return core_models.Account.objects.create(**defaults)


def create_core_Category(**kwargs):
    defaults = {}
    defaults["is_active"] = ""
    defaults["category_name"] = ""
    defaults["category_color"] = ""
    if "company" not in kwargs:
        defaults["company"] = create_core_Company()
    defaults.update(**kwargs)
    return core_models.Category.objects.create(**defaults)


def create_core_Transaction(**kwargs):
    defaults = {}
    defaults["is_active"] = ""
    defaults["transaction_amount"] = ""
    if "category" not in kwargs:
        defaults["category"] = create_core_Category()
    if "tags" not in kwargs:
        defaults["tags"] = create_core_Tag()
    if "account" not in kwargs:
        defaults["account"] = create_core_Account()
    defaults.update(**kwargs)
    return core_models.Transaction.objects.create(**defaults)


def create_core_Transfer(**kwargs):
    defaults = {}
    defaults["transfer_amount"] = ""
    defaults["is_active"] = ""
    if "from_account" not in kwargs:
        defaults["from_account"] = create_core_Account()
    if "to_account" not in kwargs:
        defaults["to_account"] = create_core_Account()
    defaults.update(**kwargs)
    return core_models.Transfer.objects.create(**defaults)


def create_core_Action(**kwargs):
    defaults = {}
    defaults["action_amount"] = ""
    defaults["is_active"] = ""
    if "tags" not in kwargs:
        defaults["tags"] = create_core_Tag()
    if "account" not in kwargs:
        defaults["account"] = create_core_Account()
    defaults.update(**kwargs)
    return core_models.Action.objects.create(**defaults)
