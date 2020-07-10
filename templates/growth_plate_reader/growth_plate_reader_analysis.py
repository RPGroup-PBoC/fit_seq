# -*- coding: utf-8 -*-
# %%
import numpy as np
import pandas as pd
import string
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import fit_seq.viz
import seaborn as sns
import statsmodels.api as sm
import git

# Import libraries necessary for Bayesian analysis
import cmdstanpy
import arviz as az

# Find home directory for repo
repo = git.Repo("./", search_parent_directories=True)
homedir = repo.working_dir

# Define directory where stan file exists
standir = f"{homedir}/fit_seq/stan_code/"

matplotlib.use('Agg')
fit_seq.viz.pboc_style_mpl()

# Find date
workdir = os.getcwd().split('/')[-1]
DATE = int(workdir.split('_')[0])
RUN_NO = int(workdir.split('_')[1][-1])

# Define parameters to group strains by
GROUP = ['strain', 'pos_selection', 'neg_selection']

# Define parameters for HMC run
CHAINS = 6
ITER_SAMPLING = 250

# Define if you only want to plot existing results
REPLOT = False

# %%
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

# %%
# Compute growth rate for individual well data

# Group data by well and strain
# NOTE: The strain grouping is to remove blanks from analysis
data_group = data.groupby(['well', 'strain'])
# List groups
groups = [group for group, data in data_group]

# Initialize data frame to save derivatives
df_gp = pd.DataFrame([])

# Check if the analysis should be done
if (not REPLOT):
    print("Compiling Stan program")

    sm = cmdstanpy.CmdStanModel(
        stan_file=f"{standir}/gp_growth_rate_prior_deriv.stan"
    )
    # Loop through groups
    for group, df in data_group:
        # Check if the group is not a blank
        if group[1] == 'blank':
            continue
        print(group)
        # Build input as required by the Gaussian process function.
        # Define time points were data was measured
        t = df["time_min"].values
        # Define number of time points
        N = len(t)
        # Define OD measurements
        y = df["OD600"].values
        # Define where PPC samples will be taken
        t_predict = t
        # Define number of points in PPC
        N_predict = len(t_predict)

        # Pack parameters in dictionary
        data = {
            "N" : N,  # number of time points
            "t": t,  # time points where data was evaluated
            "y": y,  # data's optical density
            "N_predict": N_predict,  # number of datum in PPC
            "t_predict": t_predict,  # time points where PPC is evaluated
            "alpha_param": [0, 1],  # parameters for alpha prior
            "sigma_param": [0, 1],  # parameters for sigma prior
            "rho_param": [1000, 1000],  # parameters for rho prior
        }

        print(f"Sampling GP for well {group[0]}")
        samples = sm.sample(
            data=data,
            chains=CHAINS,
            iter_sampling=ITER_SAMPLING,
            show_progress=False,
        )
        print("Done!")
        samples = az.from_cmdstanpy(posterior=samples)

        # Extract GP OD data, stacking together chains and draws as a single 
        # dimension
        data_ppc = samples.posterior["y_predict"].stack(
            {"sample": ("chain", "draw")}
        ).transpose("sample", "y_predict_dim_0")
        # Append inferred OD columns
        df = df.assign(
            gp_OD600 = np.median(data_ppc.squeeze().values, axis=0),
            gp_OD600_std = np.std(data_ppc.squeeze().values, axis=0),
        )
        # Extract GP derivative data, stacking together chains and draws as a 
        # single dimension
        data_ppc = samples.posterior["dy_predict"].stack(
            {"sample": ("chain", "draw")}
        ).transpose("sample", "dy_predict_dim_0")
        # Append inferred derivative columns
        df = df.assign(
            gp_growth_rate = np.median(data_ppc.squeeze().values, axis=0),
            gp_growth_rate_std = np.std(data_ppc.squeeze().values, axis=0),
        )
        # Extract GP doubling time data, stacking together chains and draws as a 
        # single dimension
        data_ppc = samples.posterior["doubling_time"].stack(
            {"sample": ("chain", "draw")}
        ).transpose("sample", "doubling_time_dim_0")
        # Append inferred derivative columns
        df = df.assign(
            gp_doubling_time = np.median(data_ppc.squeeze().values, axis=0),
            gp_doubling_time_std = np.std(data_ppc.squeeze().values, axis=0),
        )

        # Append dataframe
        df_gp = pd.concat([df_gp, df], ignore_index=True)

    # Export result
    df_gp.to_csv(f'output/{DATE}_r{RUN_NO}_gp_per_well.csv',
                 index=False)

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
        ax[1].plot(rate_data.time_min, rate_data.gp_growth_rate)
        ax[1].fill_between(rate_data.time_min,
                            rate_data.gp_growth_rate +
                            rate_data.gp_growth_rate_std,
                            rate_data.gp_growth_rate -
                            rate_data.gp_growth_rate_std,
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
    fig, ax = plt.subplots(
        layout_shape[0],
        layout_shape[1],
        figsize=(8, 4),
        sharex=True,
        sharey=True
    )
    # Loop through each well
    for group, df in df_gp_group:
        # Find corresponding row and column of plot
        r, c = [int(x) for x in np.where(layout == group[0])]
        # Set plot axis
        # Plot growth rate
        ax[r][c].plot(df.sort_values('time_min').time_min,
                      df.sort_values('time_min').gp_growth_rate)

    # Set ylim for plot
    ax[0][0].set_ylim([
        df.gp_growth_rate.min() - 0.001,
        df.gp_growth_rate.max() + 0.001
    ])
    # Remove axis from all plots
    ax = ax.ravel() # ravel list of axis

    # Loop through axis
    for a in ax:
        a.get_xaxis().set_visible(False)
        a.get_yaxis().set_visible(False)

    fig.suptitle(f'{DATE}_r{RUN_NO} whole plate growth rates', y=0.95)
    plt.savefig(f'output/growth_rate_summary.png',
                bbox_inches='tight')
