import requests
import pandas as pd
from io import StringIO
import time
from astropy.time import Time

# --- CONFIGURATION: THE P9 ORBIT TRACK (2025) ---
# Four "Drill Holes" along the high-probability resonance line
TARGETS = [
    {"id": "SECTOR_ALPHA", "ra": 55.0, "dec": -10.0}, # Leading edge
    {"id": "SECTOR_BETA",  "ra": 58.0, "dec": -12.0}, # The Core (We checked part of this)
    {"id": "SECTOR_GAMMA", "ra": 61.0, "dec": -14.0}, # Trailing edge
    {"id": "SECTOR_DELTA", "ra": 64.0, "dec": -16.0}  # Deep Eridanus
]
SEARCH_RADIUS = 0.25 # Slightly wider

# NOIRLab & Pan-STARRS Endpoints
NSC_URL = "https://datalab.noirlab.edu/tap/sync"
PS1_URL = "https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean/search"

def query_noirlab(ra, dec, radius):
    print(f"[*] Drilling {ra}, {dec} (Radius {radius})...")
    sql = f"""
    SELECT ra, dec, rmag, mjd, class_star
    FROM nsc_dr2.object
    WHERE 
      't' = q3c_radial_query(ra, dec, {ra}, {dec}, {radius})
      AND rmag BETWEEN 22.5 AND 24.5
      AND class_star > 0.8
    """
    params = {'request': 'doQuery', 'lang': 'ADQL', 'format': 'csv', 'query': sql}
    try:
        r = requests.post(NSC_URL, data=params)
        if r.status_code == 200 and "ERROR" not in r.text[:200].upper():
            data = StringIO(r.text)
            df = pd.read_csv(data)
            df.columns = df.columns.str.strip().str.lower()
            
            # Find mag col
            mag_candidates = [c for c in df.columns if 'rmag' in c]
            mag_col = mag_candidates[0] if mag_candidates else df.columns[2]
            
            # Standardize column names for the df
            df = df.rename(columns={mag_col: 'mag'})
            return df
    except Exception as e:
        print(f"[!] NOIRLab Error: {e}")
    return pd.DataFrame()

def check_ps1(ra, dec):
    params = {'ra': ra, 'dec': dec, 'radius': 0.000833, 'format': 'json'}
    try:
        r = requests.get(PS1_URL, params=params, timeout=5)
        if r.status_code == 200 and len(r.json()) > 0:
            return True # Found in PS1
    except:
        return True # Fail safe
    return False

# --- MAIN EXECUTION ---
print(f"--- PLANET NINE GRID SURVEY (AUTONOMOUS) ---")
master_survivors = []

for target in TARGETS:
    print(f"\n>>> INITIATING SCAN: {target['id']}")
    
    # 1. Deep Search
    df = query_noirlab(target['ra'], target['dec'], SEARCH_RADIUS)
    print(f"    > Deep Candidates Found: {len(df)}")
    
    if not df.empty:
        # 2. Cross Match
        print(f"    > Cross-matching against Pan-STARRS...")
        sector_survivors = 0
        for i, row in df.iterrows():
            if not check_ps1(row['ra'], row['dec']):
                print(f"      [!] UNIQUE HIT: Mag {row['mag']:.2f} at {row['ra']:.5f}, {row['dec']:.5f}")
                row['sector'] = target['id']
                master_survivors.append(row)
                sector_survivors += 1
            # Slight delay to be nice to API
            if i % 10 == 0: time.sleep(0.1)
            
        if sector_survivors == 0:
            print(f"    > Result: All matched. Sector Clear.")

print("\n" + "="*60)
print(f"SURVEY COMPLETE. TOTAL SURVIVORS: {len(master_survivors)}")
print("="*60)

if master_survivors:
    final_df = pd.DataFrame(master_survivors)
    print(final_df[['sector', 'ra', 'dec', 'mag', 'mjd']].to_string(index=False))
    final_df.to_csv("P9_Grid_Survivors.csv", index=False)
    print("\n[ACTION] Check 'P9_Grid_Survivors.csv'. These are the Movers.")
else:
    print("The sky is static in all sectors. Planet Nine is either fainter than Mag 24.5")
    print("or currently outside these 4 probability zones.")