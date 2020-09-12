from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Transaction, Profile, Company, Account, Category, Tag
from core.serializers import TransactionSerializer

from faker import Faker
import random


fake = Faker()

ACCOUNT_URL = '/api/v1/account/'
PROFILE_URL = '/api/v1/profile/'
COMPANY_URL = '/api/v1/company/'

TRANSACTION_URL = '/api/v1/transaction/'


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


class PublicCoreApiTest(TestCase):
    """Test unauthenticated recipe API request"""

    def setUp(self):
        self.client = APIClient()

    def test_account_auth_required(self):
        res = self.client.get(TRANSACTION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCustomerApiTests(TestCase):
    """Test authenticated API access"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@londonappdev.com',
            password='testpass',
            username='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.profile = sample_profile(user=self.user)
        self.company = sample_company(self)
        self.category = Category.objects.create(
            category_name="test category", company=self.company)
        self.account = sample_account(
            self=self,
            profile=self.profile,
            company=self.company
        )

        self.account.balance = 1000
        self.account.save()

    def test_retreive_transactions(self):
        req_tag = self.client.post('/api/v1/tag/', {
            "tag_name": "test tag",
            "company": self.company
        })
        tag = Tag.objects.get(id=req_tag.data['id'])

        transaction = Transaction.objects.create(
            account=self.account,
            company=self.company,
            transaction_amount=500,
            category=self.category,
        )

        transaction.tags.set([tag])
        transaction.save()

        res = self.client.get(TRANSACTION_URL)

        transactions = Transaction.objects.all().order_by('-id')

        serializer = TransactionSerializer(transactions, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_make_transaction(self):
        payload = {
            "account": self.account.id,
            "transaction_amount": 100,
            "company": self.company.id,
            "category": self.category.id
        }

        balance_before = self.account.balance

        res = self.client.post(TRANSACTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.account.refresh_from_db()

        balance_after = self.account.balance

        self.assertEqual(payload['transaction_amount'],
                         balance_before - balance_after)

        transaction = Transaction.objects.get(id=res.data['id'])

        self.assertEqual(payload['account'], transaction.account.id)
        self.assertEqual(payload['transaction_amount'],
                         transaction.transaction_amount)

    def test_make_withdraw(self):
        payload = {
            "account": self.account.id,
            "transaction_amount": -100,
            "company": self.company.id,
            "category": self.category.id
        }

        self.account.balance = 1000
        self.account.save()
        balance_before = self.account.balance

        res = self.client.post(TRANSACTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.account.refresh_from_db()

        balance_after = self.account.balance

        self.assertEqual(payload['transaction_amount'],
                         balance_before - balance_after)

        transaction = Transaction.objects.get(id=res.data['id'])

        self.assertEqual(payload['account'], transaction.account.id)
        self.assertEqual(payload['transaction_amount'],
                         transaction.transaction_amount)

    def test_admin_can_access_transaction_other_team_member(self):
        user2 = get_user_model().objects.create_user(
            email='other@gleb.com',
            password='otherpass',
            username='test_1'
        )
        profile2 = sample_profile(user=user2)
        account2 = sample_account(
            self=self,
            profile=profile2,
            company=self.company
        )
        self.client.post('/api/v1/join-profile-to-company/', {
            'profile_id': profile2.id,
            'profile_phone': profile2.phone
        }, format="json")
        profile2.refresh_from_db()

        client2 = APIClient()
        client2.force_authenticate(user=user2)

        payload = {
            "account": account2.id,
            "transaction_amount": 100,
            "company": self.company.id,
            "category": self.category.id
        }

        client2.post(TRANSACTION_URL, payload)

        res = self.client.get(TRANSACTION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
