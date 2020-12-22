from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class TypeTask(TextChoices):
    WORK_ITEM = 'WI', _('Work item')
    BUG = 'BUG', _('Bug')
    REQUIREMENT = 'REQ', _('Requirement')
    TEST = 'TT', _('Test')
    KNOW_ISSUE = 'KI', _('Know issue')


class StatusTask(TextChoices):
    """ Статусы аналитика """

    # поставлена
    BACKLOG = 'BL', _('BACKLOG')
    # в процессе (работе)
    IN_PROGRESS = 'IP', _('IN_PROGRESS')
    # отложена
    POSTPONED = 'PP', _('POSTPONED')
    # завершена
    DONE = 'DN', _('DONE')
    # идет с задержкой
    IS_DELAYED = 'ID', _('IS_DELAYED')
    # опоздание
    BEING_LATE = 'LT', _('BEING_LATE')

    """ Мои дополнительные """

    # на ревью
    REVIEW = 'RV', _('REVIEW')
    # закрыта
    CLOSED = 'CL', _('CLOSED')


class PriorityTask(TextChoices):
    HIGH = 'HG', _('HIGH')
    MEDIUM = 'MD', _('MEDIUM')
    LOW = 'LW', _('LOW')
