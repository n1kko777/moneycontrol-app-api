from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Profile, Company, Category
from core.serializers import CategorySerializer

from faker import Faker
import random


fake = Faker()

PROFILE_URL = '/api/v1/profile/'
COMPANY_URL = '/api/v1/company/'

CATEGORY_URL = '/api/v1/category/'


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


class PublicCoreApiTest(TestCase):
    """Test unauthenticated recipe API request"""

    def setUp(self):
        self.client = APIClient()

    def test_category_auth_required(self):
        res = self.client.get(CATEGORY_URL)
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

    def test_retreive_categorys(self):
        Category.objects.create(
            category_name=fake.name(),
            company=self.company
        )

        res = self.client.get(CATEGORY_URL)

        categorys = Category.objects.all().order_by('-id')

        serializer = CategorySerializer(categorys, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_category(self):
        payload = {
            "category_name": fake.name(),
        }

        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(res.data['id'], Category.objects.get().id)

    def test_update_category(self):
        payload = {
            "category_name": fake.name(),
        }

        self.client.post(CATEGORY_URL, payload)

        new_category_name = fake.name()
        res = self.client.put(f"{CATEGORY_URL}{Category.objects.get().id}/", {
            "category_name": new_category_name,
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['category_name'], new_category_name)

    def test_create_category_with_same_name(self):
        new_category_name = fake.name()

        payload = {
            "category_name": new_category_name,
        }

        self.client.post(CATEGORY_URL, payload)

        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_category_with_same_name(self):
        new_category_name = fake.name()

        payload = {
            "category_name": new_category_name,
        }

        self.client.post(CATEGORY_URL, payload)
        new_res = self.client.post(CATEGORY_URL, {
            "category_name": fake.name(),
        })

        res = self.client.put(
            f"{CATEGORY_URL}{new_res.data['id']}/", payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_category(self):
        payload = {
            "category_name": fake.name(),
        }

        self.client.post(CATEGORY_URL, payload)

        res = self.client.delete(f"{CATEGORY_URL}{Category.objects.get().id}/")

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
