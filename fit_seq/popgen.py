import numpy as np

"""
Title:
    viz.py
Last update:
    2019-10-30
Author(s):
    Manuel Razo-Mejia
Purpose:
    This file compiles all of the relevant functions related to the population
    genetics model associated with the fit-seq project
"""

# Thermodynamic connections to fitness
def en2fit(energy, fo, s, P_Nns=1E-4, beta=1):
    '''
    Function that maps an RNAP binding energy to a fitness value following
    the function:
    fitnes = fo + s(1 / 1 + e^β∆F),
    where ∆F = energy - ln(P_Nns)
    Parameters
    ----------
    energy : array-like.
        RNAP-DNA binding energy
    fo : float.
        basal fitness value in the absence of gene expression
    s : float.
        proportionality between binding probability and fitness.
    P_Nns : float. Default = 1E-4 (fit from Brewster & Jones 2012)
        number of polymerases divided by the number of non-specific
        binding sites.
    beta : float. Default = 1
        inverse temperature times Boltzmann constant (1 / kBT). This 
        sets the units in which the binding energy is given with respect
        to the thermal reservoir.
    
    Returns
    -------
    fitness : aray-like.
        fitness values (growth rates) for each of the energies.
    '''
    # Compute little p
    p = P_Nns * np.exp(-beta * energy)
    # Compute fitness
    return fo + s * p / (1 + p)
