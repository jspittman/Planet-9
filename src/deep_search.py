import requests
import pandas as pd
from io import StringIO
import sys

# --- CONFIGURATION ---
TARGET_RA = 58.0      # 3h 52m
TARGET_DEC = -12.0
SEARCH_RADIUS = 0.2   # degrees
URL = "https://datalab.noirlab.edu/tap/sync"

print(f"--- NOIRLab DEEP SEARCH (ROBUST V4, Q3C) ---")
print(f"Target: RA {TARGET_RA} | Dec {TARGET_DEC} | Radius: {SEARCH_RADIUS} deg")

# Use q3c_radial_query instead of ADQL CONTAINS/POINT/CIRCLE
# NOTE: q3c_radial_query must be lower-case per Data Lab quirks
sql_query = f"""
SELECT ra, dec, rmag, mjd, class_star
FROM nsc_dr2.object
WHERE
  't' = q3c_radial_query(ra, dec, {TARGET_RA}, {TARGET_DEC}, {SEARCH_RADIUS})
  AND rmag BETWEEN 22.5 AND 24.5
  AND class_star > 0.8
"""

params = {
    'request': 'doQuery',
    'lang': 'ADQL',   # Data Lab TAP still wants ADQL here, but allows q3c_* as a function
    'format': 'csv',
    'query': sql_query
}

try:
    print("[*] Sending Q3C radial query (r-band)...")
    response = requests.post(URL, data=params)
    
    if response.status_code == 200:
        # Peek at the first part of the response for TAP/VOTable errors
        head = response.text[:500]
        if "ERROR" in head.upper() and "<VOTABLE" in head.upper():
            print(f"[!] SERVER ERROR:\n{head}")
            sys.exit(1)
        else:
            data = StringIO(response.text)
            df = pd.read_csv(data)
            
            # --- HEADER NORMALIZATION ---
            # Strip whitespace and lowercase all column names
            df.columns = df.columns.str.strip().str.lower()

            print(f"\n[DEBUG] Raw columns from server: {list(df.columns)}")

            # Try to locate the r-band magnitude column robustly
            mag_candidates = [c for c in df.columns if 'rmag' in c]
            
            if not mag_candidates:
                # Fall back to "3rd column is rmag" based on SELECT order
                # (ra, dec, rmag, ...) -> Index 2
                if len(df.columns) > 2:
                    mag_col = df.columns[2]
                    print(f"[!] Could not find 'rmag' by name. Falling back to Index 2: '{mag_col}'")
                else:
                    print("[!] Critical Error: Not enough columns returned.")
                    sys.exit(1)
            else:
                mag_col = mag_candidates[0]
                print(f"[DEBUG] Using magnitude column: '{mag_col}'")

            print(f"\n[SUCCESS] Found {len(df)} deep r-band candidates.")
            
            if not df.empty:
                # Sort by faintest (largest magnitude)
                df_sorted = df.sort_values(mag_col, ascending=False)
                
                print("\nTOP FAINTEST CANDIDATES (r-mag):")
                
                # Build display columns dynamically
                cols_to_show = ['ra', 'dec', mag_col, 'mjd']
                cols_to_show = [c for c in cols_to_show if c in df_sorted.columns]
                
                print(df_sorted[cols_to_show].head(10).to_string(index=False))
                
                filename = "NSC_DR2_Deep_Candidates.csv"
                df_sorted.to_csv(filename, index=False)
                print(f"\n>>> Saved {len(df)} rows to '{filename}'")
                
                print("\n[ANALYSIS STEP]")
                print(f"1. Copy the RA/Dec of the top candidate (Mag {df_sorted.iloc[0][mag_col]:.2f}).")
                print("2. Check Pan-STARRS. If missing there, it's a ghost/P9 candidate.")
            else:
                print("No objects matched the criteria.")
    else:
        print(f"[!] HTTP Error: {response.status_code} - {response.text[:300]}")

except Exception as e:
    print(f"[!] Exception: {e}")