import numpy as np

"""
Title:
    viz.py
Last update:
    2019-10-30
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

# Generating random mutated sequences
def mut_seq(seq, p_mut, n_mut,
            bp_prob=dict(A=1/4, C=1/4,
                         G=1/4, T=1/4)):
    '''
    Function that generates random mutants from a reference 
    sequence at certain mutation rate.
    
    Parameters
    ----------
    seq : str.
        reference sequence to be mutated.
    p_mut : float. [0, 1]
        probability of a base pair being mutated.
    n_mut : int.
        number of random sequences to generate.
    bp_prob : dict. Default: 1/4 for all 4 bp.
        dictionary containing the probability of a random
        base pair being selected if a position is mutated.
        
    Returns
    -------
    sequences : array-like
        array of mutated sequences.
    '''
    # Extract elements and probabilities from dictionary
    bases = sorted(bp_prob.keys())
    p_bases = [bp_prob[x] for x in bases]  # to order them
    
    # Generate matrix indicating which bp to substitute
    subs_mat = np.random.binomial(1, p_mut, size=[n_mut, len(seq)])
    
    # Initialize array to save mutated sequences by repeating reference seq
    seqs = [seq] * n_mut
    
    # Loop through list elements
    for i, subs in enumerate(subs_mat):
        # Generate substitutions for each position
        sub_bp = np.random.choice(bases, size=sum(subs), p=p_bases)
        # Find positions for substitutions
        idx = np.where(subs)[0]
        # Loop through positions
        for j, pos in enumerate(idx):
            seqs[i] = seqs[i][:pos] + sub_bp[j] + seqs[i][pos+1:]
            
    return seqs
