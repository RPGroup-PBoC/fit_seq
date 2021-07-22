---
status: In Progress
reason: Experiment running
---

# 2021-06-04 Plate Reader Growth Measurement

## Purpose
This experiment is meant to produce our first quantitative data for some of our finalized strains.

## Strain Information

  | Host Strain | Genotype | Shorthand |
| :------ | :------- | ----------: | --------: |
| MG1655| - | MG1655 |
| MG1655| `galK<>3.19kbT+tetO2+RiboJ+tetA+GFP` |3.19|
| MG1655| `galK<>IW+tetO2+RiboJ+tetA+GFP` |IW |


## Plate Layout

**96 plate layout**

![plate layout](output/plate_layout.png)


## Notes & Observations


## Analysis Files

**Whole Plate Growth Curves**

![plate layout](output/growth_plate_summary.png)

**Whole Plate Growth Rate Inferences**

![plate layout](output/growth_rate_summary.png)

## Experimental Protocol

1. Cells as described in "Strain Information" were grown to saturation in 5 mL
of LB at 37C overnight.

1. Cells were diluted 1:1000 into M9 + 0.5% glucose media and grown for 8h

2. The cells were then diluted to a final OD of 0.01 into the plate reader 96 well plate with a
total volume of 300 µL.

4. The plate was placed in a Biotek Gen5 plate reader and grown at 37C, shaking
in a linear mode at the fastest speed. Measurements were taken every 20 minutes
for approximately 20 hours.
