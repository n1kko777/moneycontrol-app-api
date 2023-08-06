from django.db.models import Sum, Q
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.functions import Coalesce
from django.utils.timezone import make_aware

from rest_framework import status, schemas
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from operator import itemgetter
from collections import defaultdict

from dateutil import parser

import coreapi
import coreschema

from core.services import is_date
from core.mixins import ServiceExceptionHandlerMixin
from core import models


def is_date(date_str):
    try:
        parser.parse(date_str)
        return True
    except ValueError:
        return False


class OperationListViewSchema(schemas.AutoSchema):

    def get_manual_fields(self, path, method):
        extra_fields = []

        if method.lower() in ['get', ]:
            extra_fields = [
                coreapi.Field(
                    'start_date',
                    required=True,
                    location='query',
                    schema=coreschema.String()
                ),
                coreapi.Field(
                    'end_date',
                    required=True,
                    location='query',
                    schema=coreschema.String()
                ),
                coreapi.Field(
                    'account',
                    location='query',
                    schema=coreschema.Array()
                ),
                coreapi.Field(
                    'category',
                    location='query',
                    schema=coreschema.Array()
                ),
                coreapi.Field(
                    'tag',
                    location='query',
                    schema=coreschema.Array()
                ),
                coreapi.Field(
                    'type',
                    location='query',
                    schema=coreschema.Array()
                ),
            ]

        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class OperationListView(ServiceExceptionHandlerMixin, APIView):
    """Custom View to get operation list data"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    schema = OperationListViewSchema()

    def get(self, request):
        req_accounts = [account_id for account_id in request.query_params.get(
            'account', '').split(",") if account_id]
        req_categories = [category_id for category_id in request.query_params.get(
            'category', '').split(",") if category_id]
        req_tags = [tag_id for tag_id in request.query_params.get(
            'tag', '').split(",") if tag_id]
        req_types = [type_id for type_id in request.query_params.get(
            'type', '').split(",") if type_id]

        profile = models.Profile.objects.get(user=self.request.user)

        if profile.company is None:
            return Response(
                {"detail": "Сначала необходимо создать компанию или присоединиться к ней."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'start_date' not in request.query_params or 'end_date' not in request.query_params:
            return Response(
                {"detail": "Неверный диапазон дат"},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif not is_date(request.query_params['start_date']) or not is_date(request.query_params['end_date']):
            return Response(
                {"detail": "Неверный диапазон дат"},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_date = request.query_params['start_date']
        end_date = request.query_params['end_date']

        from_datetime = make_aware(
            parser.parse(start_date).replace(tzinfo=None))
        to_date = make_aware(parser.parse(end_date).replace(tzinfo=None))
        to_datetime = to_date.replace(minute=59, hour=23, second=59)

        actions = models.Action.objects.none()
        transactions = models.Transaction.objects.none()
        transfers = []

        try:
            accounts = models.Account.objects.filter(company=profile.company) if profile.is_admin \
                else models.Account.objects.filter(profile=profile)

            accounts = accounts.filter(id__in=req_accounts) if bool(
                req_accounts) else accounts

            if ('action' in req_types) or not bool(req_types):
                actions = models.Action.objects.filter(
                    account__in=accounts,
                    last_updated__range=[from_datetime, to_datetime]
                ).select_related('account', 'category').prefetch_related('tags')

                actions = actions.filter(category__in=req_categories) if bool(
                    req_categories) else actions
                actions = actions.filter(tags__in=req_tags) if bool(
                    req_tags) else actions

            if ('transaction' in req_types) or not bool(req_types):
                transactions = models.Transaction.objects.filter(
                    account__in=accounts,
                    last_updated__range=[from_datetime, to_datetime]
                ).select_related('account', 'category').prefetch_related('tags')

                transactions = transactions.filter(category__in=req_categories) if bool(
                    req_categories) else transactions
                transactions = transactions.filter(
                    tags__in=req_tags) if bool(req_tags) else transactions

            transfers_list = list(models.Transfer.objects.filter(
                Q(from_account__in=accounts) | Q(to_account__in=accounts),
                last_updated__range=[from_datetime, to_datetime]
            ).select_related('from_account', 'to_account'))

            transfers_list = [] if bool(req_categories) else transfers_list
            transfers_list = [] if bool(req_tags) else transfers_list

            transfers = [i for n, i in enumerate(
                transfers_list) if i not in transfers_list[n + 1:]]

        except Exception as e:
            print(f"transfers: {e}")

        operation_data = []

        for item in actions.values('id', 'account', 'action_amount', 'last_updated', 'category__id').annotate(
            tags=ArrayAgg('tags__id', distinct=True)
        ):
            new_item = {}
            new_item['id'] = item['id']
            account = models.Account.objects.get(
                id=item['account'])
            profile_obj = account.profile
            account_name = account.account_name
            profile_count = profile.company.profiles.count()
            if profile_count > 1:
                new_item[
                    'name'] = f"{profile_obj.first_name[:1]}. {profile_obj.last_name} ({account_name})"
            else:
                new_item['name'] = account_name
            new_item['account'] = account.id
            new_item["style"] = "color-success-600"
            new_item['balance'] = item['action_amount']
            new_item['last_updated'] = item['last_updated']
            new_item['category'] = item['category__id']
            new_item['tags'] = [int(var)
                                for var in item['tags'] if var is not None]
            new_item['type'] = "action"
            operation_data.append(new_item)

        for item in transactions.values('id', 'account', 'transaction_amount', 'last_updated', 'category__id').annotate(
            tags=ArrayAgg('tags__id', distinct=True)
        ):
            new_item = {}
            new_item['id'] = item['id']
            account = models.Account.objects.get(
                id=item['account'])
            profile_obj = account.profile
            account_name = account.account_name
            profile_count = profile.company.profiles.count()
            if profile_count > 1:
                new_item[
                    'name'] = f"{profile_obj.first_name[:1]}. {profile_obj.last_name} ({account_name})"
            else:
                new_item['name'] = account_name
            new_item['account'] = account.id
            new_item["style"] = "color-danger-600"
            new_item['balance'] = item['transaction_amount']
            new_item['last_updated'] = item['last_updated']
            new_item['category'] = item['category__id']
            new_item['tags'] = [int(var)
                                for var in item['tags'] if var is not None]
            new_item['type'] = "transaction"
            operation_data.append(new_item)

        for item in transfers:
            new_item = {}
            new_item['id'] = item.id
            from_account = item.from_account
            to_account = item.to_account
            profile_from = from_account.profile
            profile_to = to_account.profile
            from_account_name = from_account.account_name
            to_account_name = to_account.account_name
            profile_count = profile.company.profiles.count()
            if profile_count > 1:
                new_item['name'] = (
                    f"{profile_from.first_name[:1]}. {profile_from.last_name}"
                    f" ({from_account_name}) => {profile_to.first_name[:1]}. "
                    f"{profile_to.last_name} ({to_account_name})"
                )
            else:
                new_item['name'] = f"{from_account_name} => {to_account_name}"
            new_item['balance'] = item.transfer_amount
            new_item['last_updated'] = item.last_updated
            new_item["from_account"] = f"{from_account.account_name} (pk={from_account.id})"
            new_item["from_account_id"] = from_account.id
            new_item["to_account"] = f"{to_account.account_name} (pk={to_account.id})"
            new_item["to_account_id"] = to_account.id
            new_item['type'] = "transfer"
            operation_data.append(new_item)

        operation_data.sort(key=itemgetter('last_updated'), reverse=True)

        groups = defaultdict(list)

        for obj in operation_data:
            groups[obj['last_updated'].strftime('%d.%m.%Y')].append(obj)

        new_list = groups.values()

        data = [
            {"title": var[0]['last_updated'].strftime('%d.%m.%Y'), "data": var}
            for var in new_list
        ]

        total_action = actions.aggregate(action_amount__sum=Coalesce(
            Sum('action_amount'), 0))['action_amount__sum']
        total_transaction = transactions.aggregate(transaction_amount__sum=Coalesce(
            Sum('transaction_amount'), 0))['transaction_amount__sum']

        if total_action is None:
            total_action = 0

        if total_transaction is None:
            total_transaction = 0

        return Response({
            'data': data,
            "total_action": total_action,
            "total_transaction": total_transaction
        }, status=status.HTTP_200_OK)
