import os
import psycopg2
from app.db import dbconfig

def initialize_database():
    conn = None
    try:
        conn = psycopg2.connect(
            host=dbconfig['host'],
            user=dbconfig['user'],
            password=dbconfig['password'],
            database=dbconfig['database'],
            port=dbconfig['port']
        )
        cursor = conn.cursor()
        with open('schema.sql', 'r') as f:
            cursor.execute(f.read())
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    initialize_database()
