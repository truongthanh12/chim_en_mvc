from ..models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.response import Response
from django.contrib.auth.models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    user_permissions = PermissionSerializer(many=True, read_only=True)
    # favorites = serializers.StringRelatedField(many=True)
    # orders = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'gender', 'date_of_birth', 'is_superuser', 'is_staff', 'user_permissions', 'created_at']

    # def update(self, instance, validated_data):
    #     print("cc")
    #     print(validated_data)
    #     instance.username = validated_data.get('username')
    #     instance.email = validated_data.get('email')
    #     instance.first_name = validated_data.get('first_name')
    #     instance.last_name = validated_data.get('last_name')
    #     instance.gender = validated_data.get('gender')
    #     if validated_data.get('date_of_birth') is not None:
    #         instance.date_of_birth = validated_data.get('date_of_birth')
    #     instance.is_staff = validated_data.get('is_staff')

    #     if (validated_data.get('user_permissions')):
    #         permissions = Permission.objects.filter(
    #             id__in=validated_data.get('user_permissions').id)
    #         print("ahihi")
    #         print(permissions)
    #         instance.user_permissions.set(permissions)
    #     instance.save()
    #     return instance

# Register Serializer


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_staff')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):

        user = User.objects.create_user(
            validated_data['username'], validated_data['email'], validated_data['password'])
        print(validated_data)
        if 'is_staff' in validated_data:
            print("DIT ME MAY")
            user.is_staff = validated_data['is_staff']
            print(user.is_staff)

        return user

# Login Serializer


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):

        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")
