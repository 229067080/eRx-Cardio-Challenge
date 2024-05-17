# config
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, find_peaks
import pandas as pd
import os
from scipy.optimize import curve_fit

plt.rcParams.update({"font.size":20})

BPMs = []
mRSSDs = []
SDNNs = []
pNN50s = []

def linear(x,m,c):
    return m*x + c

# list of .csvs
folder="eRx/eRx Cardio Challenge 4.1/data"

files = [i for i in os.listdir(folder) if i[-10:] != 'output.csv']

###

for file in files:
    df = pd.read_csv(f"{folder}/{file}")
    x = df.time
    fig, axs = plt.subplots(2,2,figsize=(18,18))
    rgb_peaks = []
    
    for i,colour in enumerate(['Red','Blue']):
    
        # smooth data
        filtered = savgol_filter(df[colour], window_length=40, polyorder=10)
        
        # remove baseline drift
        cs = np.polyfit(x, filtered, 40)
        bdr_data = filtered - np.polyval(cs, x)
        
        # find peak indices for red and blue signals
        peaks, _ = find_peaks(bdr_data, height = 0, distance = 35)
        rgb_peaks.append(peaks)
        
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
    high = max(len(ls) for ls in rgb_peaks)    
    rgb_peaks_padded = [list(ls) + ([np.nan] * (high - len(ls))) for ls in rgb_peaks]
    peaks = np.round(np.nanmean(rgb_peaks_padded, axis=0))
    
    # alter number of peaks by the fraction of missing data
    BPMs.append(len(peaks)*(4500/len(x)))
    
    # use given lines to find metrics
    sorted_p = sorted(peaks)
    ibi = np.diff(df.time[sorted_p])*1000
    mRSSDs.append(np.sqrt(np.nanmean(np.power(np.diff(ibi), 2))))
    SDNNs.append(np.nanstd(ibi))
    pNN50s.append(len(np.where(np.abs(np.diff(ibi))>50)[0])/len(np.diff(ibi))*100)
    
    
    # IBI vs number 
    fig, axs = plt.subplots(2,2,figsize=(18,18))
    axs[0][1].plot(np.arange(len(ibi)),ibi)
    axs[0][1].set_xlabel('Interval number')
    axs[0][1].set_ylabel('Interval / ms')
    axs[0][1].grid()
    
    # Histogram
    axs[1][0].hist(ibi, bins = 20,edgecolor = 'black')
    axs[1][0].set_xlabel('IBI')
    axs[1][0].set_ylabel('Frequency')
    axs[1][0].grid()
    
    # fit a line to peak vs number
    t = peaks * 60/4500
    y = np.arange(0,len(peaks))
    popt, pcov = curve_fit(linear,t,y)
    m, c = popt
    
    # peak vs number
    axs[0][0].plot(t,y,'x',color='black',markersize=12,ls='None',label = 'Peaks')
    axs[0][0].plot(t,linear(t,m,c),'r-',label='Fitted line')
    axs[0][0].set_xlabel("Time / s")
    axs[0][0].set_ylabel ("Peak number")
    axs[0][0].grid()
    
    # fit a line to the correlation plot
    ibix = ibi[:-1]
    ibiy = ibi[1:]
    
    popt, pcov = curve_fit(linear,ibix,ibiy)
    m, c = popt
    
    # correlation plot
    axs[1][1].plot(ibix,ibiy,ls='None',marker = 'x',color='black')
    axs[1][1].plot(ibix,linear(ibix,m,c),'r-')
    axs[1][1].set_xlabel('IBI$_n$ / ms')
    axs[1][1].set_ylabel('IBI$_{n+1}$ / ms')
    axs[1][1].grid()
    plt.show()
    
    # print and save data
with open('output.csv','w') as f:
    f.write('file,hr,mrssd,sdnn,pnn50\n')
    for i in range(10):
        print(f"File: {files[i]}\n")
        print(f"BPM = {BPMs[i]}\n")
        print(f"mRSSD = {mRSSDs[i]}\n")
        print(f"SDNN = {SDNNs[i]}\n")
        print(f"pNN50 = {pNN50s[i]}\n\n\n")
        f.write(f"{files[i]},{BPMs[i]},{mRSSDs[i]},{SDNNs[i]},{pNN50s[i]}\n")
        
