from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Transfer, Profile, Company, Account
from core.serializers import TransferSerializer

from faker import Faker
import random


fake = Faker()

ACCOUNT_URL = '/api/v1/account/'
PROFILE_URL = '/api/v1/profile/'
COMPANY_URL = '/api/v1/company/'

TRANSFER_URL = '/api/v1/transfer/'


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
        "account_name": fake.name(),
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
        res = self.client.get(TRANSFER_URL)
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

        self.account1 = sample_account(
            self=self,
            profile=self.profile,
            company=self.company
        )
        self.account2 = sample_account(
            self=self,
            profile=self.profile,
            company=self.company
        )

        self.account1.balance = 1000
        self.account1.save()

    def test_retreive_transfers(self):
        Transfer.objects.create(
            from_account=self.account1,
            to_account=self.account2,
            transfer_amount=100,
            company=self.company,
        )

        res = self.client.get(TRANSFER_URL)

        transfers = Transfer.objects.all().order_by('-id')

        serializer = TransferSerializer(transfers, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_make_transfer_other_self(self):
        """ Transfer from self account to another self account """

        payload = {
            "from_account": self.account1.id,
            "to_account": self.account2.id,
            "transfer_amount": 10,
            "company": self.company.id
        }

        balance_before1 = self.account1.balance
        balance_before2 = self.account2.balance

        res = self.client.post(TRANSFER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.account1.refresh_from_db()
        self.account2.refresh_from_db()

        balance_after1 = self.account1.balance
        balance_after2 = self.account2.balance

        self.assertEqual(payload['transfer_amount'],
                         balance_before1 - balance_after1)
        self.assertEqual(payload['transfer_amount'],
                         balance_after2 - balance_before2)

        transfer = Transfer.objects.get(id=res.data['id'])

        self.assertEqual(len(Transfer.objects.all()), 1)

        self.assertEqual(payload['from_account'], transfer.from_account.id)
        self.assertEqual(payload['to_account'], transfer.to_account.id)
        self.assertEqual(payload['transfer_amount'],
                         transfer.transfer_amount)

    def test_make_transfer_same_self(self):
        """ Transfer from self account to same self account """

        payload = {
            "from_account": self.account1.id,
            "to_account": self.account1.id,
            "transfer_amount": 10,
            "company": self.company.id
        }

        res = self.client.post(TRANSFER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_make_transfer_other_member(self):
        """ Transfer from self account to another member account """
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

        payload = {
            "from_account": self.account1.id,
            "to_account": account2.id,
            "transfer_amount": 100,
            "company": self.company.id
        }

        balance_before1 = self.account1.balance
        balance_before2 = account2.balance

        res = self.client.post(TRANSFER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.account1.refresh_from_db()
        account2.refresh_from_db()

        balance_after1 = self.account1.balance
        balance_after2 = account2.balance

        self.assertEqual(payload['transfer_amount'],
                         balance_before1 - balance_after1)
        self.assertEqual(payload['transfer_amount'],
                         balance_after2 - balance_before2)

        transfer = Transfer.objects.get(id=res.data['id'])

        self.assertEqual(len(Transfer.objects.all()), 1)

        self.assertEqual(payload['from_account'], transfer.from_account.id)
        self.assertEqual(payload['to_account'], transfer.to_account.id)
        self.assertEqual(payload['transfer_amount'],
                         transfer.transfer_amount)

    def test_admin_can_access_transfer_other_team_member(self):
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
            "from_account": account2.id,
            "to_account": self.account1.id,
            "transfer_amount": 100,
            "company": self.company.id
        }

        client2.post(TRANSFER_URL, payload)

        res = self.client.get(TRANSFER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
