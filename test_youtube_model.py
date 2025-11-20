#!/usr/bin/env python
"""Simple test script to verify YouTubeVideo model"""
import os
import sys
import django

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibe_scraper.settings')

# Setup Django
django.setup()

# Test imports
try:
    from core.models import YouTubeVideo, User, Run
    print("✅ Successfully imported YouTubeVideo model")
    
    # Test creating a YouTube video instance
    user = User.objects.first()
    if user:
        video = YouTubeVideo(
            video_id='test123',
            title='Test Video',
            url='https://youtube.com/watch?v=test123',
            user=user
        )
        print(f"✅ Successfully created YouTubeVideo instance: {video}")
    else:
        print("❌ No User found in database")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")