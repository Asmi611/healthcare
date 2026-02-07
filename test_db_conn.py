from dotenv import load_dotenv
import os, mysql.connector, traceback
load_dotenv('.env.txt')
cfg = {'host':os.getenv('MYSQL_HOST'),'user':os.getenv('MYSQL_USER'),
       'password':os.getenv('MYSQL_PASSWORD'),'database':os.getenv('MYSQL_DB')}
print("Trying:", cfg)
try:
    conn = mysql.connector.connect(**cfg)
    cur = conn.cursor()
    cur.execute("SELECT DATABASE()")
    print("DB:", cur.fetchone())
    cur.execute("SHOW TABLES")
    print("Tables:", cur.fetchall())
    cur.close(); conn.close()
except Exception:
    traceback.print_exc()
