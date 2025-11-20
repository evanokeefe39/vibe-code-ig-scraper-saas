#!/usr/bin/env python
import os
import django
import sys

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibe_scraper.settings')
django.setup()

from core.models import YouTubeVideo, InstagramPost, User

def test_models():
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        print("✓ Created test user")
    else:
        print("✓ Using existing test user")

    print("Testing YouTubeVideo model...")
    try:
        # Create a test video with all required fields
        video = YouTubeVideo.objects.create(
            video_id='test123',
            url='https://youtube.com/watch?v=test123',
            title='Test Video',
            published_at='2023-01-01T00:00:00Z',
            duration_seconds=100,
            channel_name='Test Channel',
            user=user
        )
        print(f"✓ Created video with django_id: {video.id}, video_id: {video.video_id}")

        # Retrieve it
        retrieved = YouTubeVideo.objects.get(video_id='test123')
        print(f"✓ Retrieved video: {retrieved.title}")

        # Clean up
        video.delete()
        print("✓ Test video deleted")

    except Exception as e:
        print(f"✗ YouTubeVideo test failed: {e}")

    print("\nTesting InstagramPost model...")
    try:
        # Create a test post with all required fields
        post = InstagramPost.objects.create(
            instagram_id='test123',
            url='https://instagram.com/p/test123',
            type='Image',
            dimensions_height=100,
            dimensions_width=100,
            display_url='https://example.com/image.jpg',
            timestamp='2023-01-01T00:00:00Z',
            user=user
        )
        print(f"✓ Created post with django_id: {post.id}, instagram_id: {post.instagram_id}")

        # Retrieve it
        retrieved = InstagramPost.objects.get(instagram_id='test123')
        print(f"✓ Retrieved post: {retrieved.type}")

        # Clean up
        post.delete()
        print("✓ Test post deleted")

    except Exception as e:
        print(f"✗ InstagramPost test failed: {e}")

    print("\nAll tests completed!")

if __name__ == '__main__':
    test_models()