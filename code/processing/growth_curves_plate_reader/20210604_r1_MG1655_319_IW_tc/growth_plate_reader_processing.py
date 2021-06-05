# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import string
import os
import glob
import csv
import matplotlib
import matplotlib.pyplot as plt
import fit_seq.viz
import git

# Find home directory for repo
repo = git.Repo("./", search_parent_directories=True)
homedir = repo.working_dir

matplotlib.use('Agg')
fit_seq.viz.pboc_style_mpl()

# List data to be read
TABLES = ["OD600", "YFP"]

# Find date
workdir = os.getcwd().split('/')[-1]
DATE = int(workdir.split('_')[0])
RUN_NO = int(workdir.split('_')[1][-1])
# %%
# Load the data.
file = glob.glob(f'{homedir}/data/plate_reader/{DATE}_r{RUN_NO}_*.csv')[0]

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
# %%
if len(TABLES) > 1:
    ## Find empty lines in file
    # Initialize list to save empty lines index
    empty_line = list()
    # Open data file as text file
    with open(file) as f:
        # Loop through rows
        for i, line in enumerate(f):
            # Find and save empty row index
            if not line.strip():
                empty_line.append(i)
    
    # Read tables and save them into dictionary
    table_dict = {}
    for i, table in enumerate(TABLES):
        table_dict[table] = pd.read_csv(
            file, 
            header=None,
            skiprows=range(empty_line[i * 2] + 1),
            nrows=empty_line[i * 2 + 1] - empty_line[i * 2]
        ).dropna("index", "any")

    # Set columns for tidy data frame
    columns = ['time_min', 'temp_C'] + TABLES + layout
    # Initialize data frame
    df = pd.DataFrame(columns=columns)

    # Loop through columns to generate tidy data frame
    for i, col in enumerate(table_dict[TABLES[0]].loc[:, 2:].columns):
        # Initialize dataframe to save this particular well data
        df_well = pd.DataFrame(columns=columns)
        # Add time and temperature
        df_well['time_min'] = table_dict[TABLES[0]].loc[:, 0]
        df_well['temp_C'] = table_dict[TABLES[0]].loc[:, 1]
        # Add OD600 reads
        df_well[TABLES[0]] = table_dict[TABLES[0]][col]
        df_well[TABLES[1]] = table_dict[TABLES[1]][col]
        # Add parameters in layout
        for l, param in enumerate(layout):
            # Extract information for particular well and repeat it for each
            # time point
            df_well[param] = layout_info[l][i]
        # Append entries to dataframe
        df = pd.concat([df, df_well])

else:
    # Read single table for OD600
    data = pd.read_csv(file, header=None)
    # Drop NaNs
    data = data.dropna('index', 'any')

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


# Initialize array to save strains promoter and volume marker
prom = list()
vol = list()
# Loop through strains
for strain in df.strain:
    # Check if it is not a blanck
    if strain != 'blank':
        prom.append(strain.split('_')[0])
        vol.append(strain.split('_')[-1])
    else:
        prom.append('blank')
        vol.append('blank')
# Add columns to data frame
df['promoter'] = prom
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
        if len(TABLES) == 1:
            ax[r][c].scatter(data.loc[:, 0],  data.loc[:, i],
                            marker='.', s=0.2)
        else:
            ax[r][c].scatter(table_dict["OD600"].loc[:, 0],
                            table_dict["OD600"].loc[:, i],
                            marker='.', s=0.2)

        # increase counter
        i += 1

fig.suptitle(f'{DATE}_r{RUN_NO} whole plate growth curves', y=0.95)
plt.savefig(f'output/growth_plate_summary.png',
            bbox_inches='tight')
