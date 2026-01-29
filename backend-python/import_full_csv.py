import pandas as pd
import mysql.connector
import sys
import os

CSV_PATH = r"c:\Antigravity\Matt Dev\ERP Arts alu\backend-node\import_source.csv"
DB_CONFIG = { 'user': 'root', 'password': '', 'host': '127.0.0.1', 'database': 'erp_arts_alu' }

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def clean_price(val):
    if pd.isna(val): return 0.0
    s = str(val).replace(',', '.').strip()
    # Remove hidden chars
    s = ''.join(c for c in s if c.isdigit() or c == '.')
    try:
        return float(s)
    except:
        return 0.0

def safe_str(val):
    if pd.isna(val) or str(val).lower() == 'nan': return ""
    return str(val).strip()

def import_full():
    print("Starting Full CSV Import...")
    
    # Read CSV with proper encoding
    try:
        df = pd.read_csv(CSV_PATH, sep=';', encoding='utf-8-sig') # Tried utf-8-sig as seen in READ_FILE output BOOM
        # If utf-8 fails we might try latin-1, but output looked like utf-8
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    print(f"Loaded {len(df)} rows.")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # 1. Ensure Suppliers Exist
    suppliers = df['Fournisseur'].unique()
    print(f"Found {len(suppliers)} unique suppliers.")
    
    code_fou_map = {} 
    
    for supp in suppliers:
        s_name = safe_str(supp)
        if not s_name: continue
        cursor.execute("SELECT code_fou FROM fournisseur WHERE nom_court = %s", (s_name,))
        res = cursor.fetchone()
        if res:
            code_fou_map[s_name] = res[0]
        else:
            try:
                # Generate Code (Max 15 chars approx)
                clean_name = ''.join(c for c in s_name if c.isalnum()).upper()
                slug = clean_name[:10]
                if not slug: slug = "SUP_GEN"
                
                # Try to generate unique code if collision (simplistic)
                new_code = f"SUP_{slug}"
                
                # Check if code already exists (unlikely but safe)
                
                # Insert
                print(f"Creating Supplier: {s_name} -> {new_code}")
                # Schema uses 'nom_client' and 'nom_court'
                cursor.execute("INSERT INTO fournisseur (code_fou, nom_court, nom_client) VALUES (%s, %s, %s)", (new_code, s_name, s_name))
                code_fou_map[s_name] = new_code
            except Exception as e:
                print(f"Failed to create supplier {s_name}: {e}")

    # 2. Ensure Units Exist
    # Map specifically known ones or just insert all
    # CSV units: UN, Barre, Boite, ML, Rlx...
    # DB units: U, M2
    
    # We will Normalize: UN -> U
    unit_map = { 'UN': 'U', 'un': 'U', 'Un': 'U' }
    
    all_units = df['Unité Qte'].unique()
    for u in all_units:
        u_raw = safe_str(u)
        if not u_raw: continue
        
        # Check normalization
        u_code = unit_map.get(u_raw, u_raw)
        
        # Check DB
        cursor.execute("SELECT code FROM unite WHERE code = %s", (u_code,))
        if not cursor.fetchone():
            print(f"Adding new unit: {u_code}")
            try:
                # Assuming 'unite_1' matches 'libelle' logic or we just insert CODE
                # We need to know table columns. 'check_units' showed ('M2', 'Mètre Carré')
                # Let's try inserting just code and unite_1 (libelle)
                # If table has 'unite_1' column? 
                # Let's try generic INSERT
                cursor.execute("INSERT INTO unite (code, unite_1) VALUES (%s, %s)", (u_code, u_code))
            except Exception as e:
                # Fallback if column names differ
                print(f"Failed to insert unit {u_code}: {e}")
                # Try just code?
                try:
                    cursor.execute("INSERT INTO unite (code) VALUES (%s)", (u_code,))
                except:
                    pass

    count = 0
    
    for index, row in df.iterrows():
        try:
            # Map Columns
            ref = safe_str(row.get('Ref fournisseur'))
            if not ref:
                # Fallback: Supplier prefix + index
                supp = safe_str(row.get('Fournisseur'))[:3]
                ref = f"GEN_{supp}_{index}"
            
            designation = safe_str(row.get('Désignation'))
            famille = safe_str(row.get('Famille'))
            ssfamille = safe_str(row.get('Sous famille'))
            fournisseur_name = safe_str(row.get('Fournisseur'))
            fabricant = safe_str(row.get('Fabricant'))
            if not fabricant: fabricant = fournisseur_name
            
            poid = 0 
            
            unite_raw = safe_str(row.get('Unité Qte'))
            unite = unit_map.get(unite_raw, unite_raw)
            if not unite: unite = 'U' # Default
            
            cond = safe_str(row.get('Conditionnement'))
            
            stock_str = safe_str(row.get('tenu en stock')).upper()
            tenu_stock = 1 if 'OUI' in stock_str else 0
            
            prix_ht = clean_price(row.get('Prix/U HT'))
            
            # Upsert Article
            sql_art = """
                INSERT INTO article (code_art, designation, famille, ssfamille, poid, tenu_en_stock, Conditionnement, unite, Fabricant)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                designation=VALUES(designation), famille=VALUES(famille), ssfamille=VALUES(ssfamille),
                tenu_en_stock=VALUES(tenu_en_stock), Conditionnement=VALUES(Conditionnement), unite=VALUES(unite), Fabricant=VALUES(Fabricant)
            """
            cursor.execute(sql_art, (ref, designation, famille, ssfamille, poid, tenu_stock, cond, unite, fabricant))
            
            # Upsert Link Article-Fournisseur
            code_fou = code_fou_map.get(fournisseur_name)
            
            if code_fou:
                # Check if exists to avoid PK error if not upsert supported
                # But ON DUPLICATE should work
                sql_link = """
                    INSERT INTO article_fournisseur (code_art, code_fou, prix_u_ht)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    prix_u_ht=VALUES(prix_u_ht)
                """
                cursor.execute(sql_link, (ref, code_fou, prix_ht))
            
            count += 1
            if count % 1000 == 0:
                print(f"Processed {count}...")
                conn.commit()

        except Exception as e:
            print(f"Row {index} error: {e}")
            # pass

    conn.commit()
    print(f"Import Finished. Processed {count} items.")

if __name__ == "__main__":
    import_full()
