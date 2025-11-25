#!/usr/bin/env python3
"""
Simple Database Query Utility for Agents
Use this for quick database queries without Django overhead
"""
import psycopg2
import sys
import json

def execute_query(query, params=None, fetch_one=False):
    """
    Execute a query against the local Supabase database
    
    Args:
        query (str): SQL query to execute
        params (tuple): Query parameters
        fetch_one (bool): Return single row or all rows
    
    Returns:
        Query results
    """
    connection_string = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
    
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        cursor.execute(query, params or ())
        
        if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount
        
        cursor.close()
        conn.close()
        
        return result
        
    except Exception as e:
        print(f"Database error: {e}")
        return None

def main():
    """Command line interface for database queries"""
    if len(sys.argv) < 2:
        print("Usage: python query_db.py \"SELECT * FROM core_user LIMIT 5\"")
        print("       python query_db.py --list-tables")
        print("       python query_db.py --describe-table core_user")
        sys.exit(1)
    
    query = sys.argv[1]
    
    if query == "--list-tables":
        result = execute_query("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        print("Available tables:")
        for table in result:
            print(f"  - {table[0]}")
    
    elif query == "--describe-table":
        if len(sys.argv) < 3:
            print("Usage: python query_db.py --describe-table table_name")
            sys.exit(1)
        
        table_name = sys.argv[2]
        result = execute_query("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s 
            ORDER BY ordinal_position;
        """, (table_name,))
        
        print(f"Table: {table_name}")
        print("Columns:")
        for col in result:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"  - {col[0]}: {col[1]} ({nullable})")
    
    else:
        result = execute_query(query)
        if result is not None:
            if isinstance(result, list):
                print(f"Query returned {len(result)} rows:")
                for row in result:
                    print(row)
            else:
                print(f"Query result: {result}")

if __name__ == '__main__':
    main()