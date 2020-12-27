from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from jirabas.tasks.enums import PriorityTask, RelationType, StatusTask, TypeTask
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


class ProjectUserSerializer(Serializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True
    )


class ProjectRoleSerializer(ProjectUserSerializer):
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), required=True
    )


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ("creator", "date_created", "custom_number")

    def create(self, validated_data):
        project = validated_data["project"]
        number = project.tasks.all().count()

        validated_data["creator"] = self.context["request"].user
        validated_data["custom_number"] = f"{project.short_name}-{number}"
        task = super(TaskSerializer, self).create(validated_data)

        return task


class ConnectTasksSerializer(serializers.Serializer):
    to_task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    relation_type = serializers.ChoiceField(choices=RelationType.choices)


class TaskShortSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    type = serializers.ChoiceField(read_only=True, choices=TypeTask.choices)
    priority = serializers.ChoiceField(read_only=True, choices=PriorityTask.choices)
    status = serializers.ChoiceField(read_only=True, choices=StatusTask.choices)


class TasksRelationCategorySerializer(serializers.Serializer):
    relation_type = serializers.IntegerField()
    tasks = serializers.ListField(child=TaskShortSerializer())


class TasksRelationCategoriesSerializer(serializers.Serializer):
    relations = serializers.ListField(child=TasksRelationCategorySerializer())


class LogTimeTaskSerializer(ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True
    )
    task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), required=True
    )
