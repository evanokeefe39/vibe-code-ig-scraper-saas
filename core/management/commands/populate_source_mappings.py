from django.core.management.base import BaseCommand
from core.models import SourceMapping

class Command(BaseCommand):
    help = 'Populate SourceMapping table with updated mappings'

    def handle(self, *args, **options):
        # Clear existing records
        SourceMapping.objects.all().delete()
        self.stdout.write('Cleared existing SourceMapping records')

        # Define mappings
        mappings = [
            ('youtube-video', 'data_youtube_videos', 'youtube', 'YouTube video data'),
            ('youtube-hashtag', 'data_youtube_videos', 'youtube', 'YouTube hashtag search'),
            ('youtube-playlist', 'data_youtube_videos', 'youtube', 'YouTube playlist data'),
            ('youtube-search', 'data_youtube_videos', 'youtube', 'YouTube search results'),
            ('tiktok-video', 'data_tiktok_videos', 'tiktok', 'TikTok video data'),
            ('tiktok-hashtag', 'data_tiktok_videos', 'tiktok', 'TikTok hashtag search'),
            ('tiktok-profile', 'data_tiktok_videos', 'tiktok', 'TikTok profile videos'),
            ('tiktok-search', 'data_tiktok_videos', 'tiktok', 'TikTok search results'),
            ('instagram-post', 'data_instagram_posts', 'instagram', 'Instagram post data'),
            ('instagram-hashtag', 'data_instagram_posts', 'instagram', 'Instagram hashtag search'),
            ('instagram-profile-posts', 'data_instagram_posts', 'instagram', 'Instagram profile posts'),
            ('instagram-profile-reels', 'data_instagram_posts', 'instagram', 'Instagram profile reels'),
            ('instagram-profile-mentions', 'data_instagram_posts', 'instagram', 'Instagram profile mentions'),
            ('instagram-post-comments', 'data_instagram_comments', 'instagram', 'Instagram post comments'),
        ]

        # Create records
        for source_type, target_table, platform, description in mappings:
            SourceMapping.objects.create(
                source_type=source_type,
                target_table=target_table,
                platform=platform,
                description=description
            )

        self.stdout.write(f'Successfully created {len(mappings)} SourceMapping records')