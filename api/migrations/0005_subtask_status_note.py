from django.db import migrations, models


def set_status_from_completed(apps, schema_editor):
    Subtask = apps.get_model("api", "Subtask")
    Subtask.objects.filter(completed=True).update(status="completed")


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0004_alter_due_date_to_datetimefield"),
    ]

    operations = [
        migrations.AddField(
            model_name="subtask",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("completed", "Completed"),
                    ("postponed", "Postponed"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="subtask",
            name="note",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.RunPython(set_status_from_completed, migrations.RunPython.noop),
    ]
