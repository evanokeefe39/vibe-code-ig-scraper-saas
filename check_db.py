import os
import psycopg2
from psycopg2 import sql

# PostgreSQL connection for Docker environment
def check_postgres_tables():
    try:
        # Get database URL from environment (matches docker-compose.yml)
        database_url = os.getenv('DATABASE_URL', 'postgresql://vibe_user:vibe_pass@localhost:5432/vibe_scraper')

        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Query for all tables in the public schema
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print('PostgreSQL Tables:')
        for table in tables:
            print(f'  {table[0]}')

        # Specifically check for core_location
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'core_location'
            );
        """)

        exists = cursor.fetchone()[0]
        print(f'\ncore_location exists: {exists}')

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"PostgreSQL connection failed: {e}")
        print("Make sure PostgreSQL is running and DATABASE_URL is set correctly")

if __name__ == "__main__":
    check_postgres_tables()