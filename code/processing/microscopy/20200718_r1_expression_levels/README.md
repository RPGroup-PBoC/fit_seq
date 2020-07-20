---
status: rejected
notes: experiment not finished yet
---

| | |
|-|-|
| __Date__ | 2020-07-18 |
| __Equipment__ | Tenjin Nikon Microscope |
| __User__ | mrazomej |

# Description
The objective of this experiment was to quickly test if the expression level of
the three promoters not only follows the expected rank order, but if it is in
agreement with the predictions from the Sort-Seq energy matrix and the
thermodynamic model.

## Strain infromation
| Genotype | plasmid | Host Strain | Shorthand |
| :------- | :------ | :---------- | :-------- |
| `none` | `pZS4-mCherry` | HG105 | `auto-mCh` |
| `galK<>2*lacUV5-tetA-C51m` | `pZS4-mCherry` | HG105 | `UV5-mCh` |
| `galK<>2*WTlac-tetA-C51m` | `pZS4-mCherry` | HG105 | `WT-mCh` |
| `galK<>2*3.19kBT-tetA-C51m` | `pZS4-mCherry` | HG105 | `3.19-mCh` |
| `none` | `pZS4-CFP` | HG105 | `auto-CFP` |
| `galK<>2*lacUV5-tetA-C51m` | `pZS4-CFP` | HG105 | `UV5-CFP` |
| `galK<>2*WTlac-tetA-C51m` | `pZS4-CFP` | HG105 | `WT-CFP` |
| `galK<>2*3.19kBT-tetA-C51m` | `pZS4-CFP` | HG105 | `3.19-CFP` |


## Microscope settings

* 100x Oil objective
* Exposure time:
1. Brightfield : XX ms
2. mCherry : XX ms
3. YFP : 5 ms

## Experimental protocol

1. The strains were grown overnight in tubes in 4 mL of LB + spec + kan.

2. Next morning they were diluted 1:1000 into 3 mL of M9 + 0.5% glucose - no
   antibiotic for this step. 

3. After 8 hours the cells were diluted 1:10 into M9 + glucose and imaged using
   2% agar pads of 1x PBS buffer.

## Notes & Observations

## Analysis files

**Example segmentation**

![](output/example_segmentation.png)

## Conclusion

Conclusions listed here were obtained from a qualitative assessment of the data
done in the `image_exploration.ipynb` file.

The measurements were too close to the autofluorescent strains. These were done
using the YFP filter cube, but the strains have a sfGFP construct. The scaling
of the mCherry strains looks like is going in the right direction, but it is
hard to conclude anything from this data given the wrong filter cube.