# Generated migration to fix Run model user relationship

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_remove_default_icon'),
    ]

    operations = [
        # Add a proper user foreign key field
        migrations.AddField(
            model_name='run',
            name='user_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.user'),
        ),
        
        # Migrate data from user_id to user_fk
        migrations.RunSQL(
            "UPDATE core_run SET user_fk_id = user_id WHERE user_id IS NOT NULL;",
            reverse_sql="UPDATE core_run SET user_id = user_fk_id WHERE user_fk_id IS NOT NULL;"
        ),
        
        # Make the new field not nullable after data migration
        migrations.AlterField(
            model_name='run',
            name='user_fk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.user'),
        ),
        
        # Remove the old user_id field
        migrations.RemoveField(
            model_name='run',
            name='user_id',
        ),
        
        # Rename user_fk to user for consistency
        migrations.RenameField(
            model_name='run',
            old_name='user_fk',
            new_name='user',
        ),
    ]