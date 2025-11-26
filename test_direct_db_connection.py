#!/usr/bin/env python3
"""
Direct PostgreSQL connection test to Supabase
Tests the exact connection string: postgresql://postgres:postgres@127.0.0.1:5432/postgres
"""
import psycopg2
import sys

def test_direct_connection():
    """Test direct PostgreSQL connection"""
    connection_string = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
    
    print("Testing direct PostgreSQL connection to Supabase...")
    print(f"Connection string: {connection_string}")
    print("-" * 60)
    
    try:
        # Establish connection
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        print("SUCCESS: Connection successful!")
        
        # Get PostgreSQL version
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        print(f"PostgreSQL version: {version}")
        
        # List available schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast') 
            ORDER BY schema_name;
        """)
        schemas = cursor.fetchall()
        print(f"Available schemas: {[s[0] for s in schemas]}")
        
        # List tables in public schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"Tables in public schema: {[t[0] for t in tables]}")
        
        # Get table count
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        table_count = cursor.fetchone()[0]
        print(f"Total tables in public schema: {table_count}")
        
        # Check for Django-related tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (table_name LIKE '%_%' OR table_name LIKE 'auth_%' OR table_name LIKE 'django_%')
            ORDER BY table_name;
        """)
        django_tables = cursor.fetchall()
        if django_tables:
            print(f"Django-related tables found: {[t[0] for t in django_tables]}")
        else:
            print("No Django tables found - may need to run migrations")
        
        # Test a simple query
        cursor.execute('SELECT 1 as test_value, NOW() as current_time;')
        test_result = cursor.fetchone()
        print(f"Test query result: {test_result}")
        
        # Get database size
        cursor.execute("""
            SELECT pg_size_pretty(pg_database_size('postgres')) as db_size;
        """)
        db_size = cursor.fetchone()[0]
        print(f"Database size: {db_size}")
        
        cursor.close()
        conn.close()
        
        print("\nSUCCESS: All connection tests passed!")
        print("SUCCESS: Database is accessible and ready for use")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"FAILED: Connection failed: {e}")
        print("\nPossible causes:")
        print("1. PostgreSQL server is not running")
        print("2. Host/IP address is incorrect")
        print("3. Port 5432 is blocked or not accessible")
        print("4. Username/password is incorrect")
        print("5. Database 'postgres' does not exist")
        return False
        
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False

if __name__ == '__main__':
    success = test_direct_connection()
    sys.exit(0 if success else 1)