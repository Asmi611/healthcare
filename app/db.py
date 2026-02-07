
# app/db.py
import os
import mysql.connector
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env.txt')
load_dotenv(env_path)

def get_db_connection():
    cfg = {
        'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DB', 'healthcare_db'),
        'port': int(os.getenv('MYSQL_PORT', 3306))
    }
    # small startup / debug banner
    print(f"🔌 DB connect -> host={cfg['host']} user={cfg['user']} db={cfg['database']}")
    conn = mysql.connector.connect(**cfg)
    return conn
