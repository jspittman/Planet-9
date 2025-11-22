import pandas as pd
import matplotlib.pyplot as plt

# Load your results
file_path = "P9_Grid_Survivors.csv"
print(f"--- ANALYZING {file_path} ---")

try:
    df = pd.read_csv(file_path)
    total = len(df)
    
    # 1. THE NOISE FILTER (Mag > 23.3)
    # Pan-STARRS often misses things fainter than 23.3. These are likely just static stars.
    noise = df[df['mag'] > 23.3]
    
    # 2. THE "BRIGHT GHOST" FILTER (Mag < 23.3)
    # These are bright enough that Pan-STARRS *should* have seen them.
    # The fact that it didn't suggests they MOVED.
    candidates = df[df['mag'] <= 23.3].copy()
    
    print(f"Total Raw Survivors: {total}")
    print(f"Removed Faint Background (Mag > 23.3): {len(noise)}")
    print(f"PRIORITY CANDIDATES (Mag <= 23.3): {len(candidates)}")
    
    if not candidates.empty:
        # Sort by Magnitude (Brightest first = Most suspicious)
        candidates = candidates.sort_values('mag')
        
        print("\n" + "="*60)
        print("TOP 10 'BRIGHT GHOST' CANDIDATES")
        print("(Objects visible to DECam but missing from Pan-STARRS)")
        print("="*60)
        print(candidates[['sector', 'ra', 'dec', 'mag', 'mjd']].head(20).to_string(index=False))
        
        # Visualization
        plt.style.use('dark_background')
        plt.figure(figsize=(10, 6))
        
        # Plot the noise (grey)
        plt.scatter(noise['ra'], noise['dec'], c='grey', s=10, alpha=0.3, label='Faint Stars (Noise)')
        
        # Plot the Candidates (Red)
        plt.scatter(candidates['ra'], candidates['dec'], c='red', s=50, edgecolors='white', label='Bright Ghosts (P9?)')
        
        plt.xlabel('RA')
        plt.ylabel('Dec')
        plt.title(f'P9 Grid Survey: {len(candidates)} Moving Candidates')
        plt.legend()
        plt.grid(True, alpha=0.2)
        
        output_img = "P9_Phase1_Map.png"
        plt.savefig(output_img)
        print(f"\n[VISUAL] Saved detection map to '{output_img}'")
        
        # Save the "Kill List"
        candidates.to_csv("P9_Priority_Targets.csv", index=False)
        print("\n[ACTION] Data saved to 'P9_Priority_Targets.csv'.")
        print("These are the coordinates you must visually inspect.")

except Exception as e:
    print(f"Error reading CSV: {e}")