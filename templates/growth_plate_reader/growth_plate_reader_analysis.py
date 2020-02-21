# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import string
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import evo_mwc.viz
import evo_mwc.fitderiv
import seaborn as sns
import statsmodels.api as sm
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


# Define which analysis to perform
GROUPED = True # Perform analysis per groups
PER_WELL = True  # Perform analysis per well

# Define parameters to group strains by
GROUP = ['strain', 'pos_selection', 'neg_selection']

# Define if you only want to plot existing results
REPLOT = False
# ----------------------------------

# Load the data.
data = pd.read_csv(f'output/{DATE}_r{RUN_NO}_growth_plate.csv')

# Generate a dictionary of the mean blank at each time point.
blank_vals = {t: val['OD600'].mean() for t, val in
              data[data['strain'] == 'blank'].groupby(['time_min'])}

# Add mean blank values for each time point to the dataframe,
# as well as background subtracted OD values.
for k, v in blank_vals.items():
    data.loc[data['time_min'] == k, 'blank_val'] = v
data['OD_sub'] = data['OD600'] - data['blank_val']

# ----------------------------------
# Compute growth rate for grouped data

# Group data by selected criteria
data_group = data.groupby(GROUP)
# List groups
groups = [group for group, data in data_group]

# Initialize data frame to save derivatives
columns = list(data.columns) + ['logOD_fit', 'logOD_fit_std',
                                'growth_rate', 'growth_rate_std',
                                'doubling_time', 'doubling_time_std']
df_gp = pd.DataFrame(columns=columns)

# Check if the analysis should be done
if (not REPLOT) & (GROUPED):
    # Loop through groups
    for group, df in data_group:
        # Check if the group is not a blank
        if (group[0] == 'blank'):
            continue
        print(group)
        # Build input as required by the Gaussian process function.
        # This is time as  an array and then the OD as a 2D array with a column
        # per replica
        # Obtain time
        time = np.sort(df['time_min'].unique())
        # List wells in group
        wells = list(df.well.unique())
        # Extract OD measurements into the corresponding array
        if len(wells) == 1:  # For cases with one replica only
            OD = df[df.well == wells[0]].sort_values(by='time_min').OD600.values
        else:  # For cases with multiple replicas
            OD = np.zeros([len(time), len(wells)])
            # Loop through wells
            for i, well in enumerate(wells):
                # Extract OD data and sort by time (just in case)
                OD[:, i] = df[df.well ==
                              well].sort_values(by='time_min').OD600.values

        # Using the package [`fitderiv`]
        # (http://swainlab.bio.ed.ac.uk/software/fitderiv/)
        # from Peter Swain's lab,
        # perform non-parametric inference of the time-dependent growth rates.
        gp = evo_mwc.fitderiv.fitderiv(time, OD)

        # Create dataframe with full time series results of the fit
        gp_df = gp.export('NONE', savegp=False, savestats=False)
        # List columns to be saved
        gp_df = gp_df[['t', 'log(OD)', 'log(OD) error',
                       'gr', 'gr error']]
        # Rename some columns to remove undesired characters
        gp_df.rename(columns={'log(OD)': 'logOD_fit',
                              'log(OD) error': 'logOD_fit_std',
                              'gr': 'growth_rate',
                              'gr error': 'growth_rate_std',
                              't': 'time_min'}, inplace=True)
        # Compute doubling time
        gp_df['doubling_time'] = np.log(2) / gp_df['growth_rate']
        # Compute doubling time STD
        gp_df['doubling_time_std'] = np.log(2) * gp_df['growth_rate_std'] /\
                                     (gp_df['growth_rate']**2)

        # List information that is missing from this dataframe
        miss_cols = [col for col in df.columns if col not in gp_df]

        gp_df = pd.concat([gp_df.reset_index(drop=True),
                           df[df.well ==
                           wells[0]][miss_cols].reset_index(drop=True)],
                          axis=1)

        # Append dataframe
        df_gp = pd.concat([df_gp, gp_df], ignore_index=True)

    # Export result
    df_gp.to_csv(f'output/{DATE}_r{RUN_NO}_gp_grouped.csv',
                 index=False)

# Perform plots for grouped data
if GROUPED:
    # Read derivatives
    df_gp = pd.read_csv(f'output/{DATE}_r{RUN_NO}_gp_grouped.csv')

    # group derivatives
    df_gp_group = df_gp.groupby(GROUP)
    # Print growth curve and its derivative for each group

    # Initialize multi-page PDF
    with PdfPages('output/growth_rate_grouped.pdf') as pdf:
        # Loop through groups
        for group in groups:
            # check that there are no blanks
            if (group[0] == 'blank'):
                continue
            # Initialize figure
            fig, ax = plt.subplots(2, 1, figsize=(4, 4), sharex=True)
            # Extract curve data
            growth_data = data_group.get_group(group)
            rate_data = df_gp_group.get_group(group)
            # Plot plate reade data
            ax[0].plot(growth_data.time_min, growth_data.OD600, lw=0,
                       marker='.')
            # Plot growth rate with credible region
            ax[1].plot(rate_data.time_min, rate_data.growth_rate)
            ax[1].fill_between(rate_data.time_min,
                               rate_data.growth_rate +
                               rate_data.growth_rate_std,
                               rate_data.growth_rate -
                               rate_data.growth_rate_std,
                               alpha=0.5)
            # Label plot
            ax[0].set_title(str(group))
            ax[0].set_ylabel(r'OD$_{600}$')
            ax[1].set_ylabel(r'growth rate (min$^{-1}$)')
            ax[1].set_xlabel('time (min)')
            plt.tight_layout()
            pdf.savefig()
            plt.close()


