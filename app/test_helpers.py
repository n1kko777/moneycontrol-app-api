import random
import string

from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from core import models as core_models
from users import models as users_models


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
    defaults["tag_color"] = ""
    defaults["tag_name"] = ""
    if "profile" not in kwargs:
        defaults["profile"] = create_core_Profile()
    defaults.update(**kwargs)
    return core_models.Tag.objects.create(**defaults)


def create_core_Action(**kwargs):
    defaults = {}
    defaults["action_amount"] = ""
    if "account" not in kwargs:
        defaults["account"] = create_core_Account()
    if "tags" not in kwargs:
        defaults["tags"] = create_core_Tag()
    defaults.update(**kwargs)
    return core_models.Action.objects.create(**defaults)


def create_core_Category(**kwargs):
    defaults = {}
    defaults["category_color"] = ""
    defaults["caterory_name"] = ""
    if "profile" not in kwargs:
        defaults["profile"] = create_core_Profile()
    defaults.update(**kwargs)
    return core_models.Category.objects.create(**defaults)


def create_core_Transfer(**kwargs):
    defaults = {}
    defaults["transfer_amount"] = ""
    if "from_account" not in kwargs:
        defaults["from_account"] = create_core_Account()
    if "to_account" not in kwargs:
        defaults["to_account"] = create_core_Account()
    defaults.update(**kwargs)
    return core_models.Transfer.objects.create(**defaults)


def create_core_Profile(**kwargs):
    defaults = {}
    defaults["email_confirmed"] = ""
    defaults["phone_confirmed"] = ""
    defaults["last_name"] = ""
    defaults["first_name"] = ""
    defaults["phone"] = ""
    defaults["image"] = ""
    defaults["email"] = ""
    if "user" not in kwargs:
        defaults["user"] = create_users_CustomUser()
    defaults.update(**kwargs)
    return core_models.Profile.objects.create(**defaults)


def create_core_Account(**kwargs):
    defaults = {}
    defaults["balance"] = ""
    defaults["account_name"] = ""
    defaults["account_color"] = ""
    if "profile" not in kwargs:
        defaults["profile"] = create_core_Profile()
    defaults.update(**kwargs)
    return core_models.Account.objects.create(**defaults)


def create_core_Company(**kwargs):
    defaults = {}
    defaults["company_name"] = ""
    defaults.update(**kwargs)
    return core_models.Company.objects.create(**defaults)


def create_core_Transaction(**kwargs):
    defaults = {}
    defaults["transaction_amount"] = ""
    if "tags" not in kwargs:
        defaults["tags"] = create_core_Tag()
    if "account" not in kwargs:
        defaults["account"] = create_core_Account()
    if "category" not in kwargs:
        defaults["category"] = create_core_Category()
    defaults.update(**kwargs)
    return core_models.Transaction.objects.create(**defaults)


def create_users_CustomUser(**kwargs):
    defaults = {}
    defaults["username"] = "username"
    defaults["email"] = "username@tempurl.com"
    defaults.update(**kwargs)
    return users_models.CustomUser.objects.create(**defaults)
