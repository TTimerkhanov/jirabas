from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from jirabas.tasks.models import Project, ProjectMembership, Task
from jirabas.users.models import Role, User


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"

    def create(self, validated_data):
        project = super(ProjectSerializer, self).create(validated_data)

        user = self.context["request"].user
        role = Role.get_project_manager()
        ProjectMembership(project=project, member=user, role=role).save()

        return project


class ProjectRoleSerializer(Serializer):
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), required=True
    )
    users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True, many=True
    )


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ("creator",)

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super(TaskSerializer, self).create(validated_data)
