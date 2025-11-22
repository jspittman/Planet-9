import requests
import urllib.parse

# --- CANDIDATE DATA ---
# Target: 54.881786, -10.032207 -> 03 39 31.6, -10 01 56
# Date: 2018 03 28
# Obs Code: W84

def check_mpc_brute_force():
    print("--- MPC CHECKER: BRUTE FORCE PROTOCOL ---")
    
    url = "https://minorplanetcenter.net/cgi-bin/checkmp.cgi"
    
    # Construct the payload manually to ensure exact formatting
    # The MPC server hates URL-encoded spaces sometimes, but we must try standard form encoding first.
    # We use 'textarea' format which is sometimes more robust on their backend.
    
    payload = {
        'textArea': '03 39 31.6 -10 01 56',
        'obs_code': 'W84',
        'date': '2018 03 28',
        'radius': '15',
        'limit': '5',
        'view': 'xml', # Trying XML output if available, usually ignored but safe
        'mot': 'h'     # Motion in arcsec/hr
    }
    
    try:
        print(f"[*] Sending POST request to MPC for 2018-03-28...")
        # POST request is often handled better than GET for 'checkmp'
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            content = response.text
            
            if "Error from WebCS Script" in content:
                print("[!] MPC Server rejected the format. The server is extremely strict.")
                print("    Retrying with 'GET' method and pre-encoded string...")
                
                # GET Method Retry with explicit string construction
                # We intentionally replace spaces with '+'
                get_params = "ra=03+39+31&decl=-10+01+56&obs_code=W84&date=2018+03+28&radius=15&limit=5"
                full_url = f"{url}?{get_params}"
                
                response_get = requests.get(full_url)
                content = response_get.text
            
            # --- PARSE RESULT ---
            if "The following objects" in content:
                print("\n" + "="*60)
                print(">>> MATCH FOUND: KNOWN ASTEROID")
                print("="*60)
                
                # Extract table lines
                lines = content.split('\n')
                print(f"{'Object':<20} {'RA':<12} {'Dec':<12} {'V_Mag'}")
                print("-" * 50)
                
                found_any = False
                for line in lines:
                    # Look for lines that contain coordinates roughly matching ours
                    if "03 39" in line and "." in line:
                        # Hacky parse of the pre-formatted text
                        # Format is usually: Name RA Dec V Offsets...
                        parts = line.split()
                        if len(parts) > 5:
                            # Find the name (usually start) and V mag (usually near middle)
                            # This is heuristic because HTML parsing failed previously
                            print(f"RAW DATA: {line.strip()[:60]}...")
                            found_any = True
                
                if not found_any:
                    print("   (Could not parse exact line, but header says objects exist.)")
                    print("   Please check browser link manually.")

            elif "No known minor planets" in content:
                print("\n" + "="*60)
                print(">>> RESULT: NO KNOWN OBJECTS")
                print("="*60)
                print("Candidate Alpha-1 is UNIDENTIFIED.")
            
            else:
                print("[!] Unknown response structure.")
                if "Invalid data" in content:
                    print("    Server still returning 'Invalid Data'. The date/RA format is the culprit.")
                else:
                    print(content[:300])

        else:
            print(f"[!] HTTP {response.status_code}")

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    check_mpc_brute_force()