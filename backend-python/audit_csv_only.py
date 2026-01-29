
import pandas as pd
import os

# Configuration
CSV_PATH = '../backend-node/import_source.csv'

def audit_csv():
    print(f"--- AUDIT REPORT: {os.path.basename(CSV_PATH)} ---")
    if not os.path.exists(CSV_PATH):
        print("ERROR: CSV file not found!")
        return
    
    try:
        # Read with different encoding just in case
        try:
            df = pd.read_csv(CSV_PATH, dtype=str, encoding='utf-8', sep=';')
        except UnicodeDecodeError:
            df = pd.read_csv(CSV_PATH, dtype=str, encoding='latin-1', sep=';')

        print(f"Total Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # 1. Family Analysis
        if 'famille' in df.columns:
            families = df['famille'].dropna().unique()
            print(f"\n[FAMILY ANALYSIS]")
            print(f"Total Unique Families: {len(families)}")
            print("Top 10 Families:")
            print(df['famille'].value_counts().head(10))
            
            # Check for Case Inconsistency
            normalized = df['famille'].str.lower().str.strip()
            unique_norm = normalized.unique()
            if len(unique_norm) < len(families):
                print("\nWARNING: Inconsistent Casing Detected!")
                # Find examples
                for n in unique_norm[:5]:
                    matches = df[df['famille'].str.lower().str.strip() == n]['famille'].unique()
                    if len(matches) > 1:
                        print(f"  - '{n}': Found mismatches {list(matches)}")

        # 2. Supplier Analysis
        if 'fournisseur' in df.columns:
            print(f"\n[SUPPLIER ANALYSIS]")
            suppliers = df['fournisseur'].dropna().unique()
            print(f"Total Unique Suppliers: {len(suppliers)}")
            print(df['fournisseur'].value_counts().head(5))
        
        # 3. Code Analysis
        if 'code_art' in df.columns:
            print(f"\n[CODE ANALYSIS]")
            total = len(df)
            unique = df['code_art'].nunique()
            print(f"Unique Codes: {unique} / {total}")
            if total != unique:
                print(f"DUPLICATE CODES FOUND: {total - unique}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    audit_csv()
