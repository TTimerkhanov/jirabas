from collections import defaultdict

from django.db import IntegrityError
from django.http import JsonResponse
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from jirabas.tasks.enums import OUTDATED_STATUSES, RelationType, StatusTask
from jirabas.tasks.models import Project, ProjectMembership, Task, TasksRelation
from jirabas.tasks.serializers import (
    ConnectTasksSerializer,
    ProjectRoleSerializer,
    ProjectSerializer,
    ProjectUserSerializer,
    TaskSerializer,
    TasksRelationCategoriesSerializer,
)
from jirabas.users.models import Role, User
from jirabas.users.serializers import UserProjectInfoSerializer, UserSerializer


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    lookup_field = "pk"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Project.objects.filter(members__member=self.request.user)

    @action(detail=True, methods=["post"], serializer_class=ProjectRoleSerializer)
    def add_user(self, request, pk=None):
        serializer = ProjectRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = self.get_object()

        try:
            ProjectMembership.objects.create(
                project=project,
                member_id=serializer.data["user"],
                role_id=serializer.data["role"],
            )
        except IntegrityError:
            return JsonResponse(
                data={"error": "Пользователь уже добавлен к проекту"},
                status=status.HTTP_201_CREATED,
            )

        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], serializer_class=ProjectRoleSerializer)
    def change_role(self, request, pk=None):
        project = self.get_object()
        serializer = ProjectRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ProjectMembership.objects.filter(
            project=project, member_id=serializer.data["user"]
        ).update(role_id=serializer.data["role"])

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], serializer_class=ProjectUserSerializer)
    def remove_user(self, request, pk=None):
        project = self.get_object()
        serializer = ProjectUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ProjectMembership.objects.filter(
            project=project, member_id=serializer.data["user"]
        ).delete()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], serializer_class=UserProjectInfoSerializer)
    def users(self, request, pk=None):
        membership = ProjectMembership.objects.filter(
            project_id=self.kwargs[self.lookup_field]
        ).select_related("member", "role")
        data = [
            {
                "id": entry.member.id,
                "name": entry.member.name,
                "username": entry.member.username,
                "email": entry.member.email,
                "role": entry.role.name,
            }
            for entry in membership
        ]

        return JsonResponse(data=data, safe=False)

    @action(detail=True, methods=["get"])
    def users_to_add(self, request, pk=None):
        users = User.objects.exclude(
            projects__project_id=self.kwargs[self.lookup_field]
        )
        data = UserSerializer(users, many=True).data
        return JsonResponse(data=data, safe=False)

    @action(detail=True, methods=["get"])
    def info(self, request, pk=None):
        project = self.get_object()
        pm = ProjectMembership.objects.filter(
            project=project, role=Role.get_project_manager()
        )[0]
        membership = (
            ProjectMembership.objects.filter(project_id=self.kwargs[self.lookup_field])
            .select_related("member", "role")
            .exclude(member=pm.member)
        )
        data = {
            "project": ProjectSerializer(project).data,
            "pm": {
                "id": pm.member.id,
                "name": pm.member.name,
                "username": pm.member.username,
                "email": pm.member.email,
                "role": pm.role.abbreviation,
            },
            "users": [
                {
                    "id": entry.member.id,
                    "name": entry.member.name,
                    "username": entry.member.username,
                    "email": entry.member.email,
                    "role": entry.role.abbreviation,
                }
                for entry in membership
            ],
        }
        return JsonResponse(data=data)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = (
        "performer",
        "creator",
        "project",
        "type",
        "status",
    )

    def get_queryset(self):
        Task.objects.filter(
            deadline_date__lte=timezone.now(),
            status__in=OUTDATED_STATUSES
        ).update(status=StatusTask.IS_DELAYED)

        return Task.objects.all()

    @action(
        detail=True, methods=["get"], serializer_class=TasksRelationCategoriesSerializer
    )
    def related(self, request, pk=None):
        task = self.get_object()
        data = defaultdict(list)

        from_relations = TasksRelation.objects.filter(from_task=task).select_related(
            "to_task"
        )
        for rel in from_relations:
            data[RelationType(rel.relation_type).value].append(rel.to_task)

        # Нахоодим пару
        to_relations = TasksRelation.objects.filter(to_task=task).select_related(
            "from_task"
        )
        for rel in to_relations:
            for row in TasksRelation.PAIRS:
                if rel.relation_type in row:
                    idx = 0 if row.index(rel.relation_type) == 1 else 1
                    pair = row[idx]
                    data[pair.value].append(rel.from_task)

        transformed_data = [{"relation_type": k, "tasks": v} for k, v in data.items()]

        data = TasksRelationCategoriesSerializer({"relations": transformed_data}).data
        return JsonResponse(data={"results": data})

    @action(detail=True, methods=["post"], serializer_class=ConnectTasksSerializer)
    def connect(self, request, pk=None):
        serializer = ConnectTasksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        TasksRelation.objects.create(
            from_task=self.get_object(),
            to_task=serializer.validated_data["to_task"],
            relation_type=serializer.validated_data["relation_type"],
        )

        return JsonResponse(data=serializer.data)
