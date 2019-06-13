from rest_framework import serializers
from rest_framework.settings import api_settings
from django.contrib.auth.password_validation import validate_password, get_password_validators
from django.core import exceptions as django_exceptions
from djoser.conf import settings
from djoser import serializers as djoser_serialisers
from djoser.compat import get_user_email, get_user_email_field_name
from users.models import User


class PasswordValidatorsMixin:
    @staticmethod
    def password_validators():
        if settings.ALLOW_ANY_PASSWORD:
            return []
        elif settings.PASSWORD_VALIDATORS:
            return get_password_validators(settings.PASSWORD_VALIDATORS)


class UserCreateSerializer(PasswordValidatorsMixin, djoser_serialisers.UserCreateSerializer):
    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')

        try:
            validate_password(password, user, self.password_validators())
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError({
                'password': serializer_error[api_settings.NON_FIELD_ERRORS_KEY]
            })
        return attrs


class PasswordSerializer(PasswordValidatorsMixin, djoser_serialisers.PasswordSerializer):
    def validate(self, attrs):
        user = self.context['request'].user or self.user
        assert user is not None

        try:
            validate_password(attrs['new_password'], user, self.password_validators())
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        return super(djoser_serialisers.PasswordSerializer, self).validate(attrs)


class PasswordRetypeSerializer(PasswordSerializer):
    pass


class SetPasswordSerializer(PasswordSerializer, djoser_serialisers.CurrentPasswordSerializer):
    pass


class SetPasswordRetypeSerializer(PasswordRetypeSerializer, djoser_serialisers.CurrentPasswordSerializer):
    pass


class PasswordResetConfirmSerializer(djoser_serialisers.UidAndTokenSerializer, PasswordSerializer):
    pass


class PasswordResetConfirmRetypeSerializer(djoser_serialisers.UidAndTokenSerializer, PasswordRetypeSerializer):
    pass


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            settings.LOGIN_FIELD,
        )
        read_only_fields = (settings.LOGIN_FIELD, )

    def update(self, instance, validated_data):
        email_field = get_user_email_field_name(User)
        if settings.SEND_ACTIVATION_EMAIL and email_field in validated_data:
            instance_email = get_user_email(instance)
            if instance_email != validated_data[email_field]:
                instance.is_active = False
                instance.save(update_fields=['is_active'])
        return super(UserSerializer, self).update(instance, validated_data)


class CurrentUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            settings.LOGIN_FIELD,
            'battles', 'won', 'rating', 'wallet'
        )
        read_only_fields = (settings.LOGIN_FIELD, )


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'rating')


class UsersListSerializer(serializers.ModelSerializer):
    pos = serializers.CharField()

    class Meta:
        model = User
        fields = ('pos', 'username', 'rating', 'battles', 'won', 'id')
