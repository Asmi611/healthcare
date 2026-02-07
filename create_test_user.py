# create_test_user.py
from dotenv import load_dotenv
import os
import mysql.connector
from werkzeug.security import generate_password_hash

# load .env
load_dotenv('.env.txt')

cfg = {
    'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'healthcare_db')
}

print("Connecting with:", cfg['user'], "@", cfg['host'], "DB:", cfg['database'])
conn = mysql.connector.connect(**cfg)
cur = conn.cursor()

users = [
    ('Alice Patient','patient','alice@example.com', generate_password_hash('alicepass')),
    ('Dr Bob','doctor','bob@example.com', generate_password_hash('bobpass'))
]

for name, role, email, pw_hash in users:
    try:
        cur.execute(
            "INSERT INTO users (name, role, email, password_hash, phone) VALUES (%s,%s,%s,%s,%s)",
            (name, role, email, pw_hash, None)
        )
    except mysql.connector.Error as e:
        # ignore duplicates and continue
        # you can print/log e if you want details
        pass

conn.commit()
cur.close()
conn.close()
print("Test users ensured: alice@example.com (alicepass) / bob@example.com (bobpass)")
