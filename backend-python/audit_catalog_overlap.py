
import pandas as pd

CSV_PATH = '../backend-node/import_source.csv'

def clean_str(x):
    return str(x).strip().upper() if pd.notna(x) else ""

try:
    try:
        df = pd.read_csv(CSV_PATH, dtype=str, encoding='utf-8', sep=';')
    except:
        df = pd.read_csv(CSV_PATH, dtype=str, encoding='latin-1', sep=';')

    # Keys based on previous steps
    REF_COL = 'Ref fournisseur' if 'Ref fournisseur' in df.columns else 'Référence'
    SUP_COL = 'Fournisseur'
    
    print(f"Analyzing Overlap using Key: '{REF_COL}'")
    
    # Filter for overlap candidates (Refs appearing > 1 time)
    counts = df[REF_COL].value_counts()
    multi_refs = counts[counts > 1].index
    
    subset = df[df[REF_COL].isin(multi_refs)]
    print(f"Rows involved in duplication: {len(subset)}")
    print(f"Unique Refs involved: {len(multi_refs)}")
    
    # Columns to check for identity (exclude Supplier and Price obviously)
    cols_to_check = ['Agencement', 'Famille', 'Sous famille', 'Désignation', 'poids', 'superficie', 'unité']
    # Filter valid columns
    cols_to_check = [c for c in cols_to_check if c in df.columns]
    
    conflicts = 0
    perfect_dupes = 0
    
    print(f"Checking consistency on columns: {cols_to_check}")
    
    for ref in multi_refs:
        group = subset[subset[REF_COL] == ref]
        
        # Check if all columns in cols_to_check are identical
        is_identical = True
        diff_tracker = []
        
        first_row = group.iloc[0]
        
        for idx in range(1, len(group)):
            curr_row = group.iloc[idx]
            for c in cols_to_check:
                v1 = clean_str(first_row[c])
                v2 = clean_str(curr_row[c])
                if v1 != v2:
                    is_identical = False
                    diff_tracker.append(f"{c}: '{v1}' vs '{v2}'")
                    
        if is_identical:
            perfect_dupes += 1
        else:
            conflicts += 1
            if conflicts <= 5: # Sample
                suppliers = group[SUP_COL].unique()
                print(f"[Conflict] Ref '{ref}' (Suppliers: {suppliers})")
                print(f"  Differences: {list(set(diff_tracker))}")

    print("\n=== SUMMARY ===")
    print(f"Perfect Duplicates (Metadata Identical): {perfect_dupes}")
    print(f"Conflicts (Metadata Differs): {conflicts}")
    
    if conflicts == 0 and perfect_dupes > 0:
        print("CONCLUSION: All shared references have IDENTICAL metadata. Safe to merge.")
    elif conflicts > 0:
        print("CONCLUSION: Metadata varies between suppliers. Merging might lose data.")

except Exception as e:
    print(e)
