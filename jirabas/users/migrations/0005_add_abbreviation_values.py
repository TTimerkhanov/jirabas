from django.db import migrations

abbreviations = {
    "Проектный менеджер": "PM",
    "Аналитик": "AN",
    "Ответственный за качество": "QA",
    "Лидер разработчиков": "DL",
    "Тестировщик": "TST",
    "Разработчик": "DEV"
}


def add_abbreviation(apps, schema_editor):
    # We can't import the Role model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Role = apps.get_model('users', 'Role')
    for role in Role.objects.all():
        role.abbreviation = abbreviations.get(role.name)
        role.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_role_abbreviation'),
    ]

    operations = [
        migrations.RunPython(add_abbreviation),
    ]
