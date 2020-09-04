from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from django.test.utils import override_settings
from . import app_settings


CREATE_USER_URL = "/dj-rest-auth/registration/"
TOKEN_URL = "/dj-rest-auth/login/"


def create_user(**params):
    """Helper function to create new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating using with a valid payload is successful"""
        payload = {
            "email": "test@n1kko777.com",
            "password1": "testpn1kko777ass",
            "password2": "testpn1kko777ass",
            "username": "n1kko777"
        }
        res = self.client.post(CREATE_USER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {"username": "n1kko777",
                   "email": "test@n1kko777.com", "password": "testpass"}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more than 5 characters"""
        payload = {"username": "n1kko777",
                   "email": "test@n1kko777.com", "password": "pw"}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exists)

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod
        .OPTIONAL)
    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            "email": "test@n1kko777.com",
            "username": "test",
            "password1": "testn1kko777pass",
            "password2": "testn1kko777pass"
        }

        self.client.post(CREATE_USER_URL, payload)
        res = self.client.post(TOKEN_URL, {
            "email": payload["email"],
            "password": payload["password1"]
        })

        self.assertIn("key", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        self.client.post(CREATE_USER_URL, {
            "email": "test@n1kko777.com",
            "username": "n1kko777",
            "password1": "wrn1kko777ong",
            "password2": "wron1kko777ng"
        })

        payload = {"email": "test@n1kko777.com", "password": "wrong"}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doens"t exist"""
        payload = {"email": "test@n1kko777.com", "password": "testpass"}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {"email": "one", "password": ""})
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
