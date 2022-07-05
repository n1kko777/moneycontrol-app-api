from rest_framework import serializers

from . import models


class ProfileSerializer(serializers.ModelSerializer):

    accounts = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Profile
        fields = [
            'id',
            'first_name',
            'last_name',
            'accounts',
            'phone',
            'phone_confirmed',
            'image',
            'is_admin',
            'is_active',
            'company',
            'company_identificator',
            'created',
            'last_updated',
        ]

        read_only_fields = [
            'id',
            'is_admin',
            'accounts',
            'company',
            'company_identificator',
            'phone_confirmed',
            'is_active',
        ]


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Account
        fields = [
            'id',
            'profile',
            'balance',
            'is_active',
            'is_visible',
            'account_name',
            'account_color',
            'last_updated',
            'created',
        ]

        read_only_fields = [
            'id', 'profile', 'is_active',
        ]


class CompanySerializer(serializers.ModelSerializer):
    profiles = ProfileSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = models.Company
        fields = [
            'id',
            'company_id',
            'company_name',
            'profiles',
            'created',
            'last_updated',
        ]

        read_only_fields = [
            'id',
            'company_id',
        ]

    def create(self, validated_data):
        instance = models.Company.objects.create(**validated_data)

        profiles = models.Profile.objects.all().filter(
            user=self.context['request'].user)

        profile = profiles[0]
        profile.is_admin = True

        profile.company = instance
        profile.company_identificator = instance.company_id
        profile.save()

        return instance


class ActionSerializer(serializers.ModelSerializer):

    profile_name = serializers.CharField(
        source="account.profile", read_only=True)

    class Meta:
        model = models.Action
        fields = (
            'id',
            'account',
            'profile_name',
            'action_amount',
            'is_active',
            'category',
            'tags',
            'created',
            'last_updated',
        )
        read_only_fields = [
            'id', 'is_active',
        ]

    def create(self, validated_data):

        validated_data['account'].balance\
            += validated_data['action_amount']
        validated_data['account'].save()

        return super(ActionSerializer, self).create(validated_data)


class TransferSerializer(serializers.ModelSerializer):

    from_profile = serializers.CharField(
        source="from_account.profile", read_only=True)
    from_account = serializers.CharField()

    to_profile = serializers.CharField(
        source="to_account.profile", read_only=True)
    to_account = serializers.CharField()

    def validate(self, data):
        try:
            data['from_account'] = models.Account.objects.get(
                pk=data['from_account'])
        except Exception as e:
            print(e)
            raise serializers.ValidationError(
                'Счет отправителя не найден')
        try:
            data['to_account'] = models.Account.objects.get(
                pk=data['to_account'])
        except Exception as e:
            print(e)
            raise serializers.ValidationError(
                'Счет получателя не найден')
        return data

    class Meta:
        model = models.Transfer
        fields = [
            'id',
            'from_account',
            'from_profile',
            'to_account',
            'to_profile',
            'is_active',
            'transfer_amount',
            'last_updated',
            'created',
        ]
        read_only_fields = [
            'id', 'from_profile',
            'to_profile', 'is_active',
        ]


class TransactionSerializer(serializers.ModelSerializer):

    profile_name = serializers.CharField(
        source="account.profile", read_only=True)

    class Meta:
        model = models.Transaction
        fields = (
            'id',
            'account',
            'profile_name',
            'category',
            'is_active',
            'tags',
            'transaction_amount',
            'last_updated',
            'created',
        )
        read_only_fields = [
            'id', 'is_active',
        ]


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = [
            'id',
            'category_name',
            'category_color',
            'is_active',
            'created',
            'last_updated',
        ]

        read_only_fields = ['id', 'company', 'is_active']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = [
            'id',
            'tag_name',
            'tag_color',
            'is_active',
            'created',
            'last_updated',
        ]

        read_only_fields = ['id', 'company', 'is_active', ]
