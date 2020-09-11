from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Profile, Company
from core.serializers import CompanySerializer

from faker import Faker
import random

fake = Faker()

PROFILE_URL = '/api/v1/profile/'
COMPANY_URL = '/api/v1/company/'
JOIN_COMPANY_URL = '/api/v1/join-profile-to-company/'
REMOVE_COMPANY_URL = '/api/v1/remove-profile-from-company/'


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
    sample_profile(user=self.user)

    payload = {
        "company_name": fake.name()
    }

    res = self.client.post(COMPANY_URL, payload)

    return Company.objects.get(id=res.data['id'])


class PublicCoreApiTest(TestCase):
    """Test unauthenticated mncntrl API request"""

    def setUp(self):
        self.client = APIClient()

    def test_company_auth_required(self):
        """Test no unauthenticated User"""

        res = self.client.get(COMPANY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCompanyApiTests(TestCase):
    """Test authenticated API access"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@n1kko777-dev.ru',
            password='testpass',
            username='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retreive_company(self):
        """Test retreiving a company"""
        sample_company(self)

        res = self.client.get(COMPANY_URL)

        company = Company.objects.all().order_by('-id')

        serializer = CompanySerializer(company, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0], serializer.data[0])

    def test_create_company(self):
        """Test creating company"""
        profile = sample_profile(user=self.user)

        payload = {
            "company_name": fake.name()
        }

        res = self.client.post(COMPANY_URL, payload)
        profile.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['id'], profile.company.pk)
        self.assertEqual(res.data['company_id'], profile.company_identificator)

    def test_update_company(self):
        """Test company update with put"""
        profile = sample_profile(user=self.user)
        company = self.client.post(COMPANY_URL, {
            "company_name": "test_create"
        })

        payload = {
            "company_name": "test_update"
        }

        res = self.client.put(
            COMPANY_URL + str(company.data['id']) + "/", payload)
        profile.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.is_admin, True)
        self.assertEqual(res.data['company_id'], profile.company_identificator)

    def test_join_profile_to_company(self):
        """Invite profile to company"""
        user2 = get_user_model().objects.create_user(
            email='other@gleb.com',
            password='otherpass',
            username='test_1'
        )

        client1 = APIClient()
        client1.force_authenticate(user=self.user)
        profile1 = sample_profile(user=self.user)

        client2 = APIClient()
        client2.force_authenticate(user=user2)
        profile2 = sample_profile(user=user2)

        payload = {
            "company_name": "test_update"
        }

        res = client1.post(COMPANY_URL, payload)
        res_join = client1.post(JOIN_COMPANY_URL, {
            'profile_id': profile2.id,
            'profile_phone': profile2.phone
        }, format="json")
        profile1.refresh_from_db()
        profile2.refresh_from_db()

        res_get = client1.get('/api/v1/profile/')

        self.assertEqual(res_join.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], profile2.company.id)
        self.assertEqual(res.data['company_id'],
                         profile2.company_identificator)
        self.assertEqual(profile2.is_admin, False)
        self.assertEqual(len(res_get.data), 2)

    def test_remove_profile_from_company(self):
        """Remove profile from company"""
        user2 = get_user_model().objects.create_user(
            email='other@gleb.com',
            password='otherpass',
            username='test_1'
        )

        client1 = APIClient()
        client1.force_authenticate(user=self.user)
        profile1 = sample_profile(user=self.user)

        client2 = APIClient()
        client2.force_authenticate(user=user2)
        profile2 = sample_profile(user=user2)

        payload = {
            "company_name": "test_update"
        }

        client1.post(COMPANY_URL, payload)
        client1.post(JOIN_COMPANY_URL, {
            'profile_id': profile2.id,
            'profile_phone': profile2.phone
        }, format="json")
        profile1.refresh_from_db()
        profile2.refresh_from_db()

        res_remove = client1.post(REMOVE_COMPANY_URL, {
            'profile_id': profile2.id,
            'profile_phone': profile2.phone
        }, format="json")
        profile1.refresh_from_db()
        profile2.refresh_from_db()

        res_get = client1.get('/api/v1/profile/')

        self.assertEqual(res_remove.status_code, status.HTTP_200_OK)
        self.assertEqual(profile2.company, None)
        self.assertEqual(profile2.company_identificator, None)
        self.assertEqual(profile1.is_admin, True)
        self.assertEqual(len(res_get.data), 1)
