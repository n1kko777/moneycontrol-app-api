from . import serializers, models
from .services import make_transfer

from rest_framework import viewsets, status, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .mixins import ServiceExceptionHandlerMixin
from rest_framework.generics import get_object_or_404

from django.contrib.auth import get_user_model
from django.core.mail import send_mail


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for the Company class"""

    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not models.Profile.objects.all()\
                .filter(user=self.request.user).exists():
            content = {'error': 'No Profile was found!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if models.Profile.objects.get(
            user=self.request.user
        ).company is not None:
            content = {'error': 'Вы уже состоите в компании!'}
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

        if not models.Profile.objects.all()\
                .filter(user=self.request.user)[0].is_admin:
            content = {'error': 'Only admin can update!'}
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
            content = {'error': 'Only admin can delete!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        instance.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        if models.Profile.objects\
                .all().filter(user=self.request.user).exists():
            profile = models.Profile.objects\
                .all().filter(user=self.request.user)[0]
            return self.queryset\
                .filter(company_id=profile.company_identificator)


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for the Profile class"""

    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def perform_create(self, serializer):
        """Create a new pfofile"""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Return object for current authenticated user only"""
        profiles = self.queryset.filter(user=self.request.user)

        if profiles.exists() and profiles[0].is_admin is True:
            profiles = models.Profile.objects.filter(
                company=profiles[0].company)

        return profiles

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if models.Profile.objects.all()\
                .filter(user=self.request.user).exists():
            content = {'error': 'You can have only one profile!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if 'company_identificator' in self.request.data\
                and self.request.data['company_identificator'] != "":
            identificator = self.request.data['company_identificator']
            try:
                company = models.Company.objects.get(company_id=identificator)
                if not company:
                    raise Exception()

            except Exception as e:
                print(e)
                content = {
                    "error": "Identificator is incorrect. "
                    + "Keep the field empty, if you don't know."}
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

        if 'company_identificator' in self.request.data\
                and self.request.data['company_identificator'] != "":
            identificator = self.request.data['company_identificator']
            try:
                company = models.Company.objects.get(company_id=identificator)
                if not company:
                    raise Exception()

            except Exception as e:
                print(e)
                content = {
                    "error": "Identificator is incorrect. "
                    + "Keep the field empty, if you don't know."}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )

    def partial_update(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if 'company_identificator' in self.request.data\
                and self.request.data['company_identificator'] != "":
            identificator = self.request.data['company_identificator']
            try:
                company = models.Company.objects.get(company_id=identificator)
                if not company:
                    raise Exception()

            except Exception as e:
                print(e)
                content = {
                    "error": "Identificator is incorrect. "
                    + "Keep the field empty, if you don't know."}
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

        if instance.is_admin:
            models.Company.objects\
                .get(company_id=instance.company_identificator)\
                .delete()

        instance.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet for the Account class"""

    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not models.Profile.objects.all()\
                .filter(user=self.request.user).exists():
            content = {'error': 'No Profile was found!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if models.Profile.objects.get(
                user=self.request.user).company is None:
            content = {'error': 'Вы не являетесь сотрудником компании'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(profile=models.Profile.objects.get(
            user=self.request.user), company=models.Profile.objects.get(
            user=self.request.user).company)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def get_queryset(self):
        if models.Profile.objects\
                .all().filter(user=self.request.user).exists():
            profile = models.Profile.objects\
                .all().filter(user=self.request.user)[0]
            profiles = models.Profile.objects\
                .all().filter(company=profile.company)

            if profile.is_admin:
                return models.Account.objects.filter(profile__in=profiles)

            return models.Account.objects.filter(profile=profile)

    def destroy(self, request, pk=None):
        instance = self.get_object()

        if instance.balance > 0:
            content = {'error': 'Баланс должен быть равен 0!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        instance.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # check if requested account belongs to user

        try:
            profile = models.Profile.objects\
                .all().filter(user=self.request.user)[0]
            account = models.Account.objects.filter(profile=profile)\
                .get(pk=self.request.data['account'])
        except Exception as e:
            print(e)
            content = {'error': 'No such account'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if models.Profile.objects.get(
                user=self.request.user).company is None:
            content = {'error': 'Вы не являетесь сотрудником компании'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(account=account,
                        company=models.Profile.objects.get(
                            user=self.request.user).company)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        account = models.Account.objects.get(id=instance.account.id)

        if account.balance < instance.action_amount:
            content = {'error': 'Недостаточно средств'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        account.balance -= instance.action_amount
        account.save()
        return super(ActionViewSet, self)\
            .destroy(request, *args, **kwargs)

    def get_queryset(self):
        if models.Profile.objects\
                .all().filter(user=self.request.user).exists():
            profile = models.Profile.objects\
                .all().filter(user=self.request.user)[0]
            profiles = models.Profile.objects\
                .all().filter(company=profile.company)

            if profile.is_admin:
                accounts = models.Account.objects\
                    .filter(profile__in=profiles)
            else:
                accounts = models.Account.objects\
                    .filter(profile=profile)

            return self.queryset.filter(account__in=accounts)


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if models.Profile.objects.get(
                user=self.request.user).company is None:
            content = {'error': 'Вы не являетесь сотрудником компании'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        transfer_from_account = models.Account.objects.get(
            pk=self.request.data['from_account']
        )

        transfer_to_account = models.Account.objects.get(
            pk=self.request.data['to_account']
        )

        try:
            make_transfer(**serializer.validated_data)
        except Exception as e:
            print(e)
            content = {
                'error': 'Недостаточно средств ' +
                'или неверно указан счет получателя.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            if transfer_from_account.profile != transfer_to_account.profile:
                send_mail(
                    'Подтвердите перевод в ' +
                    transfer_from_account.profile.company.company_name,
                    transfer_from_account.profile.first_name +
                    " " +
                    transfer_from_account.profile.last_name +
                    " перевел Вам " +
                    self.request.data['transfer_amount'] +
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
                    'detail':
                    'Произошла ошибка на сервере. Повторите попытку позже.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        to_account = models.Account.objects.get(id=instance.to_account.id)

        if to_account.balance < instance.transfer_amount:
            content = {'error': 'Недостаточно средств'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        to_account.balance -= instance.transfer_amount
        to_account.save()

        from_account = models.Account.objects.get(id=instance.from_account.id)
        from_account.balance += instance.transfer_amount
        from_account.save()
        return super(TransferViewSet, self)\
            .destroy(request, *args, **kwargs)

    def get_queryset(self):
        if models.Profile.objects.exists():
            profile = models.Profile.objects\
                .all().filter(user=self.request.user)[0]
            profiles = models.Profile.objects\
                .all().filter(company=profile.company)

            if profile.is_admin:
                accounts = models.Account.objects\
                    .filter(profile__in=profiles)
            else:
                accounts = models.Account.objects\
                    .filter(profile=profile)

            return self.queryset.filter(from_account__in=accounts) \
                or self.queryset.filter(to_account__in=accounts)


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        if models.Profile.objects.get(
                user=self.request.user).company is None:
            content = {'error': 'Вы не являетесь сотрудником компании'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            models.Transaction.make_transaction(**serializer.validated_data)
        except ValueError:
            content = {'error': 'Недостаточно средств'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

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

    def get_queryset(self):
        if models.Profile.objects\
                .all().filter(user=self.request.user).exists():
            profile = models.Profile.objects\
                .all().filter(user=self.request.user)[0]
            profiles = models.Profile.objects\
                .all().filter(company=profile.company)

            if profile.is_admin:
                accounts = models.Account.objects\
                    .filter(profile__in=profiles)
            else:
                accounts = models.Account.objects\
                    .filter(profile=profile)

            return self.queryset.filter(account__in=accounts)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for the Category class"""

    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if models.Profile.objects.exists():
            profile = models.Profile.objects.all()\
                .filter(user=self.request.user)[0]

        if not models.Profile.objects.all()\
                .filter(user=self.request.user).exists():
            content = {'error': 'No Profile was found!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if not profile.company:
            content = {'error': 'No Company was found!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        """Create a new category"""
        profile = models.Profile.objects.get(user=self.request.user)
        serializer.save(company=profile.company)

    def get_queryset(self):
        if models.Profile.objects\
                .all().filter(user=self.request.user).exists():
            profiles = models.Profile.objects\
                .all().filter(user=self.request.user)
            profile = profiles[0]
            return models.Category.objects.filter(company=profile.company)


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for the Tag class"""

    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if models.Profile.objects\
                .all().filter(user=self.request.user).exists():
            profile = models.Profile.objects.all()\
                .filter(user=self.request.user)[0]

        if not models.Profile.objects.all()\
                .filter(user=self.request.user).exists():
            content = {'error': 'No Profile was found!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if not profile.company:
            content = {'error': 'No Company was found!'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        """Create a new tag"""
        profile = models.Profile.objects.get(user=self.request.user)
        serializer.save(company=profile.company)

    def get_queryset(self):
        if models.Profile.objects\
                .all().filter(user=self.request.user).exists():
            profiles = models.Profile.objects\
                .all().filter(user=self.request.user)
            profile = profiles[0]
            return models.Tag.objects.filter(company=profile.company)


# Custom View to join profile to Company
# – profile_id
# - profile_phone

User = get_user_model()


class JoinProfileToCompany(
    ServiceExceptionHandlerMixin,
    APIView
):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        profile = get_object_or_404(
            models.Profile.objects.all(), user=self.request.user)

        if not profile:
            return Response(
                {
                    'detail':
                    'У Вас не создан профиль сотрудника'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if profile.is_admin:

            if not models.Profile.objects.filter(
                    pk=request.data['profile_id']).exists():
                return Response(
                    {
                        'detail':
                        'Пользователь с указанным ID не найден'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_team_member = models.Profile.objects.get(
                pk=request.data['profile_id'])

            if new_team_member.company is not None:
                return Response(
                    {
                        'detail':
                        'Пользователь уже состоит в другой или Вашей компании'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if str(new_team_member.phone) != \
                    str(request.data['profile_phone']):
                return Response(
                    {
                        'detail':
                        'Неверно указан номер телефона'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_team_member.company_identificator = \
                profile.company_identificator
            new_team_member.company = \
                profile.company

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
                        'detail':
                        'Произошла ошибка на сервере. Повторите попытку позже.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_team_member.save()

            return Response(
                {
                    'detail':
                    f'{new_team_member.first_name} ' +
                    f'{new_team_member.last_name} ' +
                        'добавлен в Вашу компанию'
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'detail':
                    'Только администратор может добавить сотрудника'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
