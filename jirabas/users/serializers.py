from rest_framework import serializers

from jirabas.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "name", "password"]

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        # TODO: Проверка и корректная обработка кейса с уже существующим юзернеймом

        user = User(**validated_data)
        # Hash the user's password.
        user.set_password(validated_data["password"])
        user.save()
        return user
