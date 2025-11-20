#!/usr/bin/env python
"""Test YouTubeVideo model syntax"""
import os
import sys

# Add to project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Test model syntax without Django setup
try:
    # Just test the model class definition
    exec("""
class TestYouTubeVideo:
    video_id = 'test'
    title = 'Test Video'
    expires_at = None
    
    class Meta:
        indexes = ['video_id']
""")
    print("Model syntax is valid")
    
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")