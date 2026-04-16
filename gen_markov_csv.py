"""
Generates Markov Transition Probability Matrices for each basin.
States: 0=Wet, 1=Near-normal, 2=Moderate, 3=Severe/Extreme
"""
import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('outputs')
BASINS = ['caspiansea', 'eastern', 'qaraqom', 'markazi', 'persiangolf', 'urmia']
labels = {0: 'Wet', 1: 'Near-normal', 2: 'Moderate', 3: 'Severe/Extreme'}

def get_state(v):
    if pd.isna(v): return np.nan
    if v >= 0: return 0
    if v >= -1.0: return 1
    if v >= -1.5: return 2
    return 3

dsi = pd.read_csv(OUTPUT_DIR / 'grace_dsi.csv', index_col=0)

for b in BASINS:
    states = dsi[b].apply(get_state)
    # Transitions
    transitions = pd.DataFrame({'from': states.shift(1), 'to': states}).dropna()
    
    # Probability Matrix
    matrix = pd.crosstab(transitions['from'], transitions['to'], normalize='index')
    
    # Ensure all states exist in the matrix (0-3)
    for s in [0, 1, 2, 3]:
        if s not in matrix.index: matrix.loc[s] = 0.0
        if s not in matrix.columns: matrix[s] = 0.0
    matrix = matrix.sort_index().sort_index(axis=1)
    
    # Rename for readability
    matrix.index = [labels[i] for i in matrix.index]
    matrix.columns = [labels[i] for i in matrix.columns]
    
    matrix.to_csv(OUTPUT_DIR / f'markov_transitions_{b}.csv')

print("Markov Transition CSVs generated.")
