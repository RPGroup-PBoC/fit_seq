#%%
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os
import glob
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import colors
import seaborn as sns
import evo_mwc.viz
import git

# Find home directory for repo
repo = git.Repo("./", search_parent_directories=True)
homedir = repo.working_dir

# matplotlib.use('Agg')
evo_mwc.viz.pboc_style_mpl()

# Find date
workdir = os.getcwd().split('/')[-1]
DATE = int(workdir.split('_')[0])
RUN_NO = int(workdir.split('_')[1][-1])

# List matplotlib colormaps
cmaps = evo_mwc.viz.mpl_cmaps_dict()

#%%
# Read features on plate layout
xl = pd.ExcelFile(f'./{DATE}_plate_layout.xlsx')
# see all sheet names
layout = xl.sheet_names

# Read layout information
layout_info = pd.DataFrame([], columns=layout)
# Loop through layout info
for l in layout:
    # Read corresponding excel page
    info = pd.read_excel(f'./{DATE}_plate_layout.xlsx', sheet_name=l,
                         header=None).values
    # Append to DataFrame
    layout_info[l] = info.ravel()

# Define rows and columns read on plate
layout_info['row']= [x[0] for x in layout_info['well'].values]
layout_info['col']= [x[1:] for x in layout_info['well'].values]

# %%
# Initialize plot
fig, ax = plt.subplots(np.int(np.ceil(len(layout) / 2)) - 1, 2,
                       figsize=(20, 3 * np.int(np.ceil(len(layout) / 2)) - 1))
ax = ax.ravel()
# Initialize counter
i = 0
# Loop through features
for feature in layout:
    # If well, don't add information
    if (feature == 'well') or (feature == 'media'):
        continue
    # Extract strain data and pivot dataframe to obtain proper dimensions
    data = layout_info[['row', 'col', feature]]
    # Add code for categorical data
    data['code'] = data[feature].factorize()[0]

    # Pivot dataframe for both code and label to generate heatmap
    df_code = data.pivot('row', 'col', 'code')
    df_label = data.pivot('row', 'col', feature)

    # Select colormap
    if feature == 'strain':
        cmap = 'tab10'
    else:
        cmap = np.random.choice(cmaps['Sequential'])
    
    # Generate colormap
    sns.heatmap(df_code, cmap=cmap, linewidths=0.3,
                ax=ax[i], annot=df_label.values, fmt='',
                annot_kws={'fontsize':4}, cbar=False)
    # Set plot title
    ax[i].set_title(feature)
    i += 1

# Save it to the output file
if not os.path.exists('./output'):  # Check if directyr exists
    os.mkdir('./output')  # Generate directory if required

plt.savefig('./output/plate_layout.png', bbox_inches='tight',
            dpi=200)