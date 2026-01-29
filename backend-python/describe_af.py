import mysql.connector

DB_CONFIG = { 'user': 'root', 'password': '', 'host': '127.0.0.1', 'database': 'erp_arts_alu' }
conn = mysql.connector.connect(**DB_CONFIG)
c = conn.cursor()
c.execute("DESCRIBE article_fournisseur")
rows = c.fetchall()
c.execute("SELECT * FROM article_fournisseur LIMIT 1")
print([d[0] for d in c.description])
conn.close()
