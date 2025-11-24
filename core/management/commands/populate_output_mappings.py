from django.core.management.base import BaseCommand
from core.models import OutputType, SourceOutputMapping, SourceMapping, DataLandingZone

class Command(BaseCommand):
    help = 'Populate OutputType and SourceOutputMapping tables based on existing SourceMapping data'

    def handle(self, *args, **options):
        # Clear existing records (in correct order due to foreign keys)
        DataLandingZone.objects.all().delete()
        SourceOutputMapping.objects.all().delete()
        OutputType.objects.all().delete()
        self.stdout.write('Cleared existing records')

        # Get unique target_tables from SourceMapping to create OutputTypes
        target_tables = set(SourceMapping.objects.values_list('target_table', flat=True))
        self.stdout.write(f'Found target tables: {sorted(target_tables)}')

        # Create OutputType records from target_tables
        output_type_objects = {}
        for target_table in target_tables:
            # Convert target_table to output_type (remove 'data_' prefix)
            output_type = target_table.replace('data_', '')
            display_name = f"{output_type.replace('_', ' ').title()} Data"

            obj = OutputType.objects.create(
                output_type=output_type,
                display_name=display_name,
                field_mappings={}  # Will be populated later with actual field mappings
            )
            output_type_objects[target_table] = obj
            self.stdout.write(f'Created OutputType: {output_type} (from {target_table})')

        # Create SourceOutputMapping records from SourceMapping data
        for source_mapping in SourceMapping.objects.all():
            # Convert source_type to the new format (remove platform prefix)
            # e.g., 'instagram-post-comments' -> 'post-comments'
            parts = source_mapping.source_type.split('-', 1)
            if len(parts) > 1:
                source_type = parts[1]  # Remove platform prefix
            else:
                source_type = parts[0]

            SourceOutputMapping.objects.create(
                platform=source_mapping.platform,
                source_type=source_type,
                output_type=output_type_objects[source_mapping.target_table],
                display_name=source_mapping.description or f"{source_mapping.platform.title()} {source_type.replace('-', ' ').title()}"
            )

        # Add missing YouTube channel source type (not in original SourceMapping)
        if 'data_youtube_videos' in output_type_objects:
            SourceOutputMapping.objects.get_or_create(
                platform='youtube',
                source_type='channel',
                defaults={
                    'output_type': output_type_objects['data_youtube_videos'],
                    'display_name': 'YouTube Channel Videos'
                }
            )

        self.stdout.write(f'Successfully created {len(output_type_objects)} OutputType records')
        self.stdout.write(f'Successfully created {SourceMapping.objects.count()} SourceOutputMapping records')