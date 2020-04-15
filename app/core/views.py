from . import serializers
from . import models

from .services import make_transfer

from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


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

        self.perform_create(serializer)
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

        self.perform_create(serializer)
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

        self.perform_create(serializer)
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

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        """Create a new account"""
        profile = models.Profile.objects.get(user=self.request.user)
        serializer.save(profile=profile)

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


class ActionViewSet(viewsets.ModelViewSet):
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

        serializer.save(account=account)

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


class TransferViewSet(viewsets.ModelViewSet):
    """ViewSet for the Transfer class"""

    queryset = models.Transfer.objects.all()
    serializer_class = serializers.TransferSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            make_transfer(**serializer.validated_data)
        except Exception as e:
            print(e)
            content = {
                'error': 'Недостаточно средств ' +
                'или неверно указан счет получателя.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

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


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for the Transaction class"""

    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

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
