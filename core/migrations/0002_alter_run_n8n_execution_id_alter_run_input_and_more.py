# Generated manually for schema changes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='run',
            name='n8n_execution_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.RenameField(
            model_name='run',
            old_name='input_params',
            new_name='input',
        ),
        migrations.RemoveField(
            model_name='curatedlist',
            name='locations',
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]