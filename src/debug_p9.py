import re
import sys

# --- CONFIGURATION ---
SEARCH_RA_MIN_DEG = 45.0
SEARCH_RA_MAX_DEG = 67.5
SEARCH_DEC_MIN = -30.0
SEARCH_DEC_MAX = -5.0
FILENAME = 'itf.txt'

def parse_coordinate(coord_str):
    # Simple sexagesimal to decimal converter
    try:
        parts = coord_str.split()
        if len(parts) == 3:
            d, m, s = float(parts[0]), float(parts[1]), float(parts[2])
            val = abs(d) + m/60 + s/3600
            return val * (-1 if d < 0 or '-' in parts[0] else 1)
    except:
        return None
    return None

def main():
    print(f"--- P9 X-RAY DIAGNOSTIC ---")
    print(f"Inspecting the first 5 objects in the Target Zone...")
    print("-" * 80)

    hits_found = 0
    
    with open(FILENAME, 'r') as f:
        for line in f:
            if len(line) < 60: continue
            
            # Raw Slice (Standard MPC)
            ra_str = line[32:44]   # HH MM SS.s
            dec_str = line[44:56]  # sDD MM SS.s
            
            # Quick Spatial Check
            try:
                # Parse RA
                ra_h = float(ra_str[0:2])
                ra_m = float(ra_str[3:5])
                ra_s = float(ra_str[6:])
                ra_deg = (ra_h + ra_m/60 + ra_s/3600) * 15.0
                
                # Parse Dec
                dec_sign = -1 if dec_str[0] == '-' else 1
                dec_d = float(dec_str[1:3])
                dec_m = float(dec_str[4:6])
                dec_s = float(dec_str[7:])
                dec_deg = dec_sign * (dec_d + dec_m/60 + dec_s/3600)
                
                # CHECK IF IN BOX
                if (SEARCH_RA_MIN_DEG <= ra_deg <= SEARCH_RA_MAX_DEG) and \
                   (SEARCH_DEC_MIN <= dec_deg <= SEARCH_DEC_MAX):
                    
                    hits_found += 1
                    print(f"HIT #{hits_found}")
                    print(f"RAW LINE: {line.rstrip()}")
                    print(f"   > RA: {ra_deg:.4f} | Dec: {dec_deg:.4f}")
                    
                    # Test Date Regex
                    date_chunk = line[14:32]
                    # Improved Regex: allows integer days (no decimal)
                    match = re.search(r"(19\d{2}|20\d{2})\s+(\d{2})\s+(\d{2}(\.\d+)?)", date_chunk)
                    if match:
                        print(f"   > DATE PARSE: SUCCESS ({match.group(0)})")
                    else:
                        print(f"   > DATE PARSE: FAILED (Saw '{date_chunk}')")
                        
                    # Test Mag
                    mag_chunk = line[65:70]
                    print(f"   > MAG PARSE: '{mag_chunk}'")
                    print("-" * 80)
                    
                    if hits_found >= 5:
                        print("Diagnostic Limit Reached. Stopping.")
                        sys.exit()
                        
            except Exception:
                continue

    if hits_found == 0:
        print("Strange... No spatial hits found this time.")

if __name__ == "__main__":
    main()