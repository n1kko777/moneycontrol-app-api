from rest_framework import serializers

from . import models


class CompanySerializer(serializers.ModelSerializer):
    profiles = serializers.StringRelatedField(
        many=True,
        read_only=True)

    class Meta:
        model = models.Company
        fields = [
            "id",
            "company_id",
            "company_name",
            "profiles",
            "created",
            "last_updated",
        ]

        read_only_fields = [
            "id",
            "company_id",
        ]

    def create(self, validated_data):
        instance = models.Company.objects.create(**validated_data)

        profiles = models.Profile.objects.all().filter(
            user=self.context['request'].user)

        for profile in profiles:
            profile.is_admin = True

            profile.company = instance
            profile.company_identificator = instance.company_id
            profile.save()

        return instance


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Profile
        fields = [
            'id',
            "first_name",
            "last_name",
            "phone",
            "phone_confirmed",
            "image",
            'is_admin',
            'company',
            'company_identificator',
            "created",
            "last_updated",
        ]

        read_only_fields = [
            'is_admin',
            'company',
        ]

    def create(self, validated_data):
        instance = models.Profile.objects.create(**validated_data)
        return instance


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Account
        fields = [
            'id',
            'balance',
            "account_name",
            "account_color",
            "last_updated",
            "created",
        ]

        read_only_fields = ('id',)


class ActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Action
        fields = (
            'id',
            'account',
            'action_amount',
            'tags',
            "created",
            "last_updated",
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        if validated_data['account'].balance\
                + validated_data['action_amount'] > 0:
            validated_data['account'].balance\
                += validated_data['action_amount']
            validated_data['account'].save()
        else:
            raise serializers.ValidationError(
                ('Not enough money')
            )

        return super(ActionSerializer, self).create(validated_data)


class TransferSerializer(serializers.ModelSerializer):

    to_account = serializers.CharField()

    def validate(self, data):
        try:
            data['to_account'] = models.Account.objects.get(
                pk=data['to_account'])
        except Exception as e:
            print(e)
            raise serializers.ValidationError(
                "No such account from serializer")
        return data

    class Meta:
        model = models.Transfer
        fields = [
            'id',
            'from_account',
            'to_account',
            "transfer_amount",
            "last_updated",
            "created",
        ]
        read_only_fields = ('id', )


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Transaction
        fields = (
            'id',
            'account',
            'category',
            'tags',
            'transaction_amount',
            "last_updated",
            "created",
        )
        read_only_fields = ('id', )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = [
            "caterory_name",
            "category_color",
            "created",
            "last_updated",
        ]

        read_only_fields = ['id', 'company']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = [
            "tag_name",
            "tag_color",
            "created",
            "last_updated",
        ]

        read_only_fields = ['id', 'company']
