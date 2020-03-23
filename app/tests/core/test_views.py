import pytest
import test_helpers

from django.urls import reverse
from django.test import Client


pytestmark = [pytest.mark.django_db]


def tests_Transfer_list_view():
    instance1 = test_helpers.create_core_Transfer()
    instance2 = test_helpers.create_core_Transfer()
    client = Client()
    url = reverse("core_Transfer_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Transfer_create_view():
    from_account = test_helpers.create_core_Account()
    to_account = test_helpers.create_core_Account()
    client = Client()
    url = reverse("core_Transfer_create")
    data = {
        "transfer_amount": 1.0,
        "from_account": from_account.pk,
        "to_account": to_account.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Transfer_detail_view():
    client = Client()
    instance = test_helpers.create_core_Transfer()
    url = reverse("core_Transfer_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Transfer_update_view():
    from_account = test_helpers.create_core_Account()
    to_account = test_helpers.create_core_Account()
    client = Client()
    instance = test_helpers.create_core_Transfer()
    url = reverse("core_Transfer_update", args=[instance.pk, ])
    data = {
        "transfer_amount": 1.0,
        "from_account": from_account.pk,
        "to_account": to_account.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Category_list_view():
    instance1 = test_helpers.create_core_Category()
    instance2 = test_helpers.create_core_Category()
    client = Client()
    url = reverse("core_Category_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Category_create_view():
    company = test_helpers.create_core_Company()
    client = Client()
    url = reverse("core_Category_create")
    data = {
        "category_name": "text",
        "category_color": "text",
        "company": company.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Category_detail_view():
    client = Client()
    instance = test_helpers.create_core_Category()
    url = reverse("core_Category_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Category_update_view():
    company = test_helpers.create_core_Company()
    client = Client()
    instance = test_helpers.create_core_Category()
    url = reverse("core_Category_update", args=[instance.pk, ])
    data = {
        "category_name": "text",
        "category_color": "text",
        "company": company.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Tag_list_view():
    instance1 = test_helpers.create_core_Tag()
    instance2 = test_helpers.create_core_Tag()
    client = Client()
    url = reverse("core_Tag_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Tag_create_view():
    company = test_helpers.create_core_Company()
    client = Client()
    url = reverse("core_Tag_create")
    data = {
        "tag_name": "text",
        "tag_color": "text",
        "company": company.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Tag_detail_view():
    client = Client()
    instance = test_helpers.create_core_Tag()
    url = reverse("core_Tag_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Tag_update_view():
    company = test_helpers.create_core_Company()
    client = Client()
    instance = test_helpers.create_core_Tag()
    url = reverse("core_Tag_update", args=[instance.pk, ])
    data = {
        "tag_name": "text",
        "tag_color": "text",
        "company": company.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Company_list_view():
    instance1 = test_helpers.create_core_Company()
    instance2 = test_helpers.create_core_Company()
    client = Client()
    url = reverse("core_Company_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Company_create_view():
    client = Client()
    url = reverse("core_Company_create")
    data = {
        "company_name": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Company_detail_view():
    client = Client()
    instance = test_helpers.create_core_Company()
    url = reverse("core_Company_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Company_update_view():
    client = Client()
    instance = test_helpers.create_core_Company()
    url = reverse("core_Company_update", args=[instance.pk, ])
    data = {
        "company_name": "text",
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Profile_list_view():
    instance1 = test_helpers.create_core_Profile()
    instance2 = test_helpers.create_core_Profile()
    client = Client()
    url = reverse("core_Profile_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Profile_create_view():
    user = test_helpers.create_User()
    company = test_helpers.create_core_Company()
    client = Client()
    url = reverse("core_Profile_create")
    data = {
        "phone": "text",
        "image": "anImage",
        "first_name": "text",
        "is_admin": True,
        "last_name": "text",
        "company_identificator": "text",
        "phone_confirmed": True,
        "user": user.pk,
        "company": company.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Profile_detail_view():
    client = Client()
    instance = test_helpers.create_core_Profile()
    url = reverse("core_Profile_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Profile_update_view():
    user = test_helpers.create_User()
    company = test_helpers.create_core_Company()
    client = Client()
    instance = test_helpers.create_core_Profile()
    url = reverse("core_Profile_update", args=[instance.pk, ])
    data = {
        "phone": "text",
        "image": "anImage",
        "first_name": "text",
        "is_admin": True,
        "last_name": "text",
        "company_identificator": "text",
        "phone_confirmed": True,
        "user": user.pk,
        "company": company.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Account_list_view():
    instance1 = test_helpers.create_core_Account()
    instance2 = test_helpers.create_core_Account()
    client = Client()
    url = reverse("core_Account_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Account_create_view():
    profile = test_helpers.create_core_Profile()
    client = Client()
    url = reverse("core_Account_create")
    data = {
        "account_color": "text",
        "account_name": "text",
        "balance": 1.0,
        "profile": profile.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Account_detail_view():
    client = Client()
    instance = test_helpers.create_core_Account()
    url = reverse("core_Account_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Account_update_view():
    profile = test_helpers.create_core_Profile()
    client = Client()
    instance = test_helpers.create_core_Account()
    url = reverse("core_Account_update", args=[instance.pk, ])
    data = {
        "account_color": "text",
        "account_name": "text",
        "balance": 1.0,
        "profile": profile.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Transaction_list_view():
    instance1 = test_helpers.create_core_Transaction()
    instance2 = test_helpers.create_core_Transaction()
    client = Client()
    url = reverse("core_Transaction_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Transaction_create_view():
    tags = test_helpers.create_Tag()
    account = test_helpers.create_Account()
    category = test_helpers.create_core_Category()
    client = Client()
    url = reverse("core_Transaction_create")
    data = {
        "transaction_amount": 1.0,
        "tags": tags.pk,
        "account": account.pk,
        "category": category.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Transaction_detail_view():
    client = Client()
    instance = test_helpers.create_core_Transaction()
    url = reverse("core_Transaction_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Transaction_update_view():
    tags = test_helpers.create_Tag()
    account = test_helpers.create_Account()
    category = test_helpers.create_core_Category()
    client = Client()
    instance = test_helpers.create_core_Transaction()
    url = reverse("core_Transaction_update", args=[instance.pk, ])
    data = {
        "transaction_amount": 1.0,
        "tags": tags.pk,
        "account": account.pk,
        "category": category.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Action_list_view():
    instance1 = test_helpers.create_core_Action()
    instance2 = test_helpers.create_core_Action()
    client = Client()
    url = reverse("core_Action_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Action_create_view():
    tags = test_helpers.create_Tag()
    account = test_helpers.create_core_Account()
    client = Client()
    url = reverse("core_Action_create")
    data = {
        "action_amount": 1.0,
        "tags": tags.pk,
        "account": account.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Action_detail_view():
    client = Client()
    instance = test_helpers.create_core_Action()
    url = reverse("core_Action_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Action_update_view():
    tags = test_helpers.create_Tag()
    account = test_helpers.create_core_Account()
    client = Client()
    instance = test_helpers.create_core_Action()
    url = reverse("core_Action_update", args=[instance.pk, ])
    data = {
        "action_amount": 1.0,
        "tags": tags.pk,
        "account": account.pk,
    }
    response = client.post(url, data)
    assert response.status_code == 302
