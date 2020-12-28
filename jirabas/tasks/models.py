from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    FloatField,
    ForeignKey,
    IntegerField,
    Model,
    TextField,
)
from django.utils import timezone

from jirabas.tasks.enums import PriorityTask, RelationType, StatusTask, TypeTask
from jirabas.users.models import Role, User


class Project(Model):
    name = CharField("Name", blank=False, max_length=255)
    short_name = CharField("Short name", blank=False, max_length=4)
    description = TextField("Description", blank=True, max_length=2000)
    date_start = DateTimeField(
        "Date start", blank=False, null=False, default=timezone.now
    )
    date_finish = DateTimeField("Date finish", blank=True, null=True)

    def __str__(self):
        return "Project %s " % self.name


class ProjectMembership(Model):
    project = ForeignKey(
        Project,
        related_name="members",
        on_delete=CASCADE,
        blank=False,
        null=False,
        verbose_name="Project",
    )
    member = ForeignKey(
        User,
        related_name="projects",
        on_delete=CASCADE,
        blank=False,
        null=False,
        verbose_name="Members of project",
    )
    role = ForeignKey(
        Role,
        related_name="roles",
        on_delete=CASCADE,
        blank=False,
        null=False,
        verbose_name="Role of member",
    )

    class Meta:
        unique_together = ["project", "member"]

    def __str__(self):
        return "Project %s member %s role %s" % (self.project, self.member, self.role)


class Task(Model):
    custom_number = CharField("Number of task", blank=False, max_length=20)
    name = CharField("Name of task", blank=False, max_length=255)
    description = TextField("Description", blank=True, max_length=5000)
    status = CharField(
        max_length=2, choices=StatusTask.choices, default=StatusTask.BACKLOG
    )
    type = CharField(max_length=3, choices=TypeTask.choices, default=TypeTask.WORK_ITEM)
    acceptance_criteria = TextField("Acceptance criteria", blank=True, max_length=2000)
    priority = CharField(
        max_length=3, choices=PriorityTask.choices, default=PriorityTask.MEDIUM
    )
    estimate_hours = IntegerField("Estimate task in hours", blank=True, null=True)

    date_created = DateTimeField(
        "Creation date", blank=False, null=False, default=timezone.now
    )
    date_modified = DateTimeField("Modification date", blank=True, null=True)
    deadline_date = DateTimeField("Deadline date", blank=True, null=True)

    creator = ForeignKey(
        User,
        related_name="creator_tasks",
        on_delete=CASCADE,
        blank=False,
        null=False,
        verbose_name="Creator of task",
    )
    project = ForeignKey(
        Project,
        related_name="tasks",
        on_delete=CASCADE,
        blank=False,
        null=False,
        verbose_name="Project",
    )
    performer = ForeignKey(
        User,
        related_name="performer_tasks",
        on_delete=CASCADE,
        blank=True,
        null=True,
        verbose_name="Performer of task",
    )


class TasksRelation(Model):
    PAIRS = {
        RelationType.IS_BLOCKED_BY: RelationType.BLOCKS,
        RelationType.IS_CLONED_BY: RelationType.CLONES,
        RelationType.HAS_TEST_CASE: RelationType.COVERS_REQUIREMENT,
        RelationType.RELATES: RelationType.RELATES,
    }

    from_task = ForeignKey(
        Task,
        related_name="child_tasks",
        on_delete=CASCADE,
        blank=False,
        null=False,
    )

    to_task = ForeignKey(
        Task,
        related_name="parent_tasks",
        on_delete=CASCADE,
        blank=False,
        null=False,
    )

    relation_type = IntegerField(choices=RelationType.choices)


class Comment(Model):
    text = TextField("Text of comment", blank=False, max_length=1000)
    date_create = DateTimeField(
        "Creation date", blank=False, null=False, default=timezone.now
    )
    user = ForeignKey(
        User,
        related_name="comments",
        on_delete=CASCADE,
        blank=False,
        null=False,
        verbose_name="Author",
    )
    task = ForeignKey(
        Task,
        related_name="comments",
        on_delete=CASCADE,
        blank=False,
        null=False,
        verbose_name="Task",
    )

    def __str__(self):
        return "Comment to task %s text: %s, creator %s" % (
            self.task.custom_number,
            self.text,
            self.user,
        )


class LogTimeTask(Model):
    hours = FloatField(blank=False, default=0.0)

    date_logged = DateTimeField(
        "Date of logging", blank=False, null=False, default=timezone.now
    )
    description = TextField("Description", blank=True, max_length=500)
    user = ForeignKey(
        User,
        related_name="logged_time",
        on_delete=CASCADE,
        blank=False,
        null=False,
        verbose_name="Performer",
    )
    task = ForeignKey(
        Task,
        related_name="logged_time",
        on_delete=CASCADE,
        blank=False,
        null=False,
        verbose_name="Task",
    )

    def __str__(self):
        return "Logged time in %s hours for task %s, user %s" % (
            self.hours,
            self.task.custom_number,
            self.user,
        )
