from rest_framework import serializers

from jirabas.users.models import Role, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "name", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        # TODO: Проверка и корректная обработка кейса с уже существующим юзернеймом

        user = User(**validated_data)
        # Hash the user's password.
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserShortInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "name"]
        read_only_fields = ["id", "username", "email", "name"]


class UserProjectInfoSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"
