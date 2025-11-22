import requests
import pandas as pd
import numpy as np
from io import BytesIO
import gzip
from astropy.coordinates import SkyCoord
import astropy.units as u
from tqdm import tqdm

# --- CONFIGURATION: The "Batygin Box" (2025 Refined) ---
SEARCH_RA_MIN = 45.0   # 3h 00m in degrees
SEARCH_RA_MAX = 65.0   # 4h 20m in degrees (Expanded slightly)
SEARCH_DEC_MIN = -20.0
SEARCH_DEC_MAX = -5.0
MIN_MAG = 22.0         # P9 is faint, ignore bright stuff
MAX_MAG = 25.5         # Limit of standard surveys (Rubin goes deeper)

# URL for the MPC's Isolated Tracklet File (ITF)
# Note: The ITF is large. If this URL fails, check the MPC "Identifications" page.
ITF_URL = "https://www.minorplanetcenter.net/iau/ITF/itf.txt.gz" 

def parse_mpc80_line(line):
    """Parses a single line of MPC 80-column format."""
    try:
        # Fixed width format parsing
        # Cols 0-12: ID, 15-32: Date, 32-44: RA, 44-56: Dec, 65-71: Mag
        obj_id = line[0:12].strip()
        
        # Skip header/comments
        if not line[15].isdigit(): return None
        
        # Parse RA (HH MM SS.s) -> Decimal Degrees
        ra_str = line[32:44]
        ra_h = float(ra_str[0:2])
        ra_m = float(ra_str[3:5])
        ra_s = float(ra_str[6:11])
        ra_deg = (ra_h + ra_m/60 + ra_s/3600) * 15
        
        # Parse Dec (sDD MM SS.s) -> Decimal Degrees
        dec_str = line[44:56]
        dec_sign = -1 if dec_str[0] == '-' else 1
        dec_d = float(dec_str[1:3])
        dec_m = float(dec_str[4:6])
        dec_s = float(dec_str[7:11])
        dec_deg = dec_sign * (dec_d + dec_m/60 + dec_s/3600)
        
        # Parse Mag (optional)
        mag_str = line[65:70].strip()
        mag = float(mag_str) if mag_str else np.nan
        
        return {
            "id": obj_id,
            "ra": ra_deg,
            "dec": dec_deg,
            "mag": mag,
            "line": line.strip()
        }
    except Exception:
        return None

def main():
    print(f"--- PLANET NINE SEARCH PROTOCOL (Target: RA {SEARCH_RA_MIN}-{SEARCH_RA_MAX}) ---")
    print(f"Downloading ITF from {ITF_URL} (this may take a moment)...")
    
    try:
        response = requests.get(ITF_URL, stream=True)
        response.raise_for_status()
        
        # Handle gzip if needed, otherwise plain text
        if ITF_URL.endswith('.gz'):
            f = gzip.GzipFile(fileobj=BytesIO(response.content))
        else:
            f = BytesIO(response.content)
            
        candidates = []
        
        # Stream the file line by line to save memory
        for line in tqdm(f, desc="Scanning Tracklets"):
            line_str = line.decode('utf-8')
            parsed = parse_mpc80_line(line_str)
            
            if parsed:
                # SPATIAL FILTER: Is it in the box?
                if (SEARCH_RA_MIN <= parsed['ra'] <= SEARCH_RA_MAX) and \
                   (SEARCH_DEC_MIN <= parsed['dec'] <= SEARCH_DEC_MAX):
                       
                       # MAGNITUDE FILTER: Is it faint enough?
                       if parsed['mag'] > MIN_MAG:
                           candidates.append(parsed)
        
        df = pd.DataFrame(candidates)
        
        if not df.empty:
            print(f"\nFound {len(df)} raw detections in the Primary Target Zone!")
            
            # GROUPING: We need objects with multiple observations (tracklets) to estimate motion
            tracklet_counts = df['id'].value_counts()
            multi_obs = tracklet_counts[tracklet_counts > 1].index
            
            valid_tracklets = df[df['id'].isin(multi_obs)]
            
            print(f"Refined to {len(valid_tracklets['id'].unique())} unique tracklets with motion vectors.")
            
            # Save to CSV for visual inspection
            valid_tracklets.to_csv("P9_Candidates_2025.csv", index=False)
            print("\n>>> SUCCESS: Candidates saved to 'P9_Candidates_2025.csv'")
            print(">>> ACTION: Open this file. Look for IDs where RA changes VERY slowly (< 4 arcsec/hour).")
        else:
            print("\nNo candidates found in the exact box parameters. Try widening the search.")

    except Exception as e:
        print(f"Error: {e}")
        print("Note: If download fails, manually download 'itf.txt' from the MPC Identifications page.")

if __name__ == "__main__":
    main()