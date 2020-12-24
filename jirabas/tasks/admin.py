from django.contrib import admin

# Register your models here.
from jirabas.tasks.models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
