# config
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

plt.rcParams.update({'font.size':20})

folder="eRx/eRx Cardio Challenge 4.1/data"
files = [i for i in os.listdir(folder) if i[-10:] != 'output.csv']

BPMs = []
mRSSDs = []
SDNNs = []
pNN50s = []

for file in files:

    df = pd.read_csv(f"{folder}/{file}")
    
    x = df.time
    window_width = 30

    rb_peaks = []
    
    fig, axs = plt.subplots(2,figsize=(10,14))
    axs[0].plot(x, df.Red,'r-')
    axs[1].plot(x,df.Blue,'b-')
    
    axs[0].grid()
    axs[1].grid()
    axs[0].set_xlabel('Time / s')
    axs[1].set_ylabel('RI')
    axs[1].set_xlabel('Time / s')
    axs[0].set_ylabel('RI')
    
    # peak finding algorithm
    for j,colour in enumerate(["Red","Blue"]):
        
        # list to store peak positions
        peaks = []
        
        for i in range(len(df[colour])):
            
            # window range
            start = max(0, i-window_width)
            end = min(len(df[colour]), i+window_width)
            
            window = df[colour][start:end]
            
            # check if current value is the local maximum
            if df[colour][i] == np.max(window):
                peaks.append(i)
                
        # list to contain and later merge the red and blue data
        rb_peaks.append(peaks)
            
        axs[j].plot(x[peaks], df[colour][peaks], 'x', markersize=12, color='black')
    
    plt.show()
    
    # pad the smaller list with NaNs for nanmean to work
    high = max(len(ls) for ls in rb_peaks)    
    rb_peaks_padded = [list(ls) + ([np.nan] * (high - len(ls))) for ls in rb_peaks]
    peaks = np.round(np.nanmean(rb_peaks_padded, axis=0))
    
    # resize BPM to take into account potentially missing data
    BPMs.append(len(peaks)*(4500/len(x)))
    ibi = []
    
    # calculate other metrics
    for i in range(len(peaks)-1):
        ibi.append((df.time[peaks[i+1]] - df.time[peaks[i]])*1000)
    mRSSDs.append(np.sqrt(np.nanmean(np.power(np.diff(ibi), 2))))
    SDNNs.append(np.nanstd(ibi))
    pNN50s.append(len(np.where(np.abs(np.diff(ibi))>50)[0])/len(np.diff(ibi))*100)
    
for i in range(10):
    print(f"File: {files[i]}\n")
    print(f"BPM = {BPMs[i]}")
    print(f"mRSSD = {mRSSDs[i]}")
    print(f"SDNN = {SDNNs[i]}")
    print(f"pNN50 = {pNN50s[i]}\n\n")
