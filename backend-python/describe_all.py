
import mysql.connector

config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'erp_arts_alu'
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("DESCRIBE article")
    columns = cursor.fetchall()
    print("Columns in article table:")
    for col in columns:
        print(f"{col[0]} ({col[1]})")
    
    print("\nColumns in article_fournisseur table:")
    cursor.execute("DESCRIBE article_fournisseur")
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col[0]} ({col[1]})")

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()
