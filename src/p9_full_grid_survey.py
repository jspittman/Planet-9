import requests
import pandas as pd
from io import StringIO
import time
import sys
import os

# --- CONFIGURATION: THE PLANET NINE "GRAND TOUR" TRACK ---
# Covering every probability zone from the Northern Limit to the Galactic Edge.
# Ordered by Right Ascension (RA).

TARGETS = [
    # --- PHASE 0: THE NORTHERN LIMIT (PISCES / CETUS) ---
    # "Low Probability" - If P9 is closer/faster than models predict.
    {"id": "SECTOR_ZERO_A", "ra": 30.0, "dec": 2.0},
    {"id": "SECTOR_ZERO_B", "ra": 33.0, "dec": 0.0},
    {"id": "SECTOR_ZERO_C", "ra": 36.0, "dec": -1.0},

    # --- PHASE 3: LEADING EDGE (CETUS) ---
    {"id": "SECTOR_ZETA",   "ra": 40.0, "dec": -2.0}, 
    {"id": "SECTOR_ETA",    "ra": 45.0, "dec": -5.0},
    {"id": "SECTOR_THETA_P","ra": 50.0, "dec": -8.0},

    # --- PHASE 1: THE CORE (TAURUS / ERIDANUS BORDER) ---
    # The "Batygin Box" - Highest Probability Resonance Zone
    {"id": "SECTOR_ALPHA",  "ra": 55.0, "dec": -10.0}, # Alpha-1 Found Here
    {"id": "SECTOR_BETA",   "ra": 58.0, "dec": -12.0}, 
    {"id": "SECTOR_GAMMA",  "ra": 61.0, "dec": -14.0}, 
    {"id": "SECTOR_DELTA",  "ra": 64.0, "dec": -16.0},

    # --- PHASE 2: DEEP ERIDANUS ---
    {"id": "SECTOR_THETA",  "ra": 67.0, "dec": -18.0}, 
    {"id": "SECTOR_IOTA",   "ra": 70.0, "dec": -20.0}, # Iota-1 Found Here
    {"id": "SECTOR_KAPPA",  "ra": 73.0, "dec": -22.0}, 
    {"id": "SECTOR_LAMBDA", "ra": 76.0, "dec": -24.0},

    # --- PHASE 3: TRAILING EDGE ---
    {"id": "SECTOR_MU",     "ra": 79.0, "dec": -26.0},
    {"id": "SECTOR_NU",     "ra": 82.0, "dec": -28.0},
    {"id": "SECTOR_XI",     "ra": 85.0, "dec": -30.0},

    # --- PHASE 4: THE SOUTHERN TURN (FORNAX) ---
    # Poorly mapped by Northern surveys. High discovery potential.
    {"id": "SECTOR_OMICRON","ra": 88.0, "dec": -32.0},
    {"id": "SECTOR_PI",     "ra": 91.0, "dec": -34.0},
    {"id": "SECTOR_RHO",    "ra": 94.0, "dec": -36.0},
    {"id": "SECTOR_SIGMA",  "ra": 97.0, "dec": -38.0},

    # --- PHASE 5: THE TAIL (PHOENIX) ---
    # Deep South. Galactic latitude density starts increasing.
    {"id": "SECTOR_TAU",    "ra": 100.0, "dec": -40.0},
    {"id": "SECTOR_UPSILON","ra": 103.0, "dec": -42.0},
    {"id": "SECTOR_PHI",    "ra": 106.0, "dec": -44.0},
    {"id": "SECTOR_CHI",    "ra": 109.0, "dec": -46.0},

    # --- PHASE 6: THE GALACTIC EDGE (COLUMBA / PUPPIS) ---
    # "Lowest of Low Probabilities" - The orbit dives into the Milky Way plane.
    # Extremely high star density makes detection very difficult.
    {"id": "SECTOR_PSI",    "ra": 112.0, "dec": -48.0},
    {"id": "SECTOR_OMEGA",  "ra": 115.0, "dec": -50.0},
    {"id": "SECTOR_INF_A",  "ra": 118.0, "dec": -52.0},
    {"id": "SECTOR_INF_B",  "ra": 121.0, "dec": -54.0}
]

SEARCH_RADIUS = 0.25  # 15 arcmin radius per drill hole
OUTPUT_FILE = "results/P9_Grand_Tour_Survivors.csv"

