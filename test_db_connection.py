#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connection to Supabase
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

def test_connection():
    """Test PostgreSQL connection and inspect database"""
    try:
        print("Testing PostgreSQL connection to Supabase...")
        print(f"Connection string: postgresql://postgres:postgres@127.0.0.1:5432/postgres")
        
        with connection.cursor() as cursor:
            # Test basic connection
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            print('✅ Connection successful!')
            print(f'📊 PostgreSQL version: {version}')
            
            # List available schemas
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast') 
                ORDER BY schema_name;
            """)
            schemas = cursor.fetchall()
            print(f'📁 Available schemas: {[s[0] for s in schemas]}')
            
            # List tables in public schema
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f'📋 Tables in public schema: {[t[0] for t in tables]}')
            
            # Get table count
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            table_count = cursor.fetchone()[0]
            print(f'📈 Total tables in public schema: {table_count}')
            
            # Check if Django tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%_%' 
                ORDER BY table_name;
            """)
            django_tables = cursor.fetchall()
            if django_tables:
                print(f'🐸 Django-related tables found: {[t[0] for t in django_tables]}')
            else:
                print('⚠️  No Django tables found - may need to run migrations')
            
            # Test a simple query
            cursor.execute('SELECT 1 as test_value;')
            test_result = cursor.fetchone()[0]
            print(f'🧪 Test query result: {test_result}')
            
        print('\n✅ All connection tests passed!')
        return True
        
    except Exception as e:
        print(f'❌ Connection failed: {e}')
        print(f'🔧 Database settings: {connection.settings_dict}')
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)