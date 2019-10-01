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
