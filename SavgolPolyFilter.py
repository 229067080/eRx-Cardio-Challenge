# config
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, find_peaks
import pandas as pd
import os

plt.rcParams.update({"font.size":20})

BPMs = []
mRSSDs = []
SDNNs = []
pNN50s = []

# list of .csvs
folder="eRx/eRx Cardio Challenge 4.1/data"

files = [i for i in os.listdir(folder) if i[-10:] != 'output.csv']

###

for file in files:
    df = pd.read_csv(f"{folder}/{file}")
    x = df.time
    fig, axs = plt.subplots(2,2,figsize=(18,18))
    rb_peaks = []
    
    for i,colour in enumerate(['Red','Blue']):
    
        # smooth data
        filtered = savgol_filter(df[colour], window_length=40, polyorder=10)
        
        # remove baseline drift
        cs = np.polyfit(x, filtered, 40)
        bdr_data = filtered - np.polyval(cs, x)
        
        # find peak indices for red and blue signals
        peaks, _ = find_peaks(bdr_data, height = 0, distance = 35)
        rb_peaks.append(peaks)
        
        # plot data
        axs[i][0].plot(x, bdr_data, color=colour,label='Filtered data')
        axs[i][0].plot(x[peaks], bdr_data[peaks], 'x', color='black',markersize=12, label='Peaks')
        axs[i][1].plot(x,df[colour],color = colour)
        
        axs[i][0].grid()
        axs[i][1].grid()
        axs[i][0].set_xlabel('Time / s')
        axs[i][1].set_ylabel('RI')
        axs[i][1].set_xlabel('Time / s')
        axs[i][0].set_ylabel('RI')
        
    plt.show()

    # pad red/blue peaks list so a mean can be calculated
    high = max(len(ls) for ls in rb_peaks)    
    rb_peaks_padded = [list(ls) + ([np.nan] * (high - len(ls))) for ls in rb_peaks]
    peaks = np.round(np.nanmean(rb_peaks_padded, axis=0))
    
    # alter number of peaks by the fraction of missing data
    BPMs.append(len(peaks)*(4500/len(x)))
    ibi = []
    
    # use given lines of code to find metrics
    for i in range(len(peaks)-1):
        ibi.append((df.time[peaks[i+1]] - df.time[peaks[i]])*1000)
    mRSSDs.append(np.sqrt(np.nanmean(np.power(np.diff(ibi), 2))))
    SDNNs.append(np.nanstd(ibi))
    pNN50s.append(len(np.where(np.abs(np.diff(ibi))>50)[0])/len(np.diff(ibi))*100)
    
for i in range(10):
    print(f"File: {files[i]}\n")
    print(f"BPM = {BPMs[i]}\n")
    print(f"mRSSD = {mRSSDs[i]}\n")
    print(f"SDNN = {SDNNs[i]}\n")
    print(f"pNN50 = {pNN50s[i]}\n\n\n")
    
