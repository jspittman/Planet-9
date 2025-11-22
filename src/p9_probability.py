import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import webbrowser
from io import StringIO

# --- LOAD YOUR DATA (Hardcoded from your output for precision) ---
csv_data = """ID,Vel,Mag,RA,Dec,Obs,Arc_hr
M14xN8H,1.054,18.4,56.3535,-5.5898,3,0.8
8o3c9x4,1.250,21.2,45.1552,-6.1903,2,54.0
29Q0YZ,2.685,16.4,49.2915,-5.0989,4,1.6
29Q0ZH,2.708,18.0,50.7466,-8.4244,4,1.6
2CN056,2.957,19.5,58.1675,-11.6544,4,1.3
29S04U,2.962,18.2,51.0899,-10.1539,4,1.5
29S04T,3.291,18.2,50.9211,-13.9469,4,1.5
2CM0H9,3.317,18.6,54.8138,-6.5892,4,1.7
3AE1UO,3.353,18.6,64.2907,-5.8370,4,2.0
2CN051,3.644,19.0,53.5224,-12.8937,4,1.3
P11nR2G,3.750,21.7,45.5790,-9.6649,3,0.6
29S055,3.871,18.4,56.1568,-11.1708,4,1.5
9CU009,3.957,18.4,47.4237,-7.8588,3,1.8
2CN052,4.067,19.4,55.2360,-15.7404,4,1.3
2CM0GE,4.156,19.0,49.0263,-7.1332,4,1.7
29S05G,4.184,16.6,59.8879,-13.4435,4,1.5
29L00G,4.291,15.9,49.1252,-24.3339,4,1.0
11D01G,4.507,18.5,45.1832,-17.7142,3,1.0
29S05D,4.694,17.8,59.7238,-13.4839,4,1.5
P10hxcF,4.815,22.4,60.6258,-6.7285,3,0.6"""

def calculate_distance(velocity_arcsec_hr):
    """
    Estimates distance based on parallactic motion at opposition.
    Formula: Distance (AU) approx 147 / Velocity (arcsec/hr)
    """
    if velocity_arcsec_hr <= 0: return 0
    return 147.0 / velocity_arcsec_hr

def calculate_p9_score(row):
    """
    Calculates likelihood (0-100%) of being Planet Nine based on 2025 physics.
    """
    # 1. DISTANCE SCORE (Target: 300-600 AU -> Vel 0.25 - 0.5 "/hr)
    # However, your list starts at 1.0 "/hr.
    # 8o3c9x4 is 1.25 "/hr -> ~117 AU. This is a Sednoid.
    
    dist = calculate_distance(row['Vel'])
    
    # P9 Predicted Distance: 350-550 AU
    if 300 <= dist <= 600:
        dist_score = 100
    elif 100 <= dist < 300: # Sednoid / ETNO
        dist_score = 60
    elif 50 <= dist < 100: # Scattered Disk
        dist_score = 20
    else:
        dist_score = 0
        
    # 2. MAGNITUDE SCORE (Target: > 22.5)
    mag = row['Mag']
    if mag >= 23.0:
        mag_score = 100
    elif mag >= 21.0:
        mag_score = 70 # Possible if P9 is brighter/closer
    elif mag >= 19.0:
        mag_score = 10 # Extremely unlikely
    else:
        mag_score = 0 # Impossible (would have been seen by amateurs)
        
    # WEIGHTED TOTAL
    # Motion is physics (hard constraint). Mag is variable (albedo).
    total_prob = (dist_score * 0.7) + (mag_score * 0.3)
    
    return round(total_prob, 1), int(dist)

# --- MAIN EXECUTION ---
df = pd.read_csv(StringIO(csv_data))

# Calculate Scores
scores = []
distances = []
for index, row in df.iterrows():
    prob, dist = calculate_p9_score(row)
    scores.append(prob)
    distances.append(dist)

df['P9_Prob_%'] = scores
df['Est_Dist_AU'] = distances

# Sort by Probability
df_sorted = df.sort_values('P9_Prob_%', ascending=False)

print("-" * 80)
print("PLANET NINE CANDIDATE PROBABILITY ASSESSMENT")
print("-" * 80)
print(df_sorted[['ID', 'Vel', 'Mag', 'Est_Dist_AU', 'P9_Prob_%']].to_string(index=False))

# --- VISUALIZATION ---
plt.figure(figsize=(10, 6))
plt.style.use('dark_background')

# Plot Candidates
sc = plt.scatter(df['Vel'], df['Mag'], c=df['P9_Prob_%'], cmap='coolwarm', s=100, edgecolors='white')
plt.colorbar(sc, label='P9 Probability %')

# Annotate top hits
for i, txt in enumerate(df['ID']):
    if df['P9_Prob_%'].iloc[i] > 30: # Only label interesting ones
        plt.annotate(txt, (df['Vel'].iloc[i], df['Mag'].iloc[i]), xytext=(5, 5), textcoords='offset points', color='yellow', fontsize=8)

# Draw "The P9 Zone" (Target Area)
# Target: Vel < 0.5, Mag > 22
plt.axhspan(22, 25, xmin=0, xmax=0.2, color='green', alpha=0.2, label='Predicted P9 Region')
plt.axvline(x=0.5, color='green', linestyle='--', alpha=0.5)

plt.gca().invert_yaxis() # Brighter stars (lower mag) at top
plt.xlabel('Angular Velocity (arcsec/hour)')
plt.ylabel('Magnitude')
plt.title('Candidate Forensics: Velocity vs Brightness')
plt.grid(True, alpha=0.2)
plt.legend(['Predicted P9 Region'], loc='upper right')

# Save chart
plt.savefig('p9_probability_chart.png')
print("\n>>> Probability Chart saved as 'p9_probability_chart.png'")

# --- RESOLVER LINKS ---
# Generate MPChecker links for the top hit
top_hit = df_sorted.iloc[0]
print("\n" + "="*60)
print(f"RESOLVING TOP HIT: {top_hit['ID']}")
print("="*60)
print(f"Parameters: RA {top_hit['RA']} | Dec {top_hit['Dec']}")
print("Click this link to see if it is a KNOWN object (MPChecker):")

# Create MPChecker URL
# Note: We use a generic date (today) or the specific MJD if we had it parsed fully. 
# For the check, we use a radius search.
mpc_url = f"https://minorplanetcenter.net/cgi-bin/checkmp.cgi?ra={top_hit['RA']}&decl={top_hit['Dec']}&radius=10&limit=20"
print(mpc_url)