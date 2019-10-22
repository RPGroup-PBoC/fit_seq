import numpy as np

"""
Title:
    viz.py
Last update:
    2019-10-01
Author(s):
    Manuel Razo-Mejia
Purpose:
    This file compiles all of the relevant functions for sequence manipulation
    related to the fit_seq project.
"""

# Sort-seq related functions
def seq2mat(seq, seq_dict={'A':0,'C':1,'G':2,'T':3}):
    """
    Takes input nucleotide sequence and returns a 4xlen(seq) matrix
    representation. This representation allows for quick mapping of the 
    sequence with an energy matrix since it returns 1's on the rows mapping
    to each corresponding nucleotide as dictaded by seq_dict, and zero 
    everywhere else.
    
    Parameter
    ---------
    seq : str.
        sequence string of A,C,G,Ts
    seq_dict : dict.
        dictionary mapping the nucleotides to rows of the energy matrix.
    Returns
    -------
    mat:
        4xlen(seq) array of ones and zeros
    """
    # Initialize matrix all with zeros
    mat = np.zeros((4,len(seq)),dtype=int)
    
    # Map bp to corresponding number and change
    # value un matrix to 1
    for i, bp in enumerate(seq):
        mat[seq_dict[bp], i] = 1
    return mat

def map_energy(seq, emat, seq_dict={'A':0,'C':1,'G':2,'T':3}):
    '''
    Function to map sequence to energy given a Sort-seq enegy matrix

    Parameters
    ----------
    seq : str.
        sequence string of A,C,G,T's
    emat : 2D-array.
        energy matrix that maps from sequence to energy.
        NOTE: the order of the columns should be the same as the
        order indicated in seq_dict.
    seq_dict : dict.
        dictionary mapping the nucleotides to rows of the energy matrix.
    '''
    # Compute length of energy matrix
    emat_len = emat.shape[1]
    # Convert sequence to matrix
    seq_mat = seq2mat(seq[0:emat_len], seq_dict)
    # Map it to energies
    return np.sum(seq_mat * emat)

def seq_scan(seq, emat):
    '''
    Function that scans a sequence seq with a given energy
    matrix emat and returns the minimum binding energy for all positions.
    
    Parameters
    ----------
    seq : str.
        DNA sequence to be scanned with energy matrix
    emat : 2D-array.
        Energy matrix to map sequences to energies.
        IMPORTANT: This function assumes that each of the rows
        in the energy matrix map to A, C, G, T in that specific order.
        
    Returns
    -------
    min_energy : float.
        Minimum energy
    min_idx : int.
        Index entry of the minimum energy
    '''
    # Map sequence to matrix format
    seq_mat = seq2mat(seq)

    # Infer number of scans
    n_scan = seq_mat.shape[1] - emat_array.shape[1]

    # Initialize array to save scanned energies
    seq_scan = np.zeros(n_scan)

    # Loop through all positions
    for i in np.arange(n_scan):
        # Do elementwise multiplication of matrix section to convert
        # to energy
        seq_scan[i] = np.sum(seq_mat[:, i:i+emat_len] * emat_array)
        
    return min(seq_scan), np.argmin(seq_scan)
