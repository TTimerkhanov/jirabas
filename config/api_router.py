from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from jirabas.tasks.views import ProjectViewSet, TaskViewSet
from jirabas.users.views import RoleViewSet, UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("projects", ProjectViewSet, basename="project")
router.register("tasks", TaskViewSet, basename="task")
router.register("roles", RoleViewSet, basename="role")

app_name = "api"
urlpatterns = router.urls
