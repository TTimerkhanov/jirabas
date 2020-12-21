from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, Model, TextField, ForeignKey, DateTimeField, CASCADE, IntegerField, SET_NULL
from django.utils.translation import gettext_lazy as _


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
    date_start = DateTimeField("Date start", blank=False, null=False)
    date_finish = DateTimeField("Date finish", blank=False, null=False)

    def __str__(self):
        return "Project %s " % self.name


class Participant(Model):
    project = ForeignKey(Project, related_name='participants', on_delete=CASCADE,
                         blank=False, null=False, verbose_name='Project')
    participant = ForeignKey(User, related_name='projects', on_delete=CASCADE,
                             blank=False, null=False, verbose_name='Participant of project')
    role = ForeignKey(Role, related_name='roles', on_delete=CASCADE,
                      blank=False, null=False, verbose_name='Role of participant')

    def __str__(self):
        return "Project %s participant %s role %s" % (self.project, self.participant, self.role)


class TypeTask(Model):
    type = CharField("Name of type", blank=False, max_length=255)
    description = TextField("Description", blank=True, max_length=700)

    def __str__(self):
        return "Type %s" % self.type


class StatusTask(Model):
    status = CharField("Name of status", blank=False, max_length=255)
    description = TextField("Description", blank=True, max_length=700)

    def __str__(self):
        return "Status %s" % self.status


class PriorityTask(Model):
    priority = CharField("Name of priority", blank=False, max_length=255)
    description = TextField("Description", blank=True, max_length=500)

    def __str__(self):
        return "Priority %s" % self.priority


class TypeRelationTask(Model):
    type = CharField("Name of type", blank=False, max_length=255)
    description = TextField("Description", blank=True, max_length=500)

    def __str__(self):
        return "Type relation tasks %s" % self.type


class Task(Model):
    custom_number = CharField("Number of task", blank=False, max_length=20)
    name = CharField("Name of task", blank=False, max_length=255)
    description = TextField("Description", blank=True, max_length=5000)
    status = ForeignKey(StatusTask, related_name='tasks', on_delete=CASCADE,
                        blank=False, null=False, verbose_name='Status')
    type = ForeignKey(TypeTask, related_name='tasks', on_delete=CASCADE,
                      blank=False, null=False, verbose_name='Type')
    project = ForeignKey(Project, related_name='tasks', on_delete=CASCADE,
                         blank=False, null=False, verbose_name='Project')
    acceptance_criteria = TextField("Acceptance criteria", blank=True, max_length=2000)
    creator = ForeignKey(User, related_name='creator_tasks', on_delete=CASCADE,
                         blank=False, null=False, verbose_name='Creator of task')

    performer = ForeignKey(User, related_name='performer_tasks', on_delete=CASCADE,
                           blank=True, null=True, verbose_name='Performer of task')
    date_create = DateTimeField("Creation date", blank=False, null=False)
    date_modified = DateTimeField("Modification date", blank=True, null=True)
    deadline_date = DateTimeField("Deadline date", blank=True, null=True)
    priority = ForeignKey(PriorityTask, related_name='tasks', on_delete=CASCADE,
                          blank=False, null=False, verbose_name='Priority')
    estimate_hours = IntegerField("Estimate task in hours", blank=True, null=True)

    def __str__(self):
        return "Task %s %s, creator %s" \
               % (self.custom_number, self.name, self.creator)


class RelationTask(Model):
    first_task = ForeignKey(Task, related_name='relation_tasks_main', on_delete=CASCADE,
                            blank=False, null=False, verbose_name='Task')
    second_task = ForeignKey(Task, related_name='relation_tasks_second', on_delete=CASCADE,
                             blank=False, null=False, verbose_name='Other task')

    type = ForeignKey(TypeRelationTask, related_name='relation_tasks', on_delete=CASCADE,
                      blank=False, null=False, verbose_name='Type of relation')

    def __str__(self):
        return "Task %s %s task %s" \
               % (self.first_task.custom_number, self.type.type, self.second_task.custom_number)


class Comment(Model):
    text = TextField("Text of comment", blank=False, max_length=1000)
    date_create = DateTimeField("Creation date", blank=False, null=False)
    date_modified = DateTimeField("Modification date", blank=True, null=True)
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
