from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_rename_work_date_activity_due_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="activity",
            name="due_date",
            field=models.DateTimeField(),
        ),
    ]
