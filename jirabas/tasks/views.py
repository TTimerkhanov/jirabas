from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from jirabas.tasks.models import Project, ProjectMembership, Task
from jirabas.tasks.serializers import (
    ProjectRoleSerializer,
    ProjectSerializer,
    TaskSerializer,
)
from jirabas.users.models import Role, User


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return Project.objects.filter(members__member=self.request.user)

    @action(detail=True, methods=["post"], serializer_class=ProjectRoleSerializer)
    def add_users(self, request, pk=None):
        project = self.get_object()
        serializer = ProjectRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = Role.objects.get(pk=serializer.data["role"])
        users = User.objects.filter(pk__in=serializer.data["users"])
        objects = [
            ProjectMembership(project=project, member=user, role=role) for user in users
        ]
        ProjectMembership.objects.bulk_create(objects)

        return Response(status=status.HTTP_201_CREATED)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
