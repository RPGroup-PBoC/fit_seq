---
status: Rejected
reason: data follows exact opposite trend
---

# 2020-07-16 Plate Reader Growth Measurement

## Purpose
The purpose of this experiment is to obtain high precision measurements of cell
growth in M9 minimal media with 0.75 µg/mL tetracycline.

## Strain Information

| Plasmid | Genotype | Host Strain | Shorthand |
| :------ | :------- | ----------: | --------: |
| `pZS4*5-mCherry`| `galK<>2*lacUV5-tetA-C51m` | HG105 |`UV5 mCh` |
| `pZS4*5-mCherry`| `galK<>2*WTlac-tetA-C51m` | HG105 |`WT mCh` |
| `pZS4*5-mCherry`| `galK<>2*3.19kBT-tetA-C51m` | HG105 |`3.19 mCh` 
| `pZS4*5-CFP`| `galK<>2*lacUV5-tetA-C51m` | HG105 |`UV5 CFP` |
| `pZS4*5-CFP`| `galK<>2*WTlac-tetA-C51m` | HG105 |`WT CFP` |
| `pZS4*5-CFP`| `galK<>2*3.19kBT-tetA-C51m` | HG105 |`3.19 CFP` 

## Plate Layout

**96 plate layout**

![plate layout](output/plate_layout.png)


## Notes & Observations

In this experiment we only use a single tetracycline concentration in the hope
to get higher reproducibility for multiple technical replicates in the same
plate. The tetracycline concentration was based on the results from `20200715`
in which 0.5 µg/mL seemed too low.

Just as in `20200715` here we opted for simply inoculating 10 µL of the
saturated M9 culture.

## Analysis Files

**Whole Plate Growth Curves**

![plate layout](output/growth_plate_summary.png)

**Whole Plate Growth Rate Inferences**

![plate layout](output/growth_rate_summary.png)

## Experimental Protocol

1. Cells as described in "Strain Information" were grown to saturation in 4 mL
   of LB + Kan + Spec in 15 mL culture tubes at 37ºC and 250 rpm.

2. Cells were diluted 1:1000 into 4 mL of M9 + 0.5% glucose + Kan + Spec after ≈
   8 hours of growth in LB. These M9 cultures were grown overnight at 37ºC and
   250 rpm.

3. 10 µL of the saturated M9 culture was then added into 300 µL of M9  with
   different tetracycline concentrations according to the plate layout
   information.

4. The plate was placed in a Biotek Gen5 plate reader and grown at 37ºC, shaking
   in a linear mode at the fastest speed. OD600 and YFP Measurements were taken
   every 25 minutes for approximately 24 hours.

## Conclusions

Conclusions come from a qualitative assessment of the data based on the 
`growth_plate_reader_exploration.ipynb` file.

The data follows the exact opposite trend. It is very possible that the plate
was inverted and in reality the cells are behaving as expected, but because of
the lack of other way to check for this, the data is then useless.