from astropy.time import Time
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery.imcce import Skybot

# 1. Set the exact time from your file
# MJD 58394.168441 = 2018-10-03 04:02:33 UTC
obs_time = Time('2018-10-03 04:02:33', scale='utc')

# 2. Set the exact coordinates (RA/Dec)
field_center = SkyCoord(ra=44.9692, dec=-5.0122, unit=(u.deg, u.deg))

# 3. Query SkyBot for objects within 10 arcminutes of this spot
# The Service will return a table of all known asteroids in that field.
print(f"Searching for objects at {field_center} on {obs_time}...")

try:
    results = Skybot.cone_search(field_center, 10*u.arcmin, obs_time)
    
    # 4. Filter for objects bright enough to be seen (e.g., brighter than mag 22)
    visible_objects = results[results['V'] < 22]
    
    if len(visible_objects) > 0:
        print("\nFOUND CANDIDATES:")
        print(visible_objects['Name', 'RA', 'DEC', 'V'])
    else:
        print("No known asteroids found in this field.")

except Exception as e:
    print(f"Error querying database: {e}")
