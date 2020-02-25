from django.contrib.auth import get_user_model
from django.test import TestCase


from core.models import Account


def sample_account(user, **params):
    """Create and return a sample customer"""
    defaults = {}
    defaults.update(params)

    return Account.objects.create(user=user, **defaults)


class TestServices(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@londonappdev.com',
            password='testpass',
            username='test'
        )

        self.account = sample_account(user=self.user)
        self.account.balance = 1000
        self.account.save()
