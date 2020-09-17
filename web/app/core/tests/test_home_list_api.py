from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Category
from .helper import sample_profile, \
    sample_company, \
    sample_account, \
    fake, \
    HOMELIST_URL, \
    ACTION_URL, \
    COMPANY_URL


class PublicCoreApiTest(TestCase):
    """Test unauthenticated recipe API request"""

    def setUp(self):
        self.client = APIClient()

    def test_home_list_auth_required(self):
        res = self.client.post(HOMELIST_URL)
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

    def test_get_home_list_data_no_company(self):
        user2 = get_user_model().objects.create_user(
            email='other@gleb.com',
            password='otherpass',
            username='test_1'
        )
        sample_profile(user=user2)
        client2 = APIClient()
        client2.force_authenticate(user=user2)

        res = client2.post(HOMELIST_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_home_list_data_other_company(self):
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

        res = client2.post(HOMELIST_URL, {
            "profile_id": self.profile.id
        })

        profile2.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertFalse(profile2.company.id == self.profile.company.id)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_home_list_data(self):
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
            "action_amount": 100,
            "company": self.company.id,
            "category": self.category.id
        }

        client2.post(ACTION_URL, payload)

        res = self.client.post(HOMELIST_URL)
        self.account.refresh_from_db()
        account2.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['balance'],
                         self.account.balance + account2.balance)
