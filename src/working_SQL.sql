SELECT TOP 100 
    id, ra, dec, rmag, class_star, ndet, deltamjd, pmra, pmdec, pmraerr, pmdecerr, flags, gmag, imag, zmag
FROM nsc_dr2.object 
WHERE 't' = Q3C_RADIAL_QUERY(ra, dec, 44.96923917139104, -5.012158395219782, 0.002)

--

SELECT TOP 100 
    id, ra, dec, rmag, class_star, ndet, deltamjd, pmra, pmdec, pmraerr, pmdecerr, flags
FROM nsc_dr2.object 
WHERE 't' = Q3C_RADIAL_QUERY(ra, dec, 45.09533849942762, -5.106197438451599, 0.002)

--

SELECT TOP 100 
    id, ra, dec, rmag, class_star, ndet, deltamjd, pmra, pmdec, pmraerr, pmdecerr, flags
FROM nsc_dr2.object 
WHERE 't' = Q3C_RADIAL_QUERY(ra, dec, 44.96802331107846, -4.866686386493769, 0.002)
