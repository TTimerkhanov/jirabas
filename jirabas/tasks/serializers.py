from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from jirabas.tasks.enums import PriorityTask, RelationType, StatusTask, TypeTask
from jirabas.tasks.models import Project, ProjectMembership, Task, TasksRelation
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
        read_only_fields = ("creator",)

    relation_type = serializers.ChoiceField(
        choices=RelationType.choices, required=False
    )
    relative_task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), required=False
    )

    def create(self, validated_data):
        relation_type, relative_task = None, None

        if "relation_type" in validated_data:
            relation_type = validated_data.pop("relation_type")
        if "relative_task" in validated_data:
            relative_task = validated_data.pop("relative_task")

        validated_data["creator"] = self.context["request"].user
        task = super(TaskSerializer, self).create(validated_data)

        if relation_type and relative_task:
            TasksRelation.objects.create(
                from_task=task, to_task=relative_task, relation_type=relation_type
            )

        return task


class TaskShortSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    priority = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    def get_type(self, value):
        return TypeTask(value.type).label

    def get_priority(self, value):
        return PriorityTask(value.priority).label

    def get_status(self, value):
        return StatusTask(value.status).label


class TasksRelationCategorySerializer(serializers.Serializer):
    relation_type = serializers.CharField()
    tasks = serializers.ListField(child=TaskShortSerializer())


class TasksRelationCategoriesSerializer(serializers.Serializer):
    relations = serializers.ListField(child=TasksRelationCategorySerializer())
