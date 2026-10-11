from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0002_alter_faculty_college_alter_faculty_department_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faculty',
            name='research_areas',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
