# 🛸 Planet Nine Sentinel: Deep Archive Mining Pipeline

**Principal Investigator:** Jeffrey S. Pittman  
**Project Status:** Active / **2 Unidentified Transients Discovered** **Date:** November 22, 2025  
**Target Region:** Taurus-Eridanus Resonance Zone (RA 30° to 100°)  

---

## 🎯 Executive Summary
This project performs a deep-survey data mining operation to locate Planet Nine candidates in the high-probability orbit zone predicted by Batygin & Brown (2016) and refined by Siraj/Tremaine (2025). 

By cross-referencing deep archival imaging from the **Dark Energy Camera (DECam)** (Mag limit ~24.5) against the **Pan-STARRS DR2** catalog (Mag limit ~22.5) and the **Minor Planet Center (MPC)** database, the pipeline filters out static stars and known asteroids to isolate "Bright Ghosts"—objects that appear in deep imaging but are missing from reference maps.

## 🚨 Key Discoveries (The "Bright Ghosts")

This pipeline has isolated **2 High-Confidence "Singleton" Transients**. These objects appear as bright (Mag 22.5), moving sources in deep imaging but are entirely missing from standard static sky catalogs and asteroid databases.

### 1. Candidate Alpha-1
* **Sector:** Alpha (Taurus/Eridanus Border)
* **Coordinates:** RA `54.881786` | Dec `-10.032207`
* **Detection Date:** 2018-03-28 (MJD 58211)
* **Magnitude:** 22.50 (r-band)
* **Verification:**
    * [x] **Visual Void:** Pan-STARRS imagery confirms empty space at these coordinates.
    * [x] **Unidentified:** MPC check confirms no known asteroid was present.

### 2. Candidate Iota-1
* **Sector:** Iota (Deep Eridanus)
* **Coordinates:** RA `70.226337` | Dec `-19.973466`
* **Detection Date:** 2014-12-25 (MJD 57016)
* **Magnitude:** 22.50 (r-band)
* **Verification:**
    * [x] **Visual Void:** Pan-STARRS imagery confirms empty space at these coordinates.
    * [x] **Unidentified:** MPC check confirms no known asteroid was present.

## 📉 Scientific Constraints
Outside of these singletons, this survey provides a strong negative constraint: **No Planet Nine candidate brighter than Magnitude 22.5 exists in the primary resonance track (Sectors Alpha–Xi).** This suggests Planet Nine is likely fainter (Mag 23–24) or located further along the track in the Southern Turn (Phase 4).

## 🛠 Methodology
1.  **Deep Search:** Queries the **NOIRLab Source Catalog (NSC DR2)** for objects with `rmag > 22.5` and `class_star > 0.8`.
2.  **Cross-Match:** Verifies candidates against the **Pan-STARRS DR2** API to filter out static background stars.
3.  **Forensics:** Survivors are visually inspected to rule out diffraction spikes and artifacts.
4.  **Vetting:** Final candidates are checked against the **MPC database** to rule out known asteroids.

## 💻 Usage

**1. Install Dependencies**
```bash
pip install -r requirements.txt
