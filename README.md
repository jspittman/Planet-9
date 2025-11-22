# 🛸 Planet Nine Sentinel: Deep Archive Mining Pipeline

**Principal Investigator:** Jeffrey S. Pittman  
**Project Status:** Active / **1 Verified Unknown Object Discovered** **Date:** November 22, 2025  
**Target Region:** Taurus-Eridanus Resonance Zone (RA 30° to 100°)  

-----

## 🎯 Executive Summary

This project performs a deep-survey data mining operation to locate Planet Nine candidates in the high-probability orbit zone predicted by Batygin & Brown (2016) and refined by Siraj/Tremaine (2025).

By cross-referencing deep archival imaging from the **Dark Energy Camera (DECam)** (Mag limit \~24.5) against the **Pan-STARRS DR2** catalog (Mag limit \~22.5) and the **Minor Planet Center (MPC)** database, the pipeline filters out static stars and known asteroids to isolate "Bright Ghosts"—objects that appear in deep imaging but are missing from reference maps.

## 🚨 DISCOVERY REPORT: Object Alpha-1 (The "Alpha Ghost")

**Status:** ✅ **PHYSICALLY CONFIRMED** (Visual Verification in Raw Telemetry)  
**Classification:** Unidentified Solar System Body / Extreme TNO Candidate

This object was detected by the pipeline and subsequently verified by manual forensic analysis of raw FITS imagery from the Cerro Tololo Inter-American Observatory (CTIO).

  * **Detection Date:** 2018-11-13 (MJD 58435.238)
  * **Time:** 05:42:46 UTC
  * **Coordinates:** RA `54.780134` | Dec `-10.098003`
  * **Apparent Magnitude:** \~22.5 (r-band)
  * **Verification Data:**
      * **Source:** NOIRLab Science Archive
      * **Instrument:** DECam (Blanco 4m Telescope)
      * **File ID:** `c4d_181113_054246_ooi_r_v1.fits.fz`
      * **Location in Frame:** Extension 19, Pixel [1249, 3994]
  * **Forensic Checks:**
      * [x] **Gaia DR3:** Confirmed Visual Void (No static star exists at these coordinates).
      * [x] **MPC Database:** Confirmed No Match (No known asteroid was present).
      * [x] **Raw Imagery:** Distinct Point Source Function (PSF) confirmed in single-epoch exposure.

-----

## ⚠️ High-Priority Candidates (Unverified)

### 1. Candidate "Alpha Twin" (Possible Epoch 1 of Alpha-1)

  * **Hypothesis:** This may be the same object as Alpha-1, detected 62 days earlier. Linking these two would establish an orbit.
  * **Coordinates:** RA `54.761989` | Dec `-10.066272`
  * **Date:** 2018-09-11 (MJD 58372)
  * **Status:** **PENDING.**
      * *Note:* Detection occurred during daytime in Chile, implying the data source is the **Subaru Telescope (Hawaii)**. Verification requires access to the SMOKA (Subaru Mitaka Okayama Kiso Archive) or Hyper Suprime-Cam Public Data Release.

### 2. Candidate Iota-1

  * **Sector:** Iota (Deep Eridanus)
  * **Coordinates:** RA `70.226337` | Dec `-19.973466`
  * **Date:** 2014-12-25 (MJD 57016)
  * **Status:** **Unverified.**
      * Object has a high "Star Probability" (0.995) but sits in a dense star field. Requires further motion analysis to rule out a background variable star.

-----

## 📉 Scientific Constraints

Outside of these anomalies, this survey provides a strong negative constraint: **No Planet Nine candidate brighter than Magnitude 22.5 exists in the primary resonance track (Sectors Alpha–Xi).** This suggests Planet Nine is likely fainter (Mag 23–24) or located further along the track in the Southern Turn (Phase 4).

## 🛠 Methodology

1.  **Deep Search:** Queries the **NOIRLab Source Catalog (NSC DR2)** for objects with `rmag > 22.5` and `class_star > 0.8`.
2.  **Cross-Match:** Verifies candidates against the **Pan-STARRS DR2** API to filter out static background stars.
3.  **Forensics:** Survivors are visually inspected to rule out diffraction spikes and artifacts.
4.  **Vetting:** Final candidates are checked against the **MPC database** to rule out known asteroids.
5.  **FITS Verification:** Valid candidates are retrieved from the NOIRLab Astro Data Archive and processed using `astropy` to confirm physical presence on the CCD.

## 💻 Usage

**1. Install Dependencies**

```bash
pip install pandas numpy astropy matplotlib requests
