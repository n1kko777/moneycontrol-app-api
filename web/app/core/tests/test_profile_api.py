import os
import tempfile

from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Profile
from core.serializers import ProfileSerializer

from faker import Faker
import random

fake = Faker()

PROFILE_URL = '/api/v1/profile/'


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


class PublicCoreApiTest(TestCase):
    """Test unauthenticated mncntrl API request"""

    def setUp(self):
        self.client = APIClient()

    def test_profile_auth_required(self):
        """Test no unauthenticated User"""

        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProfileApiTests(TestCase):
    """Test authenticated API access"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@n1kko777-dev.ru',
            password='testpass',
            username='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retreive_profile(self):
        """Test retreiving a profile"""
        sample_profile(user=self.user)

        res = self.client.get(PROFILE_URL)

        profile = Profile.objects.all().order_by('-id')

        serializer = ProfileSerializer(profile, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0], serializer.data[0])

    def test_profile_limited_to_user(self):
        """Test retrieving profile for user"""
        user2 = get_user_model().objects.create_user(
            email='other@gleb.com',
            password='otherpass',
            username='test_1'
        )
        sample_profile(user=user2)
        sample_profile(user=self.user)

        res = self.client.get(PROFILE_URL)

        profiles = Profile.objects.filter(user=self.user)

        serializer = ProfileSerializer(profiles, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0], serializer.data[0])

    def test_create_profile(self):
        """Test creating profile"""
        payload = {
            "first_name": fake.name().split(' ')[0],
            "last_name": fake.name().split(' ')[1],
            "phone": f'{phn()}',
        }
        res = self.client.post(PROFILE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_profile_with_image(self):
        """Test creating profile"""

        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            payload = {
                "first_name": fake.name().split(' ')[0],
                "last_name": fake.name().split(' ')[1],
                "phone": f'{phn()}',
                "image": ntf
            }

            res = self.client.post(PROFILE_URL, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        profile = Profile.objects.get(id=res.data['id'])
        for key in payload.keys():
            if key != 'image':
                self.assertEqual(payload[key], getattr(profile, key))

        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(profile.image.path))
        profile.image.delete()


def test_update_profile(self):
    """Test profile update with put"""
    # create profile with image
    with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
        img = Image.new('RGB', (10, 10))
        img.save(ntf, format='JPEG')
        ntf.seek(0)

        profile = sample_profile(user=self.user)
        profile.image.save('abc.jpg', ntf)

    # full update
    with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
        img = Image.new('RGB', (10, 10))
        img.save(ntf, format='JPEG')
        ntf.seek(0)
        payload = {
            "first_name": fake.name().split(' ')[0],
            "last_name": fake.name().split(' ')[1],
            "phone": f'{phn()}',
            "image": ntf
        }

        res = self.client.put(
            f"{PROFILE_URL}{profile.id}/", payload, format='multipart')

    self.assertEqual(res.status_code, status.HTTP_200_OK)

    profile.refresh_from_db()

    self.assertEqual(profile.phone, payload['phone'])
    self.assertTrue(os.path.exists(profile.image.path))
    profile.image.delete()

    try:
        os.remove("/vol/web/media/upload/profile/abc.jpg")
    except Exception as e:
        if e:
            pass
