import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv('.env')

cfg = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'healthcare_db'),
}

print("Trying to connect with:", cfg['user'], "@", cfg['host'], "db:", cfg['database'])

try:
    conn = mysql.connector.connect(**cfg)
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    print("Connected! Current DB:", cursor.fetchone())
    cursor.execute("SHOW TABLES;")
    print("Tables:", cursor.fetchall())
    cursor.close()
    conn.close()
except Exception as e:
    print("Connection failed:", str(e))
