from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
from django.core.mail import send_mail
from django.db.models import Sum

from rest_framework import viewsets, status, mixins, schemas
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404

from operator import itemgetter
from collections import defaultdict

from dateutil import parser

import decimal
import coreapi
import coreschema

from .services import make_transfer, is_date
from .mixins import ServiceExceptionHandlerMixin
from . import serializers, models


User = get_user_model()


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for the Company class"""

    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        if models.Profile.objects\
                .filter(user=self.request.user,
                        company__isnull=False).exists():
            profile = models.Profile.objects\
                .filter(user=self.request.user)[0]
            return self.queryset\
                .filter(company_id=profile.company_identificator)\
                .order_by('-last_updated')

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not models.Profile.objects.all()\
                .filter(user=self.request.user,).exists():
            content = {"detail": 'Профиль не найден!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if models.Profile.objects.get(
            user=self.request.user
        ).company is not None:
            content = {"detail": 'Вы уже состоите в компании!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_update(self, serializer):
        serializer.save()

    def update(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if not models.Profile.objects.all()\
                .filter(user=self.request.user)[0].is_admin:
            content = {
                "detail": 'Только администратор может удалить компанию!'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )

    def destroy(self, request, pk=None):
        instance = self.get_object()

        if not models.Profile.objects.all()\
                .filter(user=self.request.user)[0].is_admin:
            content = {
                "detail": 'Только администратор может удалить компанию!'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        instance.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for the Profile class"""

    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """Return object for current authenticated user only"""
        profiles = self.queryset.filter(user=self.request.user)

        if profiles.exists() and profiles[0].is_admin:
            profiles = models.Profile.objects.filter(
                company=profiles[0].company)

        return profiles\
            .order_by('-last_updated')

    def perform_create(self, serializer):
        """Create a new pfofile"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if models.Profile.objects.all()\
                .filter(user=self.request.user,
                        company__isnull=False).exists():
            content = {"detail": 'У вас может быть только один профиль!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )

    def destroy(self, request, pk=None):
        instance = self.get_object()

        if instance.is_admin:
            models.Company.objects\
                .get(company_id=instance.company_identificator)\
                .delete()

        try:
            instance.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "detail":
                    'Невозможно удалить профиль, ' +
                        'который используется в операциях.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet for the Account class"""

    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        if models.Profile.objects\
                .filter(user=self.request.user,
                        company__isnull=False).exists():
            profile = models.Profile.objects\
                .filter(user=self.request.user)[0]

            if profile.is_admin:
                return models.Account.objects.filter(company=profile.company)\
                    .order_by('-last_updated')

            return models.Account.objects\
                .filter(profile=profile, company=profile.company)\
                .order_by('-last_updated')

    def perform_create(self, serializer):
        serializer.save(profile=models.Profile.objects.get(
            user=self.request.user), company=models.Profile.objects.get(
            user=self.request.user).company)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not models.Profile.objects.all()\
                .filter(user=self.request.user,
                        company__isnull=False).exists():
            content = {"detail": 'Профиль не найден!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if models.Profile.objects.get(
                user=self.request.user).company is None:
            content = {"detail": 'Вы не являетесь сотрудником компании'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if models.Account.objects.filter(
            account_name=self.request.data['account_name'],
            profile=models.Profile.objects.get
            (
                user=self.request.user
            )
        ).exists():
            content = {
                "detail": 'Счет с таким названием уже существует!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_update(self, serializer, pk=None):
        serializer.save()

    def update(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if models.Account.objects.filter(
            account_name=self.request.data['account_name'],
            profile=models.Profile.objects.get
            (
                user=self.request.user
            )
        ).exclude(id=pk).exists():
            content = {
                "detail": 'Счет с таким названием уже существует!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )

    def destroy(self, request, pk=None):
        instance = self.get_object()

        if instance.balance != 0:
            content = {"detail": 'Баланс должен быть равен 0!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "detail":
                    'Невозможно удалить счет, ' +
                        'который используется в операциях.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ActionViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """ViewSet for the Action class"""

    queryset = models.Action.objects.all()
    serializer_class = serializers.ActionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        if models.Profile.objects\
                .filter(user=self.request.user,
                        company__isnull=False).exists():
            profile = models.Profile.objects\
                .filter(user=self.request.user)[0]

            if profile.is_admin:
                accounts = models.Account.objects\
                    .filter(company=profile.company)
            else:
                accounts = models.Account.objects\
                    .filter(profile=profile, company=profile.company)

            return self.queryset.filter(account__in=accounts)\
                .order_by('-last_updated')

    def perform_create(self, serializer):
        profile = models.Profile.objects\
            .all().get(user=self.request.user)
        account = models.Account.objects.filter(profile=profile)\
            .get(pk=self.request.data['account'])
        serializer.save(account=account,
                        company=profile.company)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if float(self.request.data['action_amount']) < 0:
            content = {"detail": 'Сумма операции должна быть положительной'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = models.Profile.objects.get(user=self.request.user)
            models.Account.objects.get(
                profile=profile, pk=self.request.data['account'])
        except Exception as e:
            print(e)
            content = {"detail": 'Указанный счет не найден'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if models.Profile.objects.get(
                user=self.request.user).company is None:
            content = {"detail": 'Вы не являетесь сотрудником компании'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        account = models.Account.objects.get(id=instance.account.id)

        account.balance -= instance.action_amount
        account.save()
        return super(ActionViewSet, self)\
            .destroy(request, *args, **kwargs)


class TransferViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """ViewSet for the Transfer class"""

    queryset = models.Transfer.objects.all()
    serializer_class = serializers.TransferSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):

        if models.Profile.objects\
                .filter(user=self.request.user,
                        company__isnull=False).exists():
            profile = models.Profile.objects\
                .all().filter(user=self.request.user)[0]

            if profile.is_admin:
                accounts = models.Account.objects\
                    .filter(company=profile.company)
            else:
                accounts = models.Account.objects\
                    .filter(profile=profile, company=profile.company)

            return self.queryset.filter(from_account__in=accounts)\
                .order_by('-last_updated') \
                or self.queryset.filter(to_account__in=accounts)\
                .order_by('-last_updated')

    def perform_create(self, serializer):
        serializer.save(company=models.Profile.objects.get(
            user=self.request.user).company)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if float(self.request.data['transfer_amount']) < 0:
            content = {"detail": 'Сумма операции должна быть положительной'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = models.Profile.objects\
                .all().filter(user=self.request.user)[0]
            transfer_from_account = models.Account\
                .objects.filter(profile=profile)\
                .get(
                    pk=self.request.data['from_account']
                )
        except Exception as e:
            print(e)
            content = {"detail": 'Указанный счет не найден'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if models.Profile.objects.get(
                user=self.request.user).company is None:
            content = {"detail": 'Вы не являетесь сотрудником компании'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        transfer_to_account = models.Account.objects.get(
            pk=self.request.data['to_account']
        )

        try:
            if transfer_from_account.profile != transfer_to_account.profile:
                send_mail(
                    'Подтвердите перевод в ' +
                    transfer_from_account.profile.company.company_name,
                    transfer_from_account.profile.first_name +
                    " " +
                    transfer_from_account.profile.last_name +
                    " перевел Вам " +
                    str(self.request.data['transfer_amount']) +
                    " ₽. Если Вы не получили данную" +
                    " сумму денежных средств, перейдите в " +
                    "приложение и удалите операцию.",
                    'Команда Mncntrl.ru <service@mncntrl.ru>',
                    [models.Account.objects.get(
                        pk=self.request.data["to_account"]
                    ).profile.user.email, ],
                    fail_silently=False,
                )
        except Exception as e:
            print(e)
            return Response(
                {
                    "detail":
                    'Произошла ошибка на сервере. Повторите попытку позже.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            make_transfer(**serializer.validated_data)
        except ValueError as e:
            content = {
                "detail": str(e)
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        to_account = models.Account.objects.get(id=instance.to_account.id)

        to_account.balance -= instance.transfer_amount
        to_account.save()

        from_account = models.Account.objects.get(id=instance.from_account.id)
        from_account.balance += instance.transfer_amount
        from_account.save()
        return super(TransferViewSet, self)\
            .destroy(request, *args, **kwargs)


class TransactionViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """ViewSet for the Transaction class"""

    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        if models.Profile.objects\
                .filter(user=self.request.user,
                        company__isnull=False).exists():
            profile = models.Profile.objects\
                .filter(user=self.request.user)[0]

            if profile.is_admin:
                accounts = models.Account.objects\
                    .filter(company=profile.company)
            else:
                accounts = models.Account.objects\
                    .filter(profile=profile, company=profile.company)

            return self.queryset.filter(account__in=accounts)\
                .order_by('-last_updated')

    def perform_create(self, serializer):
        serializer.save(company=models.Profile.objects.get(
            user=self.request.user).company)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if float(self.request.data['transaction_amount']) < 0:
            content = {"detail": 'Сумма операции должна быть положительной'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        profile = models.Profile.objects\
            .all().filter(user=self.request.user)[0]

        if not models.Account.objects.filter(profile=profile)\
                .filter(pk=self.request.data['account']).exists():

            content = {"detail": 'Указанный счет не найден'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if models.Profile.objects.get(
                user=self.request.user
        ).company is None:
            content = {"detail": 'Вы не являетесь сотрудником компании'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = models.Account.objects.get(
                id=self.request.data['account']
            )
            account.balance = account.balance - \
                decimal.Decimal(self.request.data['transaction_amount'])
            account.save()

        except ValueError:
            content = {"detail": 'Некорректные данные'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        account = models.Account.objects.get(id=instance.account.id)
        account.balance += instance.transaction_amount
        account.save()
        return super(TransactionViewSet, self)\
            .destroy(request, *args, **kwargs)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for the Category class"""

    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        if models.Profile.objects\
                .filter(user=self.request.user,
                        company__isnull=False).exists():
            profile = models.Profile.objects\
                .filter(user=self.request.user)[0]

            return models.Category.objects.filter(company=profile.company)\
                .order_by('-last_updated')

    def perform_create(self, serializer):
        """Create a new category"""
        profile = models.Profile.objects.get(user=self.request.user)
        serializer.save(company=profile.company)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if models.Profile.objects.exists():
            profile = models.Profile.objects.all()\
                .filter(user=self.request.user)[0]

        if not models.Profile.objects.all()\
                .filter(user=self.request.user,
                        company__isnull=False).exists():
            content = {"detail": 'Профиль не найден!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if not profile.company:
            content = {"detail": 'Компания не найдена!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if models.Category.objects.filter(
            category_name=self.request.data['category_name'],
            company=profile.company
        ).exists():
            content = {"detail": 'Категория с таким названием уже существует!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if models.Category.objects.filter(
            category_name=self.request.data['category_name'],
            company=models.Profile.objects.get
            (
                user=self.request.user
            ).company
        ).exclude(id=pk).exists():
            content = {
                "detail": 'Категория с таким названием уже существует!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            instance.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "detail":
                    'Невозможно удалить категорию, ' +
                        'которая используется в операциях.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for the Tag class"""

    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        if models.Profile.objects\
                .filter(user=self.request.user,
                        company__isnull=False).exists():
            profile = models.Profile.objects\
                .filter(user=self.request.user)[0]

            return models.Tag.objects.filter(company=profile.company)\
                .order_by('-last_updated')

    def perform_create(self, serializer):
        """Create a new tag"""
        profile = models.Profile.objects.get(user=self.request.user)
        serializer.save(company=profile.company)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if models.Profile.objects\
                .all().filter(user=self.request.user,
                              company__isnull=False).exists():
            profile = models.Profile.objects.all()\
                .filter(user=self.request.user)[0]

        if not models.Profile.objects.all()\
                .filter(user=self.request.user,
                        company__isnull=False).exists():
            content = {"detail": 'Профиль не найден!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if not profile.company:
            content = {"detail": 'Компания не найдена!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if models.Tag.objects.filter(
            tag_name=self.request.data['tag_name'],
            company=profile.company
        ).exists():
            content = {"detail": 'Тег с таким названием уже существует!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if models.Tag.objects.filter(
            tag_name=self.request.data['tag_name'],
            company=models.Profile.objects.get
            (
                user=self.request.user
            ).company
        ).exclude(id=pk).exists():
            content = {"detail": 'Тег с таким названием уже существует!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            instance.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "detail":
                    'Невозможно удалить тег, ' +
                    'который используется в операциях.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class JoinProfileToCompany(
    ServiceExceptionHandlerMixin,
    APIView
):
    """ Custom View to join profile to Company """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    schema = schemas.AutoSchema(manual_fields=[
        coreapi.Field(
            "data",
            required=True,
            location="body",
            description='{"profile_phone":"string", "profile_id":"string"}',
            schema=coreschema.Object()
        ),
    ])

    def post(self, request):
        profile = get_object_or_404(
            models.Profile.objects.all(), user=self.request.user)

        if not profile:
            return Response(
                {
                    "detail":
                    'У Вас не создан профиль сотрудника'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if profile.is_admin:

            if not models.Profile.objects.filter(
                    pk=request.data['profile_id']).exists():
                return Response(
                    {
                        "detail":
                        'Пользователь с указанным ID не найден'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_team_member = models.Profile.objects.get(
                pk=request.data['profile_id'])

            if new_team_member.company is not None:
                return Response(
                    {
                        "detail":
                        'Пользователь уже состоит в другой или Вашей компании'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if str(new_team_member.phone) != \
                    str(request.data['profile_phone']):
                return Response(
                    {
                        "detail":
                        'Неверно указан номер телефона'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_team_member\
                .company_identificator = profile.company_identificator
            new_team_member.company = profile.company

            try:
                send_mail(
                    'Приглашение в компанию ' +
                    f'{new_team_member.company.company_name}',
                    'Вы были успешно добавлены в компанию ' +
                    f'{new_team_member.company.company_name}. ' +
                    'Зайдите в приложение!',
                    'Команда Mncntrl.ru <service@mncntrl.ru>',
                    [f'{new_team_member.user.email}'],
                    fail_silently=False,
                )
            except Exception as e:
                print(e)
                return Response(
                    {
                        "detail":
                        'Произошла ошибка на сервере. Повторите попытку позже.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_team_member.save()

            return Response(
                {
                    "detail":
                    f'{new_team_member.first_name} ' +
                    f'{new_team_member.last_name} ' +
                        'добавлен в Вашу компанию'
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "detail":
                    'Только администратор может добавить сотрудника'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class RemoveProfileFromCompany(
    ServiceExceptionHandlerMixin,
    APIView
):
    """ Custom View to remove profile from Company """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    schema = schemas.AutoSchema(manual_fields=[
        coreapi.Field(
            "data",
            required=True,
            location="body",
            description='{"profile_phone":"string", "profile_id":"string"}',
            schema=coreschema.Object()
        ),
    ])

    def post(self, request):
        profile = get_object_or_404(
            models.Profile.objects.all(), user=self.request.user)

        if not profile:
            return Response(
                {
                    "detail":
                    'У Вас не создан профиль сотрудника'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if profile.pk == request.data['profile_id']:
            return Response(
                {
                    "detail":
                    'Вы не можете удалить себя.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if profile.is_admin:

            if not models.Profile.objects.filter(
                    pk=request.data['profile_id']).exists():
                return Response(
                    {
                        "detail":
                        'Пользователь с указанным ID не найден'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            old_team_member = models.Profile.objects.get(
                pk=request.data['profile_id'])

            if old_team_member.company is None:
                return Response(
                    {
                        "detail":
                        'Пользователь не состоит ни в какой из компаний.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if str(old_team_member.phone) != \
                    str(request.data['profile_phone']):
                return Response(
                    {
                        "detail":
                        'Неверно указан номер телефона'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            old_team_member\
                .company_identificator = None
            old_team_member.company = None

            try:
                send_mail(
                    'Удаление из компании ' +
                    f'{profile.company.company_name}',
                    'Вы были успешно удалены из компании ' +
                    f'{profile.company.company_name}. ' +
                    'Зайдите в приложение!',
                    'Команда Mncntrl.ru <service@mncntrl.ru>',
                    [f'{old_team_member.user.email}'],
                    fail_silently=False,
                )
            except Exception as e:
                print(e)
                return Response(
                    {
                        "detail":
                        'Произошла ошибка на сервере. Повторите попытку позже.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            old_team_member.save()

            return Response(
                {
                    "detail":
                    f'{old_team_member.first_name} ' +
                    f'{old_team_member.last_name} ' +
                        'удален из Вашей компании.'
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "detail":
                    'Только администратор может удалить сотрудника'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


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


class HomeListView(
    ServiceExceptionHandlerMixin,
    APIView
):
    """ Custom View to get home list data """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )
    schema = HomeListViewSchema()

    def get(self, request, format=None):
        req_profile = None

        if 'profile_id' in request.query_params:
            if not models.Profile.objects.filter(
                id=self.request.query_params['profile_id']
            ).exists():
                return Response({
                    "detail":
                    "Указанный профиль не содержиться в Вашей компании."
                }, status=status.HTTP_400_BAD_REQUEST)

            req_profile = models.Profile.objects.get(
                id=self.request.query_params['profile_id']
            )

            user_profile = models.Profile.objects.get(
                user=self.request.user
            )

            if req_profile.company != models.Profile.objects.get(
                user=self.request.user
            ).company:
                return Response({
                    "detail":
                    "Указанный профиль не содержиться в Вашей компании."
                }, status=status.HTTP_400_BAD_REQUEST)

            if not user_profile.is_admin:
                return Response({
                    "detail":
                    "Невозможно получить данные пользователя."
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            req_profile = models.Profile.objects.get(
                user=self.request.user
            )

        if req_profile.company is None:
            return Response({
                "detail": "Сначала необходимо создать " +
                "компанию или присоединиться к ней."
            }, status=status.HTTP_400_BAD_REQUEST)

        data = []

        profile = req_profile

        accounts = None

        if profile.is_admin:
            accounts = models.Account.objects\
                .filter(company=profile.company)
        else:
            accounts = models.Account.objects\
                .filter(profile=profile, company=profile.company)

        account_data = {
            'navigate': "Account",
            'title': "Счета",
            'data': [],
        }

        layout_accounts = models.Account.objects.filter(
            profile=profile
        ).order_by('-last_updated')[:5]

        for item in layout_accounts:
            new_item = {}

            new_item['id'] = item.id
            new_item['name'] = item.account_name
            new_item['balance'] = item.balance
            new_item['last_updated'] = item.last_updated
            new_item['type'] = "account"
            account_data['data'].append(new_item)
        data.append(account_data)

        if profile.is_admin and profile.company.profiles.count() > 1:
            profile_data = {
                'navigate': "Team",
                'title': "Команда",
                'data': [],
            }

            profiles = models.Company.objects.get(
                id=profile.company.id
            ).profiles.order_by('id')[:5]

            for item in profiles:
                new_item = {}

                new_item['id'] = item.id
                new_item['name'] = item.first_name + " " + item.last_name
                new_item['balance'] = models.Account.objects.filter(
                    profile=item).aggregate(Sum('balance'))['balance__sum']
                new_item['last_updated'] = item.last_updated
                new_item['type'] = "profile"
                profile_data['data'].append(new_item)
            data.append(profile_data)

        category_data = {
            'navigate': "Category",
            'title': "Категории",
            'data': [],
        }

        categories = models.Category.objects.filter(
            company=profile.company
        ).order_by('-last_updated')[:5]

        for item in categories:
            new_item = {}

            new_item['id'] = item.id
            new_item['name'] = item.category_name
            new_item['balance'] = ""
            new_item['last_updated'] = item.last_updated
            new_item['type'] = "category"
            category_data['data'].append(new_item)
        data.append(category_data)

        tag_data = {
            'navigate': "Tag",
            'title': "Теги",
            'data': [],
        }

        tags = models.Tag.objects.filter(
            company=profile.company
        ).order_by('-last_updated')[:5]

        for item in tags:
            new_item = {}

            new_item['id'] = item.id
            new_item['name'] = item.tag_name
            new_item['balance'] = ""
            new_item['last_updated'] = item.last_updated
            new_item['type'] = "tag"
            tag_data['data'].append(new_item)
        data.append(tag_data)

        operation_data = {
            'navigate': "Operation",
            'title': "Последние операции",
            'data': [],
        }

        actions = models.Action.objects.filter(account__in=accounts)

        for item in actions:
            new_item = {}

            new_item['id'] = item.id
            if req_profile.company.profiles.count() > 1:
                new_item['name'] = item.account.profile.first_name[:1] + \
                    ". " + item.account.profile.last_name + \
                    " (" + item.account.account_name + ")"
            else:
                new_item['name'] = item.account.account_name
            new_item["style"] = "color-success-600"
            new_item['balance'] = item.action_amount
            new_item['last_updated'] = item.last_updated
            new_item['type'] = "action"
            operation_data['data'].append(new_item)

        transactions = models.Transaction.objects.filter(account__in=accounts)
        for item in transactions:
            new_item = {}

            new_item['id'] = item.id
            if req_profile.company.profiles.count() > 1:
                new_item['name'] = item.account.profile.first_name[:1] + \
                    ". " + item.account.profile.last_name + \
                    " (" + item.account.account_name + ")"
            else:
                new_item['name'] = item.account.account_name
            new_item["style"] = "color-danger-600"
            new_item['balance'] = item.transaction_amount
            new_item['last_updated'] = item.last_updated
            new_item['type'] = "transaction"
            operation_data['data'].append(new_item)

        transfers = []

        transfers_list = [*models.Transfer.objects.filter(
            from_account__in=accounts
        ), *models.Transfer.objects.filter(
            to_account__in=accounts
        )]

        transfers = [i for n, i in enumerate(
            transfers_list) if i not in transfers_list[n + 1:]]

        for item in transfers:
            new_item = {}
            new_item['id'] = item.id
            if req_profile.company.profiles.count() > 1:
                new_item['name'] = item.from_account.profile.first_name[:1] + \
                    ". " + item.from_account.profile.last_name + \
                    " (" + item.from_account.account_name + ") " + \
                    "=>" + \
                    item.to_account.profile.first_name[:1] + \
                    ". " + item.to_account.profile.last_name + \
                    " (" + item.to_account.account_name + ") "
            else:
                new_item['name'] = item.from_account.account_name + \
                    " => " + \
                    item.to_account.account_name
            new_item['balance'] = item.transfer_amount
            new_item['last_updated'] = item.last_updated
            new_item["from_account"] = \
                f"{item.from_account.account_name} (pk={item.from_account.id})"
            new_item["to_account"] = \
                f"{item.to_account.account_name} (pk={item.to_account.id})"
            new_item['type'] = "transfer"
            operation_data['data'].append(new_item)

        operation_data['data'].sort(
            key=itemgetter('last_updated'), reverse=True)
        operation_data['data'] = operation_data['data'][:10]

        data.append(operation_data)

        home_data = {
            "balance": accounts.aggregate(Sum('balance'))['balance__sum'],
            "data": data
        }

        return Response(home_data, status=status.HTTP_200_OK)


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
            ]

        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class OperationListView(
    ServiceExceptionHandlerMixin,
    APIView
):
    """ Custom View to get home list data """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    schema = OperationListViewSchema()

    def get(self, request, format=None):
        req_accounts = request.query_params['account'].split(
            ",") if 'account' in request.query_params else []
        req_categories = request.query_params['category'].split(
            ",") if 'category' in request.query_params else []
        req_tags = request.query_params['tag'].split(
            ",") if 'tag' in request.query_params else []

        profile = models.Profile.objects.get(
            user=self.request.user
        )

        data = []
        operation_data = []

        if profile.company is None:
            return Response({
                "detail": "Сначала необходимо создать " +
                "компанию или присоединиться к ней."
            }, status=status.HTTP_400_BAD_REQUEST)

        if (
            'start_date' not in request.query_params or
            'end_date' not in request.query_params
        ):
            return Response({
                "detail": "Неверный диапазон дат"
            }, status=status.HTTP_400_BAD_REQUEST)
        elif (
            not is_date(request.query_params['start_date']) or
            not is_date(request.query_params['end_date'])
        ):
            return Response({
                "detail": "Неверный диапазон дат"
            }, status=status.HTTP_400_BAD_REQUEST)

        start_date = request.query_params['start_date']
        end_date = request.query_params['end_date']

        from_datetime = make_aware(
            parser.parse(start_date).replace(tzinfo=None))
        to_datetime = make_aware(parser.parse(end_date).replace(tzinfo=None))

        try:
            if profile.is_admin:
                accounts = models.Account.objects.filter(
                    company=profile.company
                )
                accounts = accounts.filter(
                    id__in=req_accounts
                ) if bool(req_accounts) else accounts
            else:
                accounts = models.Account.objects.filter(
                    profile=profile
                )
                accounts = accounts.filter(
                    id__in=req_accounts
                ) if bool(req_accounts) else accounts

        except Exception as e:
            print(f"action: {e}")

        try:
            actions = models.Action.objects.filter(
                account__in=accounts,
                last_updated__range=[
                    from_datetime,
                    to_datetime
                ]
            )

            actions = actions.filter(
                category__in=req_categories,
            ) if bool(req_categories) else actions
            actions = actions.filter(
                tags__in=req_tags,
            ) if bool(req_tags) else actions

        except Exception as e:
            print(f"action: {e}")

        for item in actions:
            new_item = {}

            new_item['id'] = item.id
            if profile.company.profiles.count() > 1:
                new_item['name'] = item.account.profile.first_name[:1] + \
                    ". " + item.account.profile.last_name + \
                    " (" + item.account.account_name + ")"
            else:
                new_item['name'] = item.account.account_name
            new_item['account'] = item.account.id
            new_item["style"] = "color-success-600"
            new_item['balance'] = item.action_amount
            new_item['last_updated'] = item.last_updated
            new_item['category'] = item.category.id
            new_item['tags'] = [int(var.id) for var in item.tags.all()]
            new_item['type'] = "action"
            operation_data.append(new_item)

        try:
            transactions = models.Transaction.objects.filter(
                account__in=accounts,
                last_updated__range=[
                    from_datetime,
                    to_datetime
                ]
            )

            transactions = transactions.filter(
                category__in=req_categories,
            ) if bool(req_categories) else transactions
            transactions = transactions.filter(
                tags__in=req_tags,
            ) if bool(req_tags) else transactions

        except Exception as e:
            print(f"transactions: {e}")

        for item in transactions:
            new_item = {}

            new_item['id'] = item.id
            if profile.company.profiles.count() > 1:
                new_item['name'] = item.account.profile.first_name[:1] + \
                    ". " + item.account.profile.last_name + \
                    " (" + item.account.account_name + ")"
            else:
                new_item['name'] = item.account.account_name
            new_item['account'] = item.account.id
            new_item["style"] = "color-danger-600"
            new_item['balance'] = item.transaction_amount
            new_item['last_updated'] = item.last_updated
            new_item['category'] = item.category.id
            new_item['tags'] = [int(var.id) for var in item.tags.all()]
            new_item['type'] = "transaction"
            operation_data.append(new_item)

        transfers = []

        try:
            transfers_list = [
                *models.Transfer.objects.filter(
                    from_account__in=accounts,
                    last_updated__range=[
                        from_datetime,
                        to_datetime
                    ]
                ),
                *models.Transfer.objects.filter(
                    to_account__in=accounts,
                    last_updated__range=[
                        from_datetime,
                        to_datetime
                    ]
                )
            ]

            transfers_list = [] if bool(req_categories) else transfers_list
            transfers_list = [] if bool(req_tags) else transfers_list

        except Exception as e:
            print(f"transfers: {e}")

        transfers = [i for n, i in enumerate(
            transfers_list) if i not in transfers_list[n + 1:]]

        for item in transfers:
            new_item = {}
            new_item['id'] = item.id
            if profile.company.profiles.count() > 1:
                new_item['name'] = item.from_account.profile.first_name[:1] + \
                    ". " + item.from_account.profile.last_name + \
                    " (" + item.from_account.account_name + ") " + \
                    "=>" + \
                    item.to_account.profile.first_name[:1] + \
                    ". " + item.to_account.profile.last_name + \
                    " (" + item.to_account.account_name + ") "
            else:
                new_item['name'] = item.from_account.account_name + \
                    " => " + \
                    item.to_account.account_name
            new_item['balance'] = item.transfer_amount
            new_item['last_updated'] = item.last_updated
            new_item["from_account"] = \
                f"{item.from_account.account_name} (pk={item.from_account.id})"
            new_item["from_account_id"] = item.from_account.id
            new_item["to_account"] = \
                f"{item.to_account.account_name} (pk={item.to_account.id})"
            new_item["to_account_id"] = item.to_account.id
            new_item['type'] = "transfer"
            operation_data.append(new_item)

        operation_data.sort(
            key=itemgetter('last_updated'),
            reverse=True
        )

        groups = defaultdict(list)

        for obj in operation_data:
            groups[obj['last_updated'].strftime('%d.%m.%Y')].append(obj)

        new_list = groups.values()

        data = [{
            "title": var[0]['last_updated'].strftime('%d.%m.%Y'),
            "total_day_action": actions
                .filter(
                    last_updated__day=var[0]['last_updated'].day,
                    last_updated__month=var[0]['last_updated'].month,
                    last_updated__year=var[0]['last_updated'].year
            )
            .aggregate(
                Sum('action_amount')
            )['action_amount__sum'],
            "total_day_transaction": transactions
            .filter(
                last_updated__day=var[0]['last_updated'].day,
                last_updated__month=var[0]['last_updated'].month,
                last_updated__year=var[0]['last_updated'].year
            )
            .aggregate(
                Sum('transaction_amount')
            )['transaction_amount__sum'],
            "data": var
        } for var in new_list]

        return Response({
            "total_action": actions.
            aggregate(
                Sum('action_amount')
            )['action_amount__sum'],
            "total_transaction": transactions.
            aggregate(
                Sum('transaction_amount')
            )['transaction_amount__sum'],
            "data": data
        }, status=status.HTTP_200_OK)
