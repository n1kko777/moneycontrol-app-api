from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from core import models

from faker import Faker
fake = Faker(['ru_RU'])


def sample_user():
    """Create a sample user"""
    return get_user_model()\
        .objects.\
        create_user({'email': fake.email(), 'password': fake.password()})


def sample_profile():
    user = sample_user()
    """Create a sample profile"""
    return models.Profile.objects.create(
        user=user,
        company=None,
        first_name=fake.name().split(" ")[0],
        last_name=fake.name().split(" ")[0],
        phone=fake.phone_number(),
        phone_confirmed=False,
        image=None,
        is_admin=False,
        is_active=True,
        company_identificator=None
    )


class ModelTest(TestCase):

    def test_company_str(self):
        """Test the company string representation"""

        company = models.Company.objects.create(company_name="Test Company")

        self.assertEqual(
            str(company), f'{company.company_name} (pk={company.pk})')

    def test_profile_str(self):
        """Test the profile string representation"""
        profile = sample_profile()

        self.assertEqual(
            str(profile),
            f'{profile.first_name} {profile.last_name} (id={profile.id})')

    @patch('uuid.uuid4')
    def test_profile_file_name_uuid(self, mock_uuid):
        """Test that the image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.customer_image_file_path(None, 'myimage.jpg')

        exp_path = f'upload/customer/{uuid}.jpg'

        self.assertEqual(file_path, exp_path)

    def test_account_str(self):
        """Test the account string representation"""
        profile = sample_profile()

        account1 = models.Account.objects.create(
            profile=profile,
            company=models.Company.objects.create(company_name="Test Company"),
            balance=0,
            account_name='Test',
        )

        account2 = models.Account.objects.create(
            profile=profile,
            company=models.Company.objects.create(company_name="Test Company"),
            balance=2000.32,
            account_name='Test',
        )

        self.assertEqual(
            str(account1), f'{account1.account_name} (pk={account1.pk})')
        self.assertEqual(
            str(account2), f'{account2.account_name} (pk={account2.pk})')

    def test_action_str(self):
        """Test the action string representation"""

        profile = sample_profile()
        company = models.Company.objects.create(company_name="Test Company")

        account = models.Account.objects.create(
            profile=profile,
            company=company,
            balance=0,
            account_name='Test',
        )

        action = models.Action.objects.create(
            account=account,
            category=models.Category.objects.create(
                category_name="test", company=company),
            company=company,
            action_amount=124,
        )

        action.tags.add(models.Tag.objects.create(
            tag_name="test", company=company))

        self.assertEqual(
            str(action), str(action.pk))

    def test_transaction_str(self):
        """Test the transaction string representation"""

        profile = sample_profile()
        company = models.Company.objects.create(company_name="Test Company")

        account = models.Account.objects.create(
            profile=profile,
            company=company,
            balance=0,
            account_name='Test',
        )

        transaction = models.Transaction.objects.create(
            account=account,
            category=models.Category.objects.create(
                category_name="test", company=company),
            company=company,
            transaction_amount=124,
        )

        transaction.tags.add(models.Tag.objects.create(
            tag_name="test", company=company))

        self.assertEqual(
            str(transaction), str(transaction.pk))

    def test_make_transaction_success(self):
        """Make succesful transaction"""
        profile = sample_profile()
        company = models.Company.objects.create(company_name="Test Company")
        profile.company = company
        profile.company_identificator = company.company_id
        profile.is_admin = True
        profile.save()

        initial_balance = 1000
        trans_amount = 500

        account = models.Account.objects.create(
            profile=profile,
            company=company,
            balance=initial_balance,
            account_name='Test',
        )

        models.Transaction.make_transaction(
            transaction_amount=trans_amount,
            account=account,
            category=models.Category.objects.create(
                category_name="test", company=company),
            tags=[],
            merchant='bk'
        )

        account.refresh_from_db()

        expected_balance = initial_balance - trans_amount

        transactions = models.Transaction.objects.all()

        self.assertEqual(expected_balance, account.balance)
        self.assertEqual(len(transactions), 1)

    def test_transfer_str(self):
        """Test the transfer string representation"""

        profile = sample_profile()
        company = models.Company.objects.create(company_name="Test Company")

        transfer_amount = 10000

        from_account = models.Account.objects.create(
            profile=profile,
            company=company,
            balance=transfer_amount,
            account_name='Test',
        )

        to_account = models.Account.objects.create(
            profile=profile,
            company=company,
            balance=0,
            account_name='Test1',
        )

        transfer = models.Transfer.objects.create(
            from_account=from_account,
            to_account=to_account,
            company=company,
            transfer_amount=transfer_amount
        )

        self.assertEqual(
            str(transfer), str(transfer.pk))

    def test_category_str(self):
        """Test the category string representation"""

        category = models.Category.objects.create(
            company=models.Company.objects.create(company_name="Test Company"),
            category_name="Test"
        )

        self.assertEqual(
            str(category), f'{category.category_name} (pk={category.pk})')

    def test_tag_str(self):
        """Test the tag string representation"""

        tag = models.Tag.objects.create(
            company=models.Company.objects.create(company_name="Test Company"),
            tag_name="Test"
        )

        self.assertEqual(
            str(tag), f'{tag.tag_name} (pk={tag.pk})')
