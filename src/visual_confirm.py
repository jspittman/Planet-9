import webbrowser
import sys

# --- TARGET #1 DATA (From your Sector Alpha results) ---
RA = 54.881786
DEC = -10.032207
MAG = 22.50
DATE = "2018-03-28 (MJD 58211)"

def main():
    print(f"--- VISUAL INSPECTION PROTOCOL ---")
    print(f"Target ID: SECTOR_ALPHA_TOP_HIT")
    print(f"Coordinates: RA {RA} | Dec {DEC}")
    print(f"DECam Detection: Mag {MAG} on {DATE}")
    print("-" * 50)
    print("STATUS: DECam saw a bright object here.")
    print("STATUS: Pan-STARRS Catalog says 'Nothing here'.")
    print("-" * 50)
    print("Launching Pan-STARRS Image Cutout service...")
    print(">>> CHECK YOUR BROWSER WINDOW <<<")

    # Construct the precise STScI Cutout URL
    # We request a 'color' stack image, size 240 pixels (approx 1 arcmin)
    url = (
        f"https://ps1images.stsci.edu/cgi-bin/ps1cutouts"
        f"?pos={RA}+{DEC}"
        f"&filter=color"
        f"&filetypes=stack"
        f"&auxiliary=data"
        f"&size=240"
        f"&output_size=0"
        f"&verbose=0"
        f"&autoscale=99.5"
    )
    
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Error launching browser: {e}")
        print(f"Manual Link: {url}")

if __name__ == "__main__":
    main()