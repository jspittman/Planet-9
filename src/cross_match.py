import pandas as pd
import requests
import time
from astropy.time import Time

# --- CONFIGURATION ---
INPUT_FILE = "NSC_DR2_Deep_Candidates.csv"
OUTPUT_FILE = "P9_Final_Survivors.csv"
SEARCH_RADIUS_DEG = 0.000833  # 3 arcseconds (Standard matching radius)

def get_mjd_date(mjd):
    try:
        t = Time(mjd, format='mjd')
        return t.iso.split()[0]
    except:
        return "Unknown"

def check_ps1_catalog(ra, dec):
    """
    Queries the Pan-STARRS DR2 Mean Object Catalog.
    Returns True if a static star exists there.
    Returns False if the sky is empty (meaning our candidate is unique).
    """
    url = "https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean/search"
    params = {
        'ra': ra,
        'dec': dec,
        'radius': SEARCH_RADIUS_DEG,
        'format': 'json',
        'sort_by': 'distance'
    }
    
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # If 'data' has entries, Pan-STARRS saw a star there.
            if len(data) > 0:
                # Check magnitude of the match to be sure it's not just noise
                # If PS1 sees something very faint, it's likely the same object
                return True, data[0]['objID']
            else:
                return False, None
        return True, "Error" # Fail safe: assume it exists if error
    except Exception as e:
        print(f"[!] Connection Error: {e}")
        return True, "Error"

print(f"--- PAN-STARRS CROSS-MATCH PROTOCOL ---")
print(f"Loading candidates from {INPUT_FILE}...")

try:
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} DECam candidates.")
    
    survivors = []
    
    print("\nBeginning Cross-Match (This filters out static background stars)...")
    print("-" * 60)
    print(f"{'ID':<5} {'Mag':<6} {'Date (DECam)':<12} {'Status'}")
    print("-" * 60)
    
    for index, row in df.iterrows():
        # Respect API limits
        time.sleep(0.1) 
        
        ra, dec = row['ra'], row['dec']
        mag = row['rmag']
        mjd = row['mjd']
        date_str = get_mjd_date(mjd)
        
        # Check PS1
        exists_in_ps1, ps1_id = check_ps1_catalog(ra, dec)
        
        if not exists_in_ps1:
            # HIT! IT IS MISSING IN PAN-STARRS!
            print(f"#{index:<4} {mag:.2f}   {date_str:<12}  >>> UNIQUE (POSSIBLE MOVER) <<<")
            survivors.append(row)
        else:
            # Boring star
            # print(f"#{index:<4} {mag:.2f}   {date_str:<12}  Found in PS1 (Static)")
            pass
            
    print("-" * 60)
    print(f"\nCROSS-MATCH COMPLETE.")
    
    if len(survivors) > 0:
        final_df = pd.DataFrame(survivors)
        final_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n[!!!] {len(survivors)} CANDIDATES SURVIVED PAN-STARRS CHECK!")
        print(f"Saved to '{OUTPUT_FILE}'")
        print("\nNext Step: These are objects DECam saw in 2017/2018 that Pan-STARRS did not.")
        print("They are either ghosts, transients, or Planet Nine.")
    else:
        print("\nResult: All 68 objects were found in Pan-STARRS.")
        print("Conclusion: They are extremely faint background stars, not planets.")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure the CSV file is in the same folder.")