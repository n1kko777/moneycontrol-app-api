from core.models import Profile, Company, Account

import random

from faker import Faker
fake = Faker()

ACCOUNT_URL = '/api/v1/account/'
PROFILE_URL = '/api/v1/profile/'
COMPANY_URL = '/api/v1/company/'

ACTION_URL = '/api/v1/action/'
TRANSACTION_URL = '/api/v1/transaction/'
TRANSFER_URL = '/api/v1/transfer/'

CATEGORY_URL = '/api/v1/category/'
TAG_URL = '/api/v1/tag/'

JOIN_COMPANY_URL = '/api/v1/join-profile-to-company/'
REMOVE_COMPANY_URL = '/api/v1/remove-profile-from-company/'

HOMELIST_URL = '/api/v1/home-list/'


def phn():
    n = '0000000000'
    while '9' in n[3:6] or n[3:6] == '000' or n[6] == n[7] == n[8] == n[9]:
        n = str(random.randint(10**9, 10**10-1))
    return n


def sample_profile(user, **params):
    """Create and return a sample profile"""
    defaults = {
        "first_name": fake.name().split(' ')[0],
        "last_name": fake.name().split(' ')[1],
        "phone": f'{phn()}',
        "image": None
    }
    defaults.update(params)

    return Profile.objects.create(user=user, **defaults)


def sample_company(self):
    """Create and return a sample company"""
    payload = {
        "company_name": fake.name()
    }

    res = self.client.post(COMPANY_URL, payload)

    return Company.objects.get(id=res.data['id'])


def sample_account(self, profile, company, **params):
    """Create and return a sample customer"""
    defaults = {
        "balance": 0,
        "account_name": "string",
        "account_color": "string"
    }

    defaults.update(params)

    return Account.objects.create(
        profile=profile,
        company=company,
        **defaults
    )
