
import pandas as pd

CSV_PATH = '../backend-node/import_source.csv'

try:
    try:
        df = pd.read_csv(CSV_PATH, dtype=str, encoding='utf-8', sep=';')
    except:
        df = pd.read_csv(CSV_PATH, dtype=str, encoding='latin-1', sep=';')

    print(f"Total Rows: {len(df)}")
    cols = df.columns.tolist()
    print(f"Columns: {cols}")
    
    if 'Référence' in cols:
        u_ref = df['Référence'].dropna().nunique()
        print(f"\n[Référence]: {u_ref} unique values.")
        
    if 'Ref fournisseur' in cols:
        u_rf = df['Ref fournisseur'].dropna().nunique()
        print(f"[Ref fournisseur]: {u_rf} unique values.")
        
    # Check overlap
    if 'Référence' in cols and 'Ref fournisseur' in cols:
        diff = df[df['Référence'] != df['Ref fournisseur']]
        print(f"Rows where they differ: {len(diff)}")
        if len(diff) > 0:
            print("Sample Differences:")
            print(diff[['Référence', 'Ref fournisseur']].head(5))

except Exception as e:
    print(e)
