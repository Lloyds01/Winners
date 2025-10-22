from rest_framework import serializers

from account.models import TelcosPhoneNumber, User
from account.validator import validate_password_strength
from pos_app.models import Agent


class TelcosPhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelcosPhoneNumber
        exclude = (
            "created_at",
            "updated_at",
        )

class LoginSerializer(serializers.Serializer):
    """
    Login Serializer
    """

    username = serializers.CharField()
    password = serializers.CharField()


class EmailLoginSerializer(serializers.Serializer):
    """
    Login Serializer
    """

    email = serializers.EmailField()
    password = serializers.CharField()


class PhoneLoginSerializer(serializers.Serializer):
    """
    Login Serializer
    """

    phone = serializers.CharField()
    password = serializers.CharField()


class CreateUserSerializer(serializers.Serializer):
    """
    Create User Serializer

    This serializer field should be user model field
    """

    confirm_password = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    password = serializers.CharField()
    referral_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("password does not match")

        validate_password_strength(data["confirm_password"])

        # check if phone number is valid
        if not Agent.check_if_phone_number_is_valid(data["phone"]):
            raise serializers.ValidationError("Please check the length of the phone number or content of the phone number")

        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ActivateUserSerializer(serializers.Serializer):
    """
    Activate User Serializer
    """

    email = serializers.EmailField()
    code = serializers.CharField()


class ResendActivationCodeSerializer(serializers.Serializer):
    """
    Resend Activation Code Serializer
    """
    email = serializers.EmailField()
