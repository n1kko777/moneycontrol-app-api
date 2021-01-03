import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Category, Transaction
from .helper import sample_profile, \
    sample_company, \
    sample_account, \
    fake, \
    OPERATION_URL, \
    TRANSACTION_URL, \
    COMPANY_URL


class PublicCoreApiTest(TestCase):
    """Test unauthenticated recipe API request"""

    def setUp(self):
        self.client = APIClient()

    def test_operation_list_auth_required(self):
        res = self.client.get(OPERATION_URL)
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

    def test_get_operation_list_data_no_company(self):
        user2 = get_user_model().objects.create_user(
            email='other@gleb.com',
            password='otherpass',
            username='test_1'
        )
        sample_profile(user=user2)
        client2 = APIClient()
        client2.force_authenticate(user=user2)

        res = client2.get(OPERATION_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_operation_list_data_other_company(self):
        user2 = get_user_model().objects.create_user(
            email='other@gleb.com',
            password='otherpass',
            username='test_1'
        )

        client2 = APIClient()
        client2.force_authenticate(user=user2)

        profile2 = sample_profile(user=user2)

        payload = {
            "company_name": fake.name()
        }

        client2.post(COMPANY_URL, payload)

        res = client2.get(f"{OPERATION_URL}?profile_id={self.profile.id}")

        profile2.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertFalse(profile2.company.id == self.profile.company.id)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_operation_list_admin_access(self):
        user2 = get_user_model().objects.create_user(
            email='other@gleb.com',
            password='otherpass',
            username='test_1'
        )

        client2 = APIClient()
        client2.force_authenticate(user=user2)

        profile2 = sample_profile(user=user2)

        payload = {
            "company_name": fake.name()
        }

        client2.post(COMPANY_URL, payload)

        client2.post('/api/v1/join-profile-to-company/', {
            'profile_id': self.profile.id,
            'profile_phone': self.profile.phone
        }, format="json")
        self.profile.refresh_from_db()
        profile2.refresh_from_db()

        res = self.client.get(f"{OPERATION_URL}?profile_id={profile2.id}")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_operation_list_no_date(self):
        user2 = get_user_model().objects.create_user(
            email='other@gleb.com',
            password='otherpass',
            username='test_1'
        )

        client2 = APIClient()
        client2.force_authenticate(user=user2)

        profile2 = sample_profile(user=user2)

        payload = {
            "company_name": fake.name()
        }

        client2.post(COMPANY_URL, payload)

        client2.post('/api/v1/join-profile-to-company/', {
            'profile_id': self.profile.id,
            'profile_phone': self.profile.phone
        }, format="json")
        self.profile.refresh_from_db()
        profile2.refresh_from_db()

        res = self.client.get(OPERATION_URL)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_operation_list_data(self):
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

        trans_req = client2.post(TRANSACTION_URL, {
            "transaction_amount": 100,
            "account": account2.id,
            "company": self.company.id,
            "category": self.category.id
        })

        self.assertEqual(trans_req.status_code, status.HTTP_201_CREATED)

        trans = Transaction.objects.get(id=trans_req.data['id'])

        today = datetime.datetime.utcnow()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)

        res = self.client.get(
            f'{OPERATION_URL}?start_date={yesterday}&end_date={tomorrow}'
        )
        self.account.refresh_from_db()
        account2.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data['data']) > 0)
        self.assertEqual(trans.last_updated.strftime(
            '%d.%m.%Y'), res.data['data'][0]['title'])
        self.assertEqual(trans.id, res.data['data'][0]['data'][0]['id'])
