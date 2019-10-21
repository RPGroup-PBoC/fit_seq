#%%
import os
import glob
import itertools
import numpy as np
import pandas as pd
import skbio

# Import this project's library
import fit_seq 

# Import matplotlib stuff for plotting
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
import matplotlib_venn as mpl_venn

# Seaborn, useful for graphics
import seaborn as sns

#%%
# Define dataset
DATASET = 

# Define file pattern
PATTERN = 

# Define time point position in file name
# For example for a file named:
# 20160519_MG1655_prel_day1_rel.qcfilt.bin2.fastq.gz
# the pattern 'day' is at position [3] when split by '_'
TIME_IDX = 3

# Define data directory
datadir = '../../../data/raw_sequencing/' +\
          f'{DATASET}/'

# Define output dir
outputdir = '../../../data/raw_read_counts/'

# List all fastq.gz files
fastq_files = glob.glob(f'{datadir}{PATTERN}')

#%%
df_seq = pd.DataFrame()
for fastq in fastq_files:
    # Extract time point number
    time = fastq.split('/')[-1].split('_')[TIME_IDX]
    print(f'time {time}: {fastq}')
    # Use skbio to have a generator to iterate over fastq
    seqs = skbio.io.read(fastq,
                         format='fastq',
                         verify=True)

    # Initialize list to save sequence objects
    seq_list = list()
    # Iterate over sequences
    # initialize counter
    counter = 0
    for seq in seqs:
        if counter%100000 == 0:
            print(f'count # {counter}')
        # Extract sequence information
        sequence = str(skbio.DNA(sequence=seq,
                                 validate=False))
        # Append to list
        seq_list.append([sequence])
        # Update counter
        counter += 1

     # Initialize dataframe to save sequences
    names = ['sequence']
    df = pd.DataFrame.from_records(seq_list, columns=names)

    # Add bin number to dataframe
    df['time'] =  [time] * len(df)
    
    # Append to dataframe
    df_seq = df_seq.append(df, ignore_index=True)

#%%
# Group by day
df_group = df_seq.groupby('time')

# Initialize dataframe to save counts
df_counts = pd.DataFrame()

print('counting alleles')
# Loop through days
for time, data in df_group:
    print(time)
    # Count unique entries
    counts = data['sequence'].value_counts()
    # Extract index
    idx = counts.index.values
    # Generate dataframe
    df = pd.DataFrame({'sequence': idx,
                       'counts': list(counts),
                       'time': [time] * len(counts)})
    # Append to general dataframe
    df_counts = df_counts.append(df, ignore_index=True)

print('write file into memory')
df_counts.to_csv(outputdir + f'{DATASET}_read_count.csv', index=False)