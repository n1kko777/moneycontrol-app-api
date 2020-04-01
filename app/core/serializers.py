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
            'company',
            'company_identificator',
            'created',
            'last_updated',
        ]

        read_only_fields = [
            'is_admin',
            'accounts',
            'company',
        ]

    def create(self, validated_data):
        instance = models.Profile.objects.create(**validated_data)
        if instance.company_identificator is not None and\
                instance.company_identificator is not "":
            company = models.Company.objects.get(
                company_id=instance.company_identificator)
            instance.company = company
        else:
            instance.company_identificator = None

        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.company_identificator = validated_data.get(
            'company_identificator', instance.company_identificator)
        instance.company = validated_data.get('company', instance.company)
        instance.is_admin = validated_data.get('is_admin', instance.is_admin)

        if instance.company_identificator is None or\
                instance.company_identificator is "":
            instance.company_identificator = None

            company = instance.company

            instance.company = None
            if instance.is_admin:
                instance.is_admin = False
                company.delete()
        else:
            company = models.Company.objects.get(
                company_id=instance.company_identificator)
            instance.company = company

        instance.id = validated_data.get('id', instance.id)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.phone_confirmed = validated_data.get(
            'phone_confirmed', instance.phone_confirmed)
        instance.image = validated_data.get('image', instance.image)
        instance.created = validated_data.get('created', instance.created)
        instance.last_updated = validated_data.get(
            'last_updated', instance.last_updated)

        instance.save()

        return instance


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Account
        fields = [
            'profile',
            'id',
            'balance',
            'account_name',
            'account_color',
            'last_updated',
            'created',
        ]

        read_only_fields = ('id', 'profile')


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

    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = models.Action
        fields = (
            'id',
            'account',
            'action_amount',
            'tags',
            'created',
            'last_updated',
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

    from_profile = serializers.CharField(source="from_account.profile")
    from_account = serializers.CharField()
    to_profile = serializers.CharField(source="to_account.profile")
    to_account = serializers.CharField()

    def validate(self, data):
        try:
            data['to_account'] = models.Account.objects.get(
                pk=data['to_account'])
        except Exception as e:
            print(e)
            raise serializers.ValidationError(
                'No such account from serializer')
        return data

    class Meta:
        model = models.Transfer
        fields = [
            'id',
            'from_account',
            'from_profile',
            'to_account',
            'to_profile',
            'transfer_amount',
            'last_updated',
            'created',
        ]
        read_only_fields = ('id', 'from_profile', 'to_profile', )


class TransactionSerializer(serializers.ModelSerializer):

    category = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = models.Transaction
        fields = (
            'id',
            'account',
            'category',
            'tags',
            'transaction_amount',
            'last_updated',
            'created',
        )
        read_only_fields = ('id', )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = [
            'id',
            'category_name',
            'category_color',
            'created',
            'last_updated',
        ]

        read_only_fields = ['id', 'company']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = [
            'tag_name',
            'tag_color',
            'created',
            'last_updated',
        ]

        read_only_fields = ['id', 'company']
