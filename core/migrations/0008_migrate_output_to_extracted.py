# Generated manually for data migration

from django.db import migrations


def migrate_output_to_extracted(apps, schema_editor):
    Run = apps.get_model('core', 'Run')
    for run in Run.objects.filter(output__isnull=False):
        # Assume existing output is extracted entities
        run.extracted = {'result': run.output}
        run.save()


def reverse_migrate_output_to_extracted(apps, schema_editor):
    # Reverse migration: clear extracted if it matches output
    Run = apps.get_model('core', 'Run')
    for run in Run.objects.filter(output__isnull=False, extracted__isnull=False):
        if run.extracted.get('result') == run.output:
            run.extracted = None
            run.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_add_scraped_extracted_fields'),
    ]

    operations = [
        migrations.RunPython(
            migrate_output_to_extracted,
            reverse_migrate_output_to_extracted
        ),
    ]