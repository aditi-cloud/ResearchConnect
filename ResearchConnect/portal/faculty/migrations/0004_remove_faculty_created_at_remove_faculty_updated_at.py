from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0003_alter_faculty_research_areas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='faculty',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='faculty',
            name='updated_at',
        ),
    ]
