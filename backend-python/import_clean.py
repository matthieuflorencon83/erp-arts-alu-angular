
import pandas as pd
import mysql.connector
import os
import re

# Config
CSV_PATH = '../backend-node/import_source.csv'
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'erp_arts_alu'
}

def clean_price(val):
    if pd.isna(val) or val == '':
        return 0.00
    if isinstance(val, (int, float)):
        return float(val)
    # Replace comma, remove spaces/currency symbols
    val = str(val).replace(',', '.').replace('€', '').replace(' ', '').strip()
    try:
        return float(val)
    except:
        return 0.00

def clean_text(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    return s if s else None

def normalize_case(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    if not s:
        return None
    # Title Case: "PROFIL ALU" -> "Profil Alu"
    return s.title() 

def run_import():
    print("=== STARTING CLEAN IMPORT ===")
    
    # 1. READ CSV
    try:
        try:
            df = pd.read_csv(CSV_PATH, dtype=str, encoding='utf-8', sep=';')
        except UnicodeDecodeError:
            df = pd.read_csv(CSV_PATH, dtype=str, encoding='latin-1', sep=';')
    except Exception as e:
        print(f"FATAL: Could not read CSV. {e}")
        return

    print(f"Loaded {len(df)} rows from CSV.")
    
    # 2. TRANSFORM DATA
    print("Transforming Data...")
    
    articles_data = []
    suppliers_map = {} # Name -> Code
    links_data = []

    for idx, row in df.iterrows():
        # Mapping based on debug_columns.py discovery
        # 'Famille', 'Sous famille', 'Désignation', 'Fournisseur', 'Fabricant', 'Ref fournisseur', ... 'Prix/U HT'
        
        # Mandatory: Code Art (Mapped from 'Ref fournisseur')
        code_art = clean_text(row.get('Ref fournisseur'))
        if not code_art:
            # Fallback check for 'Référence' just in case
            code_art = clean_text(row.get('Référence'))
        
        if not code_art:
           # print(f"Skipping Row {idx}: No Code Art")
           continue
           
        code_art = code_art.upper() # Force Case for Deduplication compatibility with MySQL
            
        designation = clean_text(row.get('Désignation')) or "Sans Nom"
        famille = normalize_case(row.get('Famille'))
        ssfamille = normalize_case(row.get('Sous famille'))
        
        # Smart Family Fill: If Famille is empty but Ssfamille exists, use Ssfamille as Famille?
        # User complained about missing families.
        if not famille and ssfamille:
             famille = ssfamille
             
        fournisseur_nom = clean_text(row.get('Fournisseur'))
        unite = clean_text(row.get('Unité Qte')) or clean_text(row.get('unité'))
        
        prix = clean_price(row.get('Prix/U HT'))
        if prix == 0:
             prix = clean_price(row.get('prix')) # Fallback
             
        # columns 'poids' and 'superficie' might be missing from dataframe if header was cut
        poids = clean_price(row.get('poids')) if 'poids' in row else 0.00
        dimension = clean_text(row.get('superficie')) if 'superficie' in row else None
        
        # Prepare Supplier Code if exists
        code_fou = None
        if fournisseur_nom:
            # Generate a pseudo-code if we don't have one (Assuming CSV provides Name only)
            # Create a consistent code slug
            slug = re.sub(r'[^A-Z0-9]', '', fournisseur_nom.upper())[:10]
            code_fou = f"SUP_{slug}"
            suppliers_map[code_fou] = fournisseur_nom

        stock_val = 0
        stock_str = clean_text(row.get('tenu en stock'))
        if stock_str and stock_str.lower() in ['oui', 'yes', 'true', '1']:
            stock_val = 1
            
        # Article Object
        articles_data.append((
            code_art, designation, famille, ssfamille, 
            unite, poids, dimension, stock_val 
        ))
        
        # Link Object
        if code_fou:
            links_data.append((
                code_art, code_fou, prix
            ))
            
        
    # Remove Duplicate Articles
    unique_articles = {}
    for a in articles_data:
        unique_articles[a[0]] = a 
        
    # Remove Duplicate Links (Keep last price seen)
    unique_links_map = {}
    for l in links_data:
        # l = (code_art, code_fou, prix)
        key = (l[0], l[1])
        unique_links_map[key] = l 
        
    unique_links = list(unique_links_map.values())
        
    # Extract Unique Units
    # a[4] is 'unite' in the tuple (code, des, fam, ssfam, unit, pd, dim, stock)
    unique_units = set([a[4] for a in articles_data if a[4]])
    
    print(f"Unique Articles to Insert: {len(unique_articles)}")
    print(f"Unique Units to Upsert: {len(unique_units)}")
    print(f"Unique Links to Insert: {len(unique_links)}")
    
    # 3. DB OPERATIONS
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("Truncating Tables...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE article_fournisseur")
        cursor.execute("TRUNCATE TABLE article")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # 3.5 INSERT UNITS
        print("Upserting Units...")
        for u in unique_units:
             sql_u = "INSERT INTO unite (code, unite_1) VALUES (%s, %s) ON DUPLICATE KEY UPDATE unite_1 = VALUES(unite_1)"
             cursor.execute(sql_u, (u, u))
             
        # 4. INSERT SUPPLIERS
        print(f"Upserting {len(suppliers_map)} Suppliers...")
        for code, name in suppliers_map.items():
            sql = "INSERT INTO fournisseur (code_fou, nom_court) VALUES (%s, %s) ON DUPLICATE KEY UPDATE nom_court = VALUES(nom_court)"
            cursor.execute(sql, (code, name))
            
        # 5. INSERT ARTICLES
        print("Inserting Articles...")
        sql_art = """
            INSERT INTO article 
            (code_art, designation, famille, ssfamille, unite, poid, dimension, tenu_en_stock)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        batch_art = list(unique_articles.values())
        cursor.executemany(sql_art, batch_art)
        
        # 6. INSERT LINKS
        print(f"Inserting {len(unique_links)} Supplier Links...")
        sql_link = "INSERT INTO article_fournisseur (code_art, code_fou, prix_u_ht) VALUES (%s, %s, %s)"
        cursor.executemany(sql_link, unique_links)
        
        conn.commit()
        print("SUCCESS: Import Completed.")
        
    except mysql.connector.Error as err:
        print(f"DB Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_import()
