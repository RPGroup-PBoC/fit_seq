## `templates`

In this directory we store templates of each experiment descriptions
and processing scripts such that updating them for each experiment is simple.
Specifically we have the files:

- `DATASET_read_counts.py` : This script takes as set of raw `fastq` files, and
  counts how many times each of the unique reads appears on each `fastq` file.
  Each of the files usually corresponds to a different time-point in the
  experiment, such that if an experiment consisted of tracking a population
  through several time points this script counts how many time each individual
  sequence appears on each day.