

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, Model, TextField, ForeignKey, DateTimeField, CASCADE, IntegerField, SET_NULL
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from jirabas.users.enums import TypeTask, StatusTask, PriorityTask


class User(AbstractUser):
    """Default user for jirabas."""

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)

    def __str__(self):
        return self.name


class Role(Model):
    name = CharField("Name", blank=False, max_length=255)
    description = TextField("Description", blank=True, max_length=700)

    def __str__(self):
        return "Role %s" % self.name


class Project(Model):
    name = CharField("Name", blank=False, max_length=255)
    short_name = CharField("Short name", blank=False, max_length=4)
    description = TextField("Description", blank=True, max_length=2000)
    date_start = DateTimeField("Date start", blank=False, null=False, default=timezone.now)
    date_finish = DateTimeField("Date finish", blank=True, null=True)

    def __str__(self):
        return "Project %s " % self.name


class ProjectMembership(Model):
    project = ForeignKey(Project, related_name='members', on_delete=CASCADE,
                         blank=False, null=False, verbose_name='Project')
    member = ForeignKey(User, related_name='projects', on_delete=CASCADE,
                        blank=False, null=False, verbose_name='Members of project')
    role = ForeignKey(Role, related_name='roles', on_delete=CASCADE,
                      blank=False, null=False, verbose_name='Role of member')

    def __str__(self):
        return "Project %s member %s role %s" % (self.project, self.member, self.role)


class TypeRelationTask(Model):
    type = CharField("Name of type", blank=False, max_length=255)
    description = TextField("Description", blank=True, max_length=500)

    def __str__(self):
        return "Type relation tasks %s" % self.type


class Task(Model):
    custom_number = CharField("Number of task", blank=False, max_length=20)
    name = CharField("Name of task", blank=False, max_length=255)
    description = TextField("Description", blank=True, max_length=5000)
    status = CharField(max_length=2, choices=StatusTask.choices, default=StatusTask.BACKLOG)
    type = CharField(max_length=3, choices=TypeTask.choices, default=TypeTask.WORK_ITEM)
    project = ForeignKey(Project, related_name='tasks', on_delete=CASCADE,
                         blank=False, null=False, verbose_name='Project')
    acceptance_criteria = TextField("Acceptance criteria", blank=True, max_length=2000)
    creator = ForeignKey(User, related_name='creator_tasks', on_delete=CASCADE,
                         blank=False, null=False, verbose_name='Creator of task')

    performer = ForeignKey(User, related_name='performer_tasks', on_delete=CASCADE,
                           blank=True, null=True, verbose_name='Performer of task')
    date_create = DateTimeField("Creation date", blank=False, null=False, default=timezone.now)
    date_modified = DateTimeField("Modification date", blank=True, null=True)
    deadline_date = DateTimeField("Deadline date", blank=True, null=True)
    priority = CharField(max_length=3, choices=PriorityTask.choices, default=PriorityTask.MEDIUM)
    estimate_hours = IntegerField("Estimate task in hours", blank=True, null=True)
    parent_task = ForeignKey("Task", related_name='child_tasks', on_delete=SET_NULL,
                             blank=True, null=True, verbose_name='Parent task')

    def __str__(self):
        return "Task %s %s, creator %s" \
               % (self.custom_number, self.name, self.creator)


class Comment(Model):
    text = TextField("Text of comment", blank=False, max_length=1000)
    date_create = DateTimeField("Creation date", blank=False, null=False, default=timezone.now)
    user = ForeignKey(User, related_name='comments', on_delete=CASCADE,
                      blank=False, null=False, verbose_name='Author')
    task = ForeignKey(Task, related_name='comments', on_delete=CASCADE,
                      blank=False, null=False, verbose_name='Task')

    def __str__(self):
        return "Comment to task %s text: %s, creator %s" \
               % (self.task.custom_number, self.text, self.user)


class LogTimeTask(Model):
    minutes = IntegerField("Log time in minutes", blank=False, null=False)
    date_logged = DateTimeField("Date of logging", blank=False, null=False)
    description = TextField("Description", blank=True, max_length=500)
    user = ForeignKey(User, related_name='logged_time', on_delete=CASCADE,
                      blank=False, null=False, verbose_name='Performer')
    task = ForeignKey(Task, related_name='logged_time', on_delete=CASCADE,
                      blank=False, null=False, verbose_name='Task')

    def __str__(self):
        return "Logged time in minutes %s for task %s, user %s" \
               % (self.minutes, self.task.custom_number, self.user)
