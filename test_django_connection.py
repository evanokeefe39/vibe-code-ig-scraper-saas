#!/usr/bin/env python3
"""
Test Django database connection using current settings
"""
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibe_scraper.settings')

import django
django.setup()

from django.db import connection

def test_django_connection():
    """Test Django database connection"""
    print("Testing Django database connection...")
    print(f"Database settings: {connection.settings_dict['NAME']}@{connection.settings_dict['HOST']}:{connection.settings_dict['PORT']}")
    print("-" * 60)
    
    try:
        with connection.cursor() as cursor:
            # Test basic connection
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            print("SUCCESS: Django connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # List Django tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"Tables accessible via Django: {[t[0] for t in tables]}")
            
            # Test Django migrations
            from django.core.management import call_command
            from io import StringIO
            out = StringIO()
            call_command('showmigrations', '--plan', stdout=out)
            migrations_output = out.getvalue()
            print(f"Django migrations status:\n{migrations_output[:500]}...")
            
        print("\nSUCCESS: Django database connection is working!")
        return True
        
    except Exception as e:
        print(f"FAILED: Django connection failed: {e}")
        print(f"Database settings: {connection.settings_dict}")
        return False

if __name__ == '__main__':
    success = test_django_connection()
    sys.exit(0 if success else 1)