# API Endpoints
NSC_URL = "https://datalab.noirlab.edu/tap/sync"
PS1_URL = "https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean/search"

def query_noirlab(ra, dec, radius):
    """Queries NOIRLab Source Catalog (Deep DECam Data)"""
    print(f"[*] Drilling {ra}, {dec} (Radius {radius})...")
    
    # We ask for r-band mag between 22.0 and 24.5
    # We ensure it looks like a star (class_star > 0.8)
    sql = f"""
    SELECT ra, dec, rmag, mjd, class_star
    FROM nsc_dr2.object
    WHERE 
      't' = q3c_radial_query(ra, dec, {ra}, {dec}, {radius})
      AND rmag BETWEEN 22.0 AND 24.5
      AND class_star > 0.8
    """
    params = {'request': 'doQuery', 'lang': 'ADQL', 'format': 'csv', 'query': sql}
    
    try:
        r = requests.post(NSC_URL, data=params)
        if r.status_code == 200:
            if "ERROR" in r.text[:200].upper() or "<VOTABLE" in r.text[:200]: 
                print(f"[!] NOIRLab Error: {r.text[:100]}")
                return pd.DataFrame()
                
            data = StringIO(r.text)
            df = pd.read_csv(data)
            df.columns = df.columns.str.strip().str.lower()
            
            # Robustly find the magnitude column
            mag_col = next((c for c in df.columns if 'rmag' in c), None)
            if mag_col:
                df = df.rename(columns={mag_col: 'mag'})
                return df
            elif len(df.columns) > 2:
                 df = df.rename(columns={df.columns[2]: 'mag'})
                 return df
    except Exception as e:
        print(f"[!] Network Error: {e}")
    return pd.DataFrame()

def check_ps1(ra, dec):
    """Queries Pan-STARRS to see if a static star exists there"""
    params = {'ra': ra, 'dec': dec, 'radius': 0.000833, 'format': 'json'}
    try:
        r = requests.get(PS1_URL, params=params, timeout=4)
        if r.status_code == 200 and len(r.json()) > 0:
            return True # Static Star Found
    except:
        return True # Fail safe
    return False

# --- MAIN EXECUTION ---
if not os.path.exists('results'):
    os.makedirs('results')

print(f"--- PLANET NINE GRAND TOUR SURVEY ---")
print(f"Targets: {len(TARGETS)} Sectors (RA 30 to 121)")
print("Filters: Mag 22.0 - 24.5 | Star-like | Missing in Pan-STARRS")

master_survivors = []
total_deep_candidates = 0

for target in TARGETS:
    print(f"\n>>> SCANNING: {target['id']}")
    df = query_noirlab(target['ra'], target['dec'], SEARCH_RADIUS)
    count = len(df)
    total_deep_candidates += count
    print(f"    > Deep Candidates: {count}")
    
    if not df.empty:
        # Artifact Filter: Remove exact 22.000000 (Saturation/Flag)
        df = df[df['mag'] != 22.0]
        
        if df.empty:
            print("    > No valid candidates after artifact cleaning.")
            continue

        print(f"    > Verifying {len(df)} objects against Pan-STARRS...")
        sector_survivors = 0
        
        for i, row in df.iterrows():
            if not check_ps1(row['ra'], row['dec']):
                # Highlight Bright Ghosts immediately
                if row['mag'] < 23.3:
                    print(f"      [!] BRIGHT GHOST: Mag {row['mag']:.2f} at {row['ra']:.5f}, {row['dec']:.5f}")
                
                row['sector'] = target['id']
                master_survivors.append(row)
                sector_survivors += 1
            
            if i % 20 == 0: time.sleep(0.05)
            
        if sector_survivors == 0:
            print(f"    > Sector Clean.")
    else:
        print("    > No candidates found in deep search.")

print("\n" + "="*60)
print(f"GRAND TOUR COMPLETE.")
print(f"Total Objects Scanned: {total_deep_candidates}")
print(f"Total Survivors (Movers): {len(master_survivors)}")
print("="*60)

if master_survivors:
    final_df = pd.DataFrame(master_survivors)
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n[ACTION] Data saved to '{OUTPUT_FILE}'")
    print("[NEXT STEP] Run 'analyze_survivors.py' to update the map.")
else:
    print("No candidates found.")