#!/usr/bin/env python3
"""
Universal Database Connection Utility for Vibe Scraper Project
Supports both Docker internal and Docker host access patterns
"""
import os
import sys
import argparse

def get_connection_string(context='auto'):
    """
    Get appropriate database connection string based on context
    
    Args:
        context: 'auto', 'docker', 'host', or 'direct'
    
    Returns:
        tuple: (connection_string, description)
    """
    
    if context == 'auto':
        # Auto-detect based on environment
        if os.getenv('DOCKER_CONTAINER'):
            context = 'docker'
        else:
            context = 'host'
    
    if context == 'docker':
        # Inside Docker container - use service names
        conn_str = "postgresql://postgres:postgres@db:5432/postgres"
        desc = "Docker internal network (service names)"
    elif context == 'host':
        # From Docker host - direct connection to Supabase
        conn_str = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
        desc = "Docker host direct connection"
    elif context == 'direct':
        # Explicit direct connection
        conn_str = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
        desc = "Direct connection to localhost"
    else:
        raise ValueError(f"Unknown context: {context}")
    
    return conn_str, desc

def test_connection(connection_string, description):
    """Test database connection and return results"""
    try:
        import psycopg2
        
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Basic connection test
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        
        # Get table count
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        table_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'description': description,
            'version': version,
            'table_count': table_count,
            'connection_string': connection_string
        }
        
    except Exception as e:
        return {
            'success': False,
            'description': description,
            'error': str(e),
            'connection_string': connection_string
        }

def main():
    parser = argparse.ArgumentParser(description='Test database connections')
    parser.add_argument('--context', choices=['auto', 'docker', 'host', 'direct'], 
                       default='auto', help='Connection context')
    parser.add_argument('--test-all', action='store_true', 
                       help='Test all connection methods')
    
    args = parser.parse_args()
    
    print("=== Vibe Scraper Database Connection Test ===\n")
    
    if args.test_all:
        contexts = ['docker', 'host', 'direct']
    else:
        contexts = [args.context]
    
    results = []
    
    for ctx in contexts:
        conn_str, desc = get_connection_string(ctx)
        print(f"Testing {desc}...")
        print(f"Connection: {conn_str}")
        
        result = test_connection(conn_str, desc)
        results.append(result)
        
        if result['success']:
            print(f"SUCCESS: Connected to PostgreSQL")
            print(f"Version: {result['version'].split(',')[0]}")
            print(f"Tables: {result['table_count']} found")
        else:
            print(f"FAILED: {result['error']}")
        
        print("-" * 60)
    
    # Summary
    successful = [r for r in results if r['success']]
    print(f"\nSummary: {len(successful)}/{len(results)} connections successful")
    
    if successful:
        print("\nRecommended connection string for current environment:")
        print(successful[0]['connection_string'])
    
    return len(successful) > 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)