# ----------------------------------
# Compute growth rate for individual well data

# Group data by well and strain
# NOTE: The strain grouping is to remove blanks from analysis
data_group = data.groupby(['well', 'strain'])
# List groups
groups = [group for group, data in data_group]

# Initialize data frame to save derivatives
columns = list(data.columns) + ['logOD_fit', 'logOD_fit_std',
                                'growth_rate', 'growth_rate_std',
                                'doubling_time', 'doubling_time_std']
df_wells = pd.DataFrame(columns=columns)

# Check if the analysis should be done
if (not REPLOT) & (PER_WELL):
    # Loop through groups
    for group, df in data_group:
        # Check if the group is not a blank
        if group[1] == 'blank':
            continue
        print(group)
        # Build input as required by the Gaussian process function.
        # This is time as  an array and then the OD as a 2D array with a column
        # per replica
        # Obtain time
        time = np.sort(df['time_min'].unique())

        # Extract OD measurements into the corresponding array
        OD = df.sort_values(by='time_min').OD600.values
        # Using the package [`fitderiv`]
        # (http://swainlab.bio.ed.ac.uk/software/fitderiv/)
        # from Peter Swain's lab,
        # perform non-parametric inference of the time-dependent growth rates.
        gp = evo_mwc.fitderiv.fitderiv(time, OD)

        # Create dataframe with full time series results of the fit
        gp_df = gp.export('NONE', savegp=False, savestats=False)
        # List columns to be saved
        gp_df = gp_df[['t', 'log(OD)', 'log(OD) error',
                       'gr', 'gr error']]
        # Rename some columns to remove undesired characters
        gp_df.rename(columns={'log(OD)': 'logOD_fit',
                              'log(OD) error': 'logOD_fit_std',
                              'gr': 'growth_rate',
                              'gr error': 'growth_rate_std',
                              't': 'time_min'}, inplace=True)
        # Compute doubling time
        gp_df['doubling_time'] = np.log(2) / gp_df['growth_rate']
        # Compute doubling time STD
        gp_df['doubling_time_std'] = np.log(2) * gp_df['growth_rate_std'] /\
                                     (gp_df['growth_rate']**2)

        # List information that is missing from this dataframe
        miss_cols = [col for col in df.columns if col not in gp_df]

        gp_df = pd.concat([gp_df.reset_index(drop=True),
                           df[miss_cols].reset_index(drop=True)],
                          axis=1)

        # Append dataframe
        df_gp = pd.concat([df_gp, gp_df], ignore_index=True)

    # Export result
    df_gp.to_csv(f'output/{DATE}_r{RUN_NO}_gp_per_well.csv',
                 index=False)

# Perform plots for grouped data
if PER_WELL:
    # Read derivatives
    df_gp = pd.read_csv(f'output/{DATE}_r{RUN_NO}_gp_per_well.csv')

    # group derivatives
    df_gp_group = df_gp.groupby(['well', 'strain'])
    # Print growth curve and its derivative for each group

    # Initialize multi-page PDF
    with PdfPages('output/growth_rate_per_well.pdf') as pdf:
        # Loop through groups
        for group in groups:
            # check that there are no blanks
            if group[1] == 'blank':
                continue
            # Initialize figure
            fig, ax = plt.subplots(2, 1, figsize=(4, 4), sharex=True)
            # Extract curve data
            growth_data = data_group.get_group(group)
            rate_data = df_gp_group.get_group(group)
            # Plot plate reade data
            ax[0].plot(growth_data.time_min, growth_data.OD600, lw=0,
                       marker='.')
            # Plot growth rate with credible region
            ax[1].plot(rate_data.time_min, rate_data.growth_rate)
            ax[1].fill_between(rate_data.time_min,
                               rate_data.growth_rate +
                               rate_data.growth_rate_std,
                               rate_data.growth_rate -
                               rate_data.growth_rate_std,
                               alpha=0.5)
            # Label plot
            ax[0].set_title(str(group))
            ax[0].set_ylabel(r'OD$_{600}$')
            ax[1].set_ylabel(r'growth rate (min$^{-1}$)')
            ax[1].set_xlabel('time (min)')
            plt.tight_layout()
            pdf.savefig()
            plt.close()


    # Make summary figure of growth rates.
    # find number of rows and columns from layout
    layout = pd.read_excel(f'./{DATE}_plate_layout.xlsx', sheet_name='well',
                                 header=None).values
    layout_shape = layout.shape

    # Initlaize plot
    fig, ax = plt.subplots(layout_shape[0], layout_shape[1], figsize=(8, 4),
                           sharex=True, sharey=True)

    # Loop through each well
    for group, df in df_gp_group:
        # Find corresponding row and column of plot
        r, c = [int(x) for x in np.where(layout == group[0])]
        # Set plot axis
        ax[r][c].set_ylim([-0.01, 0.01])
        # Plot growth rate
        ax[r][c].plot(df.sort_values('time_min').time_min,
                      df.sort_values('time_min').growth_rate)
        # increase counter

    # Remove axis from all plots
    ax = ax.ravel() # ravel list of axis

    # Loop through axis
    for a in ax:
        a.get_xaxis().set_visible(False)
        a.get_yaxis().set_visible(False)

    fig.suptitle(f'{DATE}_r{RUN_NO} whole plate growth rates', y=0.95)
    plt.savefig(f'output/growth_rate_summary.png',
                bbox_inches='tight')
