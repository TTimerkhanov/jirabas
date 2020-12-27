from django.db.models import TextChoices
from django.db.models.enums import IntegerChoices
from django.utils.translation import gettext_lazy as _


class TypeTask(TextChoices):
    WORK_ITEM = "WI", _("Work item")
    BUG = "BUG", _("Bug")
    REQUIREMENT = "REQ", _("Requirement")
    TEST = "TT", _("Test")
    KNOW_ISSUE = "KI", _("Know issue")


class StatusTask(TextChoices):
    """ Статусы аналитика """

    # поставлена
    BACKLOG = "BL", _("BACKLOG")
    # в процессе (работе)
    IN_PROGRESS = "IP", _("IN_PROGRESS")
    # отложена
    POSTPONED = "PP", _("POSTPONED")
    # завершена
    DONE = "DN", _("DONE")
    # идет с задержкой
    IS_DELAYED = "ID", _("IS_DELAYED")
    # опоздание
    BEING_LATE = "LT", _("BEING_LATE")
    # на ревью
    REVIEW = "RV", _("REVIEW")


class PriorityTask(TextChoices):
    HIGH = "HG", _("HIGH")
    MEDIUM = "MD", _("MEDIUM")
    LOW = "LW", _("LOW")


class RelationType(IntegerChoices):
    IS_BLOCKED_BY = 0, "блокируется"
    BLOCKS = 1, "блокирует"
    IS_CLONED_BY = 2, "имеет дубль"
    CLONES = 3, "дублирует"
    RELATES = 4, "связана"

    HAS_TEST_CASE = 90, "описана тест-кейсом"
    COVERS_REQUIREMENT = 91, "покрывает требования"
