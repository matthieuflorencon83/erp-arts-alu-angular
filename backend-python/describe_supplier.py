import mysql.connector

DB_CONFIG = { 'user': 'root', 'password': '', 'host': '127.0.0.1', 'database': 'erp_arts_alu' }
conn = mysql.connector.connect(**DB_CONFIG)
c = conn.cursor()
c.execute("DESCRIBE fournisseur")
rows = c.fetchall()
for r in rows:
    print(r)
conn.close()
