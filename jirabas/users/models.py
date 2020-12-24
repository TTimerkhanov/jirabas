from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, Model, TextField


class User(AbstractUser):
    name = CharField("Name of User", blank=True, max_length=255)

    def __str__(self):
        return self.name


class Role(Model):
    name = CharField("Name", blank=False, max_length=255, unique=True, db_index=True)
    description = TextField("Description", blank=True, max_length=700)

    def __str__(self):
        return f"Role {self.name}"

    @classmethod
    def get_project_manager(cls) -> "Role":
        return cls.objects.get(name="Проектный менеджер")
