from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Account
from core.serializers import AccountSerializer
from .helper import sample_profile, sample_company, sample_account, ACCOUNT_URL


class PublicCoreApiTest(TestCase):
    """Test unauthenticated recipe API request"""

    def setUp(self):
        self.client = APIClient()

    def test_account_auth_required(self):
        res = self.client.get(ACCOUNT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCustomerApiTests(TestCase):
    """Test authenticated API access"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@n1kko777-dev.ru',
            password='testpass',
            username='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retreive_account(self):
        profile = sample_profile(self.user)
        company = sample_company(self)

        sample_account(self, profile, company)

        res = self.client.get(ACCOUNT_URL)

        account = Account.objects.all().order_by('-id')

        serializer = AccountSerializer(account, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_account(self):
        profile = sample_profile(self.user)
        company = sample_company(self)

        payload = {
            "balance": 0,
            "account_name": "string",
            "account_color": "string",
            "profile": profile,
            "company": company
        }
        res = self.client.post(ACCOUNT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        account = Account.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(account, key))

    def test_full_update_account(self):
        profile = sample_profile(self.user)
        company = sample_company(self)
        account = sample_account(self, profile, company)
        url = ACCOUNT_URL + str(account.id) + '/'

        payload = {
            "balance": 120,
            "account_name": "string123",
            "account_color": "string",
            "profile": profile,
            "company": company
        }

        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_admin_not_access_account_other_team_member(self):
        """Test unauthenticated recipe API request"""

        user2 = get_user_model().objects.create_user(
            email='other@gleb.com',
            password='otherpass',
            username='test_1'
        )

        client1 = APIClient()
        client1.force_authenticate(user=self.user)

        profile1 = sample_profile(user=self.user)
        company = sample_company(self)

        sample_account(self, profile1, company)

        client2 = APIClient()
        client2.force_authenticate(user=user2)
        profile2 = sample_profile(user=user2)

        client1.post('/api/v1/join-profile-to-company/', {
            'profile_id': profile2.id,
            'profile_phone': profile2.phone
        }, format="json")
        profile1.refresh_from_db()
        sample_account(self, profile2, company)

        res = client1.get(ACCOUNT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
