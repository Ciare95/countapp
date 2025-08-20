import psycopg2
import os
from urllib.parse import urlparse

def check_existing_tables():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found in environment variables")
        return
    
    # Ensure SSL mode for Render
    if "render.com" in database_url and "sslmode" not in database_url:
        database_url += "?sslmode=require"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        
        print("Existing tables:")
        for table in tables:
            print(f"  - {table[0]}")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    check_existing_tables()
