import mysql.connector

DB_CONFIG = { 'user': 'root', 'password': '', 'host': '127.0.0.1', 'database': 'erp_arts_alu' }
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()
cursor.execute("SELECT * FROM unite")
rows = cursor.fetchall()
print("Units in DB:", rows)
conn.close()
