from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from jirabas.tasks.models import Project, ProjectMembership
from jirabas.users.models import Role
from jirabas.users.serializers import (
    RoleSerializer,
    UserProjectInfoSerializer,
    UserSerializer,
    UserShortInfoSerializer,
)

User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(id=self.request.user.id)

    @swagger_auto_schema(responses={status.HTTP_200_OK: UserShortInfoSerializer()})
    @action(detail=False, methods=["GET"])
    def me(self, request):
        serializer = UserShortInfoSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "project",
                openapi.IN_QUERY,
                description="Project ID",
                required=True,
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={status.HTTP_200_OK: UserProjectInfoSerializer()},
    )
    @action(detail=False, methods=["GET"])
    def project_role(self, request):
        if not request.query_params.get("project"):
            return JsonResponse(
                data={"error": "Заполните параметр project"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project = get_object_or_404(Project, pk=request.query_params["project"])
        membership = get_object_or_404(
            ProjectMembership, member=request.user, project=project
        )

        serializer = UserProjectInfoSerializer(
            {
                "username": request.user.username,
                "email": request.user.email,
                "name": request.user.name,
                "role": membership.role.name,
            }
        )
        return JsonResponse(status=status.HTTP_200_OK, data=serializer.data)


class RoleViewSet(ModelViewSet):
    serializer_class = RoleSerializer
    queryset = Role.objects.all()
