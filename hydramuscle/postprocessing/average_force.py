import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import pandas as pd
import sys, time
from tqdm import tqdm

def load_data(file):
    # Load data
    return pd.read_csv(file).values

def compress_frame(frame, size_x, size_y, to_size_x, to_size_y):
    # Compress the frame by averaging neighboring elements
    mat = np.reshape(frame, (size_x, size_y))
    new_mat = np.zeros((to_size_x, to_size_y))
    win_x = int(size_x/to_size_x)
    win_y = int(size_y/to_size_y)
    
    for i in range(to_size_x):
        for j in range(to_size_y):
            new_mat[i, j] = np.mean(mat[i*win_x:(i+1)*win_x, j*win_y:(j+1)*win_y])
            
    return np.reshape(new_mat, (to_size_x*to_size_y))

if __name__ == "__main__":
    force = load_data('/media/hengji/DATA/Data/Documents/hydramuscle/results/data/force/200x200_100s_cycle.csv')
    new_force = np.zeros((len(force), 400))

    for j in range(len(force)):
        frame = force[j]
        new_force[j,:] = compress_frame(frame, 200, 200, 20, 20)

    df = pd.DataFrame(new_force)
    df.to_csv('/media/hengji/DATA/Data/Documents/hydramuscle/results/data/force/200x200_100s_cycle_averaged.csv', index = False)