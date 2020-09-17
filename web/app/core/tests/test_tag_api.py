from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from core.serializers import TagSerializer
from .helper import sample_profile, \
    sample_company, \
    fake, \
    TAG_URL


class PublicCoreApiTest(TestCase):
    """Test unauthenticated recipe API request"""

    def setUp(self):
        self.client = APIClient()

    def test_tag_auth_required(self):
        res = self.client.get(TAG_URL)
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

    def test_retreive_tags(self):
        Tag.objects.create(
            tag_name=fake.name(),
            company=self.company
        )

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-id')

        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_tag(self):
        payload = {
            "tag_name": fake.name(),
        }

        res = self.client.post(TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(res.data['id'], Tag.objects.get().id)

    def test_update_tag(self):
        payload = {
            "tag_name": fake.name(),
        }

        self.client.post(TAG_URL, payload)

        new_tag_name = fake.name()
        res = self.client.put(f"{TAG_URL}{Tag.objects.get().id}/", {
            "tag_name": new_tag_name,
        })

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['tag_name'], new_tag_name)

    def test_create_tag_with_same_name(self):
        new_tag_name = fake.name()

        payload = {
            "tag_name": new_tag_name,
        }

        self.client.post(TAG_URL, payload)

        res = self.client.post(TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_tag_with_same_name(self):
        new_tag_name = fake.name()

        payload = {
            "tag_name": new_tag_name,
        }

        self.client.post(TAG_URL, payload)
        new_res = self.client.post(TAG_URL, {
            "tag_name": fake.name(),
        })

        res = self.client.put(
            f"{TAG_URL}{new_res.data['id']}/", payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_tag(self):
        payload = {
            "tag_name": fake.name(),
        }

        self.client.post(TAG_URL, payload)

        res = self.client.delete(f"{TAG_URL}{Tag.objects.get().id}/")

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
