import pandas as pd
import numpy as np

# --- CONFIGURATION ---
TARGET_MJD = 58211.525916  # The timestamp of your discovery
TARGET_SECTOR = "SECTOR_ALPHA"
TARGET_RA = 54.881786
TARGET_DEC = -10.032207
TIME_WINDOW = 0.2  # Look for hits within +/- 4 hours (0.2 days)

print(f"--- TRACKLET HUNTER ---")
print(f"Target: {TARGET_SECTOR} on MJD {TARGET_MJD}")
print(f"Anchor Position: {TARGET_RA}, {TARGET_DEC}")

try:
    df = pd.read_csv("P9_Grid_Survivors.csv")
    
    # Filter for the specific night and sector
    night_hits = df[
        (df['sector'] == TARGET_SECTOR) & 
        (np.abs(df['mjd'] - TARGET_MJD) < TIME_WINDOW)
    ].copy()
    
    print(f"\n[SEARCH RESULT] Found {len(night_hits)} detections on this night.")
    
    if len(night_hits) > 1:
        print("\n>>> POSSIBLE TRACKLET FOUND! <<<")
        print("These points form a motion vector:")
        
        # Sort by time
        night_hits = night_hits.sort_values('mjd')
        print(night_hits[['ra', 'dec', 'mag', 'mjd']].to_string(index=False))
        
        # Calculate Velocity
        t1 = night_hits.iloc[0]
        t2 = night_hits.iloc[-1]
        
        dt_hours = (t2['mjd'] - t1['mjd']) * 24.0
        if dt_hours > 0:
            # Calculate spherical distance (approximate)
            dra = (t2['ra'] - t1['ra']) * np.cos(np.deg2rad(t1['dec']))
            ddec = t2['dec'] - t1['dec']
            dist_deg = np.sqrt(dra**2 + ddec**2)
            dist_arcsec = dist_deg * 3600
            
            velocity = dist_arcsec / dt_hours
            
            print("\n" + "="*40)
            print(f"CALCULATED VELOCITY: {velocity:.2f} arcsec/hour")
            print("="*40)
            
            if velocity < 5.0:
                print(">>> VERDICT: PLANET NINE CANDIDATE (Slow Mover)")
            elif velocity > 20.0:
                print(">>> VERDICT: MAIN BELT ASTEROID (Fast Mover)")
            else:
                print(">>> VERDICT: DISTANT OBJECT (Centaur/Kuiper Belt)")
    else:
        print("\nResult: Only 1 detection found.")
        print("We have a 'Singleton'. We cannot calculate speed without a second point.")
        print("This remains an Unidentified Transient, but orbit is indeterminate.")

except Exception as e:
    print(f"Error: {e}")