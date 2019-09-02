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
# Define data directory
datadir = '../../data/raw_sequencing/' +\
          '20171114_fitseq_rel_2/rel/'

# Define output dir
outputdir = '../../data/allele_freq/'


# List all fastq.gz files
fastq_files = glob.glob(f'{datadir}*qcfilt.bin*.fastq.gz')

#%%
df_seq = pd.DataFrame()
for fastq in fastq_files:
    # Extract day number
    day = fastq.split('/')[-1].split('_')[3]
    print(f'day {day}: {fastq}')
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
    df['day'] =  [day] * len(df)
    
    # Append to dataframe
    df_seq = df_seq.append(df, ignore_index=True)

#%%
# Group by day
df_group = df_seq.groupby('day')

# Initialize dataframe to save counts
df_counts = pd.DataFrame()

print('counting alleles')
# Loop through days
for day, data in df_group:
    print(day)
    # Count unique entries
    counts = data['sequence'].value_counts()
    # Extract index
    idx = counts.index.values
    # Generate dataframe
    df = pd.DataFrame({'sequence': idx,
                       'counts': list(counts),
                       'day': [day] * len(counts)})
    # Append to general dataframe
    df_counts = df_counts.append(df, ignore_index=True)

print('write file into memory')
df_counts.to_csv(outputdir + 'rel_read_count.csv', index=False)