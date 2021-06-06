

"""
Title:
    image.py
Last update:
    2021-06-03
Author(s):
    Tom Roeschinger
Purpose:
    This file contains functions to fit a certain growth model
    to data using STAN.
"""
import cmdstanpy
import git
import arviz as az
import numpy as np

# Find home directory for repo
repo = git.Repo("./", search_parent_directories=True)
homedir = repo.working_dir

# Define directory where stan file exists
standir = f"{homedir}/fit_seq/stan_code/"

def logistic_growth_fit(
    t, 
    y, 
    y_0_sigma=0.01, 
    K_sigma=1, 
    sigma_sigma=0.001, 
    log_lambda_mu=-1.5,
    log_lambda_sigma=0.75,
    chains=4, 
    iter_sampling=1000, 
    iter_warmup=1000, 
    t_ppc=[],
    return_samples=False
    ):
    """
    Fit a logistic growth model to a single growth curve.

    Parameters
    ----------
    t : array-like
        Time measurements.
    y : array-like
        Population measurements, e.g., OD or cell count.
    y_0_sigma : float, default 0.01
        Standard Deviation of half normal prior for initial measurement at t=0. Default is chosen for OD measurements.
    K_sigma : float, default 5
        Standard Deviation of half normal prior for carrying capacity. Default is chosen for OD measurements.
    sigma_sigma : float, default 0.01
        Standard Deviation of half normal prior for standard deviation of the normal likelihood.
    log_lambda_mu : float, default -1.5
        Mean of Normal prior on the log of the growth rate.
    sigma_lambda_mu : float, default 0.75
        Standard Deviation of Normal prior on the log of the growth rate.
    chains : int, default 4
        Number chains used in Stan.
    iter_sampling : int, default 1000
        Number if sampling steps in Stan.
    iter_warmup : int, default 1000
        Number of warmup steps in Stan.
    t_ppc : array-like, default []
        Time points for posterior predictive check. If empty, then same time points as measurements are taken.
    return_samples : boolean, default False
        If True, the arviz object is returned.
    
    Returns
    -------
    med_growth_rate : float
        Median of inferred growth rates.
    med_K : float
        Median of inferred carrying capacities.
    samples : arviz object
        Returned if return_samples is given as True.
    
    """

    if t_ppc == []:
        t_ppc = t
    data = {
        "t": t, 
        "y":y, 
        "N":len(t),
        "y_0_sigma": y_0_sigma,
        "K_sigma": K_sigma,
        "sigma_sigma": sigma_sigma,
        "log_lambda_sigma": log_lambda_sigma,
        "log_lambda_mu": log_lambda_mu,
        "N_ppc":len(t_ppc),
        "t_ppc":t_ppc
        }
    # Compile Stan
    sm = cmdstanpy.CmdStanModel(
        stan_file=f"{standir}/logistic_growth_model.stan"
    )

    # Run Sampling
    samples = sm.sample(
            data=data,
            chains=chains,
            iter_warmup=iter_warmup,
            iter_sampling=iter_sampling,
            show_progress=False,
        )

    # Retrieve samples
    samples = az.from_cmdstanpy(posterior=samples)
    
    # Get median parameters
    med_K = np.median(samples.posterior["K"])
    med_growth_rate = np.median(samples.posterior["lambda"])

    if return_samples:
        return med_growth_rate, med_K, samples
    else:
        return med_growth_rate, med_K
