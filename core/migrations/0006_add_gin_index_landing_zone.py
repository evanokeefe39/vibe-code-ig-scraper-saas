# Generated manually for GIN index on data_landing_zone.data

from django.db import migrations, models


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("core", "0005_add_landing_zone_models"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lz_data_gin ON data_landing_zone USING GIN (data);",
                    reverse_sql="DROP INDEX IF EXISTS idx_lz_data_gin;"
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name='datalandingzone',
                    index=models.Index(fields=['data'], name='idx_lz_data_gin'),
                ),
            ],
        ),
    ]