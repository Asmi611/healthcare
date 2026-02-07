import mysql.connector

cfg = {
    'host': 'localhost',
    'user': 'root',
    'password': '9393aai',  # leave empty string '' if root has no password
}

DB_NAME = 'healthcare_db'

print(f"Connecting as {cfg['user']} to {cfg['host']}...")
conn = mysql.connector.connect(**cfg)
cur = conn.cursor()
cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
cur.close()
conn.close()
print("Database ensured.")

cfg['database'] = DB_NAME
conn = mysql.connector.connect(**cfg)
cur = conn.cursor()

with open('docs/init_db.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

for stmt in [s.strip() for s in sql.split(';') if s.strip()]:
    cur.execute(stmt)
conn.commit()
cur.close()
conn.close()
print("✅ init_db.sql executed successfully.")
