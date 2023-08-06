from django.db.models import Sum
from django.db.models.functions import Coalesce

from rest_framework import status, schemas
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from operator import itemgetter

import coreapi
import coreschema

from core.mixins import ServiceExceptionHandlerMixin
from core import models


class HomeListViewSchema(schemas.AutoSchema):

    def get_manual_fields(self, path, method):
        extra_fields = []

        if method.lower() in ['get', ]:
            extra_fields = [
                coreapi.Field(
                    name='profile_id',
                    location='query',
                    schema=coreschema.String()
                )
            ]

        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class HomeListView(ServiceExceptionHandlerMixin, APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    schema = HomeListViewSchema()

    def get_error_response(self, detail):
        return Response({
            "detail": detail
        }, status=status.HTTP_400_BAD_REQUEST)

    def get_action_name(self, action):
        if action.account.profile.company.profiles.count() > 1:
            return f"{action.account.profile.first_name[:1]}. {action.account.profile.last_name} ({action.account.account_name})"
        else:
            return action.account.account_name

    def get_transaction_name(self, transaction):
        if transaction.account.profile.company.profiles.count() > 1:
            return f"{transaction.account.profile.first_name[:1]}. {transaction.account.profile.last_name} ({transaction.account.account_name})"
        else:
            return transaction.account.account_name

    def get_transfer_name(self, transfer):
        if transfer.from_account.profile.company.profiles.count() > 1:
            return (f"{transfer.from_account.profile.first_name[:1]}. {transfer.from_account.profile.last_name} "
                    f"({transfer.from_account.account_name}) => "
                    f"{transfer.to_account.profile.first_name[:1]}. {transfer.to_account.profile.last_name} "
                    f"({transfer.to_account.account_name})")
        else:
            return f"{transfer.from_account.account_name} => {transfer.to_account.account_name}"

    def get(self, request):
        req_profile = None
        profile_queryset = models.Profile.objects.select_related('company')

        if 'profile_id' in request.query_params:
            req_profile = profile_queryset.filter(
                id=self.request.query_params['profile_id'],
                company__profiles=self.request.user.profile
            ).first()

            if not req_profile:
                return self.get_error_response("Указанный профиль не содержится в Вашей компании.")

            if not req_profile.is_admin:
                return self.get_error_response("Невозможно получить данные пользователя.")
        else:
            req_profile = profile_queryset.get(user=self.request.user)

        company = req_profile.company

        if not company:
            return self.get_error_response("Сначала необходимо создать компанию или присоединиться к ней.")

        accounts = models.Account.objects.filter(company=company)
        layout_accounts = models.Account.objects.filter(
            profile=req_profile).order_by('-last_updated')[:5]

        account_data = {
            'navigate': "CreateAccount",
            'title': "Счета",
            'data': [],
        }

        for item in layout_accounts:
            new_item = {
                'id': item.id,
                'name': item.account_name,
                'balance': item.balance,
                'last_updated': item.last_updated,
                'type': "account",
            }
            account_data['data'].append(new_item)

        data = [account_data]

        if 'profile_id' not in request.query_params and req_profile.is_admin and company.profiles.count() > 1:
            profile_data = {
                'navigate': "CreateTeam",
                'title': "Команда",
                'data': [],
            }

            profiles = company.profiles.order_by('id')[:5]

            for item in profiles:
                balance_sum = models.Account.objects.filter(profile=item).aggregate(
                    balance__sum=Coalesce(Sum('balance'), 0)
                )['balance__sum']

                new_item = {
                    'id': item.id,
                    'name': f"{item.first_name} {item.last_name}",
                    'balance': balance_sum,
                    'last_updated': item.last_updated,
                    'type': "profile",
                }
                profile_data['data'].append(new_item)

            data.append(profile_data)

        category_data = {
            'navigate': "CreateCategory",
            'title': "Категории",
            'data': [],
        }

        categories = models.Category.objects.filter(
            company=company).order_by('-last_updated')[:5]

        for item in categories:
            new_item = {
                'id': item.id,
                'name': item.category_name,
                'balance': "",
                'last_updated': item.last_updated,
                'type': "category",
            }
            category_data['data'].append(new_item)

        data.append(category_data)

        tag_data = {
            'navigate': "CreateTag",
            'title': "Теги",
            'data': [],
        }

        tags = models.Tag.objects.filter(
            company=company).order_by('-last_updated')[:5]

        for item in tags:
            new_item = {
                'id': item.id,
                'name': item.tag_name,
                'balance': "",
                'last_updated': item.last_updated,
                'type': "tag",
            }
            tag_data['data'].append(new_item)

        data.append(tag_data)
        operation_data = {
            'navigate': "Operation",
            'title': "Последние операции",
            'data': [],
        }

        actions = models.Action.objects.filter(account__in=accounts)

        for item in actions:
            new_item = {
                'id': item.id,
                'name': self.get_action_name(item),
                'balance': item.action_amount, 'last_updated': item.last_updated, 'type': "action", }
            operation_data['data'].append(new_item)

        transactions = models.Transaction.objects.filter(
            account__in=accounts)

        for item in transactions:
            new_item = {
                'id': item.id,
                'name': self.get_transaction_name(item),
                'balance': item.transaction_amount,
                'last_updated': item.last_updated,
                'type': "transaction",
            }
            operation_data['data'].append(new_item)

        transfers_list = [*models.Transfer.objects.filter(
            from_account__in=accounts
        ), *models.Transfer.objects.filter(
            to_account__in=accounts
        )]

        transfers = [i for n, i in enumerate(
            transfers_list) if i not in transfers_list[n + 1:]]

        for item in transfers:
            new_item = {
                'id': item.id,
                'name': self.get_transfer_name(item),
                'balance': item.transfer_amount,
                'last_updated': item.last_updated,
                'from_account': f"{item.from_account.account_name} (pk={item.from_account.id})",
                'to_account': f"{item.to_account.account_name} (pk={item.to_account.id})",
                'type': "transfer",
            }
            operation_data['data'].append(new_item)

        operation_data['data'].sort(
            key=itemgetter('last_updated'), reverse=True)
        operation_data['data'] = operation_data['data'][:10]

        data.append(operation_data)

        home_data = {
            "balance": accounts.aggregate(balance__sum=Coalesce(Sum('balance'), 0))['balance__sum'],
            "data": data
        }

        return Response(home_data, status=status.HTTP_200_OK)
