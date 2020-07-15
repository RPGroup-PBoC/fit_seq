---
status: Rejected
reason: data makes no sense. clusters in the wrong way
---

# 2020-07-14 Plate Reader Growth Measurement

## Purpose
The purpose of this experiment is to obtain high precision measurements of cell
growth in M9 minimal media with 1 µg/mL tetracycline.

## Strain Information

| Plasmid | Genotype | Host Strain | Shorthand |
| :------ | :------- | ----------: | --------: |
| `pZS4*5-mCherry`| `galK<>2*lacUV5-tetA-C51m` | HG105 |`UV5 mCh` |
| `pZS4*5-mCherry`| `galK<>2*WTlac-tetA-C51m` | HG105 |`WT mCh` |
| `pZS4*5-mCherry`| `galK<>2*3.19kBT-tetA-C51m` | HG105 |`3.19 mCh` 

## Plate Layout

**96 plate layout**

![plate layout](output/plate_layout.png)


## Notes & Observations

In this experiment we only use a single tetracycline concentration in the hope
to get higher reproducibility for multiple technical replicates in the same
plate.

## Analysis Files

**Whole Plate Growth Curves**

![plate layout](output/growth_plate_summary.png)

**Whole Plate Growth Rate Inferences**

![plate layout](output/growth_rate_summary.png)

## Experimental Protocol

1. Cells as described in "Strain Information" were grown to saturation in 4 mL
   of LB + Kan + Spec in 15 mL culture tubes at 37ºC and 250 rpm.

2. Cells were diluted 1:4000 into 4 mL of M9 + 0.5% glucose + Kan + Spec after ≈
   8 hours of growth in LB. These M9 cultures were grown overnight at 37ºC and
   250 rpm.

3. 1 mL of M9 saturated culture was spun down at top speed for 30 seconds. The
   formed pellet was resuspended in 200 µL of fresh M9 for a 5x concentration of
   the cells.

3. 5 µL of the concentrated M9 culture was then added into 300 µL of M9  with
   different tetracycline concentrations according to the plate layout
   information.

4. The plate was placed in a Biotek Gen5 plate reader and grown at 37ºC, shaking
   in a linear mode at the fastest speed. OD600 and YFP Measurements were taken
   every 20 minutes for approximately 24 hours..

## Conclusions

The conclusions here are made from a qualitative assessment of the data based on
the `growth_plate_reader_exploration.ipynb` file.

The data clusters by which side of the plate, rather than by which strain is on
each well. This makes no sense, making the dataset completely useless.