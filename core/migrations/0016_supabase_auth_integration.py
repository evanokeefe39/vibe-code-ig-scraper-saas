# Generated migration for Supabase authentication integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_migrate_extraction_prompt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='supabase_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='subscription_tier',
            field=models.CharField(choices=[('free', 'Free'), ('basic', 'Basic'), ('pro', 'Pro'), ('enterprise', 'Enterprise')], default='free', max_length=50),
        ),
    ]