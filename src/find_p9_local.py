import pandas as pd
import numpy as np
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import SkyCoord
from tqdm import tqdm
import re

# --- CONFIGURATION: 2025 SEARCH PARAMETERS ---
SEARCH_RA_MIN = 45.0   # 3h
SEARCH_RA_MAX = 68.0   # 4h 32m
SEARCH_DEC_MIN = -30.0
SEARCH_DEC_MAX = -5.0

# DISCARD only if it has a magnitude AND is brighter than 15 (Main Belt)
DISCARD_BRIGHTER_THAN = 15.0 

FILENAME = 'itf.txt'

def parse_mag(mag_str):
    """Returns float mag or None if empty."""
    try:
        if not mag_str or mag_str.isspace(): return None
        match = re.search(r"(\d+\.\d+|\d+)", mag_str)
        if match:
            return float(match.group(1))
        return None
    except:
        return None

def parse_date_bulletproof(date_chunk):
    """
    Manually handles 'YYYY MM DD.ddddd' to avoid Astropy ISO errors.
    """
    try:
        # Regex: Group 1=Year, 2=Month, 3=Day(Int), 4=Decimal(Optional)
        match = re.search(r"(19\d{2}|20\d{2})\s+(\d{2})\s+(\d{2})(\.\d+)?", date_chunk)
        
        if match:
            y, m, d = match.group(1), match.group(2), match.group(3)
            decimal_part = match.group(4)
            
            # 1. Create base time from integer date (Safe for Astropy)
            iso_base = f"{y}-{m}-{d}"
            t = Time(iso_base, format='iso', scale='utc')
            
            # 2. Add the decimal portion directly to MJD
            mjd = t.mjd
            if decimal_part:
                mjd += float(decimal_part)
                
            return mjd
        return None
    except:
        return None

def parse_line(line):
    try:
        if len(line) < 60: return None
        
        # --- 1. SPATIAL PARSE (Do this first for speed) ---
        ra_str = line[32:44]
        dec_str = line[44:56]
        
        if not ra_str[0].isdigit() and ra_str[0] != ' ': return None

        # RA
        ra_h = float(ra_str[0:2])
        ra_m = float(ra_str[3:5])
        ra_s = float(ra_str[6:])
        ra_deg = (ra_h + ra_m/60 + ra_s/3600) * 15.0

        # Check RA Box
        if not (SEARCH_RA_MIN <= ra_deg <= SEARCH_RA_MAX): return None

        # Dec
        dec_sign = -1 if dec_str[0] == '-' else 1
        dec_d = float(dec_str[1:3])
        dec_m = float(dec_str[4:6])
        dec_s = float(dec_str[7:])
        dec_deg = dec_sign * (dec_d + dec_m/60 + dec_s/3600)
        
        # Check Dec Box
        if not (SEARCH_DEC_MIN <= dec_deg <= SEARCH_DEC_MAX): return None

        # --- 2. MAG PARSE ---
        mag_str = line[65:70]
        mag = parse_mag(mag_str)
        
        # Filter: Only toss if BRIGHT (Low mag number)
        if mag is not None and mag < DISCARD_BRIGHTER_THAN:
            return None

        # --- 3. DATE PARSE (The Bulletproof Version) ---
        date_chunk = line[14:32]
        mjd = parse_date_bulletproof(date_chunk)
        if not mjd: return None

        return {
            'id': line[0:12].strip(),
            'mjd': mjd,
            'ra': ra_deg,
            'dec': dec_deg,
            'mag': mag if mag is not None else np.nan
        }
    except:
        return None

def main():
    print(f"--- PLANET NINE BULLETPROOF SEARCH ---")
    print(f"Target: RA {SEARCH_RA_MIN}-{SEARCH_RA_MAX} | Dec {SEARCH_DEC_MIN} to {SEARCH_DEC_MAX}")
    
    candidates = []
    
    with open(FILENAME, 'r') as f:
        f.seek(0, 2) 
        size = f.tell()
        f.seek(0)
        pbar = tqdm(total=size, unit='B', unit_scale=True, desc="Extracting")
        
        for line in f:
            pbar.update(len(line))
            res = parse_line(line)
            if res:
                candidates.append(res)
        pbar.close()
        
    print(f"\nRaw Objects in Zone: {len(candidates)}")
    
    if len(candidates) == 0:
        print("Still 0? Then the file is empty or the Box is empty (which contradicts X-Ray).")
        return

    # --- MOTION ANALYSIS ---
    print("Calculating velocity vectors...")
    df = pd.DataFrame(candidates)
    
    # Filter for multiple observations
    counts = df['id'].value_counts()
    multi_obs_ids = counts[counts > 1].index
    df_filtered = df[df['id'].isin(multi_obs_ids)]
    
    unique_ids = df_filtered['id'].unique()
    print(f"Tracklets with motion: {len(unique_ids)}")
    
    final_suspects = []
    
    for uid in tqdm(unique_ids, desc="Computing Orbits"):
        group = df_filtered[df_filtered['id'] == uid].sort_values('mjd')
        
        t_start = group.iloc[0]
        t_end = group.iloc[-1]
        dt_hours = (t_end['mjd'] - t_start['mjd']) * 24.0
        
        if dt_hours > 0.5:
            c1 = SkyCoord(ra=t_start['ra']*u.deg, dec=t_start['dec']*u.deg)
            c2 = SkyCoord(ra=t_end['ra']*u.deg, dec=t_end['dec']*u.deg)
            sep_arcsec = c1.separation(c2).arcsec
            velocity = sep_arcsec / dt_hours
            
            # P9 FILTER: 0.5 to 5.0 arcsec/hour
            if 0.5 < velocity < 5.0:
                avg_mag = group['mag'].mean()
                final_suspects.append({
                    'ID': uid,
                    'Vel': round(velocity, 3),
                    'Mag': round(avg_mag, 1) if not np.isnan(avg_mag) else "N/A",
                    'RA': round(t_start['ra'], 4),
                    'Dec': round(t_start['dec'], 4),
                    'Obs': len(group),
                    'Arc(hr)': round(dt_hours, 1)
                })

    if final_suspects:
        res_df = pd.DataFrame(final_suspects).sort_values('Vel')
        print("\n" + "="*60)
        print(f"!!! PLANET NINE CANDIDATES: {len(res_df)} !!!")
        print("="*60)
        print(res_df.head(25).to_string(index=False))
        res_df.to_csv("P9_Bulletproof_Candidates.csv", index=False)
    else:
        print("\nNo candidates in velocity range (0.5-5.0 \"/hr).")

if __name__ == "__main__":
    main()