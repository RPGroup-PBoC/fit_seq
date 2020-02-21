# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import string
import os
import glob
import csv
import matplotlib
import matplotlib.pyplot as plt
import evo_mwc.viz
import git

# Find home directory for repo
repo = git.Repo("./", search_parent_directories=True)
homedir = repo.working_dir

matplotlib.use('Agg')
evo_mwc.viz.pboc_style_mpl()

# Find date
workdir = os.getcwd().split('/')[-1]
DATE = int(workdir.split('_')[0])
RUN_NO = int(workdir.split('_')[1][-1])

# ----------------------------------
# Load the data.
file = glob.glob(f'{homedir}/data/plate_reader/{DATE}_r{RUN_NO}_*.csv')[0]
data = pd.read_csv(file, header=None)
# Drop NaNs
data = data.dropna('index', 'any')

# Read features on plate layout
xl = pd.ExcelFile(f'./{DATE}_plate_layout.xlsx')
# see all sheet names
layout = xl.sheet_names

# Read layout information
layout_info = list()  # Initialize list to save layout information
# Loop through layout info
for l in layout:
    # Read corresponding excel page
    info = pd.read_excel(f'./{DATE}_plate_layout.xlsx', sheet_name=l,
                         header=None).values
    # Flatten array to 1D going through columns
    info = info.ravel()
    # Append to list
    layout_info.append(info)

# Set columns for tidy data frame
columns = ['time_min', 'temp_C', 'OD600'] + layout

# Initialize data frame
df = pd.DataFrame(columns=columns)

# Loop through columns to generate tidy data frame
for i, col in enumerate(data.loc[:, 2:].columns):
    # Initialize dataframe to save this particular well data
    df_well = pd.DataFrame(columns=columns)
    # Add time and temperature
    df_well['time_min'] = data.loc[:, 0]
    df_well['temp_C'] = data.loc[:, 1]
    # Add OD600 reads
    df_well['OD600'] = data[col]
    # Add parameters in layout
    for l, param in enumerate(layout):
        # Extract information for particular well and repeat it for each
        # time point
        df_well[param] = layout_info[l][i]
    # Append entries to dataframe
    df = pd.concat([df, df_well])


# Initialize array to save strains operator, repressor and volume marker
op = list()
rep = list()
vol = list()
# Loop through strains
for strain in df.strain:
    # Check if it is not a blanck
    if strain != 'blank':
        op.append(strain.split('_')[0])
        rep.append(int(strain.split('_')[1][1:]))
        vol.append(strain.split('_')[-1])
    else:
        op.append('blank')
        rep.append(None)
        vol.append('blank')
# Add columns to data frame
df['operator'] = op
df['repressor'] = rep
df['volume_marker'] = vol

# Convert the time to minutes
df['time_min'] = df['time_min'].str.split(':').apply(lambda x: int(x[0]) * 60
                                             + int(x[1])+int(x[2])/60)

# Insert identifier information.
df['date'] = DATE
df['run_number'] = RUN_NO

# Save it to the output file
if not os.path.exists('./output'):  # Check if directyr exists
    os.mkdir('./output')  # Generate directory if required
df.to_csv(f'output/{DATE}_r{RUN_NO}_growth_plate.csv', index=False)

# Make summary growth curve figure.
# find number of rows and columns from layout
layout_shape = pd.read_excel(f'./{DATE}_plate_layout.xlsx', sheet_name=l,
                         header=None).values.shape
# Initlaize plot
fig, ax = plt.subplots(layout_shape[0], layout_shape[1], figsize=(8, 4))

# Initialize loop counter
i = 2
# Loop through each position
for r in np.arange(layout_shape[0]):
    for c in np.arange(layout_shape[1]):
        # Set plot axis
        ax[r][c].set_ylim([0, 1.5])
        ax[r][c].get_xaxis().set_visible(False)
        ax[r][c].get_yaxis().set_visible(False)
        # Plot data
        ax[r][c].scatter(data.loc[:, 0],  data.loc[:, i],
                         marker='.', s=0.2)
        # increase counter
        i += 1

fig.suptitle(f'{DATE}_r{RUN_NO} whole plate growth curves', y=0.95)
plt.savefig(f'output/growth_plate_summary.png',
            bbox_inches='tight')
