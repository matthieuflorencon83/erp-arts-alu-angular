
import pandas as pd
import mysql.connector
import os

# Configuration
CSV_PATH = '../backend-node/import_source.csv'
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'erp_arts_alu'
}

def audit_csv():
    print(f"\n=== AUDIT CSV: {CSV_PATH} ===")
    if not os.path.exists(CSV_PATH):
        print("ERROR: CSV file not found!")
        return None
    
    try:
        try:
            df = pd.read_csv(CSV_PATH, dtype=str, encoding='utf-8', sep=';')
        except UnicodeDecodeError:
            df = pd.read_csv(CSV_PATH, dtype=str, encoding='latin-1', sep=';')
            
        print(f"Total Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Check Critical Columns
        critical_cols = ['code_art', 'designation', 'famille', 'fournisseur', 'prix_u_ht']
        for col in critical_cols:
            if col in df.columns:
                missing = df[col].isnull().sum()
                print(f"  - Missing '{col}': {missing}")
            else:
                print(f"  - WARNING: Column '{col}' NOT FOUND in CSV")

        # Check for Duplicates
        if 'code_art' in df.columns:
            dupes = df[df.duplicated('code_art')]
            print(f"  - Duplicate Article Codes: {len(dupes)}")

        # Family Consistency
        if 'famille' in df.columns:
            print("  - Unique Families (Top 10):")
            print(df['famille'].unique()[:10])
            
        return df
    except Exception as e:
        print(f"CSV Error: {e}")
        return None

def audit_db():
    print("\n=== AUDIT DATABASE: erp_arts_alu ===")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Article Count
        cursor.execute("SELECT COUNT(*) as c FROM article")
        art_count = cursor.fetchone()['c']
        print(f"Total Articles in DB: {art_count}")
        
        # Missing Families
        cursor.execute("SELECT COUNT(*) as c FROM article WHERE famille IS NULL OR famille = ''")
        missing_fam = cursor.fetchone()['c']
        print(f"Articles with Missing Family: {missing_fam}")
        
        # Distinct Families (checking case sensitivity issues in DB vs CSV)
        cursor.execute("SELECT DISTINCT famille FROM article LIMIT 10")
        fams = cursor.fetchall()
        print("Sample Families in DB:", [f['famille'] for f in fams])

        # Article-Fournisseur Stats
        cursor.execute("SELECT COUNT(*) as c FROM article_fournisseur")
        link_count = cursor.fetchone()['c']
        print(f"Total Supplier Links: {link_count}")
        
        # Dead Links (Supplier code in link table NOT in supplier table)
        cursor.execute("""
            SELECT COUNT(DISTINCT af.code_fou) as c 
            FROM article_fournisseur af 
            LEFT JOIN fournisseur f ON af.code_fou = f.code_fou 
            WHERE f.code_fou IS NULL
        """)
        dead_links = cursor.fetchone()['c']
        print(f"Orphan Supplier Codes in Links: {dead_links}")
        
        # Specific examples of dead links
        if dead_links > 0:
            cursor.execute("""
                SELECT DISTINCT af.code_fou 
                FROM article_fournisseur af 
                LEFT JOIN fournisseur f ON af.code_fou = f.code_fou 
                WHERE f.code_fou IS NULL
                LIMIT 5
            """)
            orphans = cursor.fetchall()
            print("Sample Orphan Codes:", [o['code_fou'] for o in orphans])
            
    except mysql.connector.Error as err:
        print(f"DB Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    csv_df = audit_csv()
    audit_db()
