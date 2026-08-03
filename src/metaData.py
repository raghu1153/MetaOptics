import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

'''
This file contains FDTD data of different geometries
Structure type a = 
1. height
2. periodicity
3. Varying Radius
.
.
CrossWidth
FinWidth
Length
'''

# --- Single Wavelength Data ---
Data = {1477:('Cylinder-Silicon','a',243,534/2,[695,815,855,975],[0,90,180,270],[0.95,0.9,0.9,0.95]),
        715:('Cylinder-Silicon','a',130,360,[115,120,125,130,135,140,145,150,155],[  0, 23,51,116,238,280,303,327,336],[1,1,1,1,1,1,1,1,1]),
        633:('Cylinder-Silicon','a',280,280,[55,61,65,67,69,71,73,77,83, 91, 99],[0, 39, 82, 110, 139, 167, 191, 229, 264, 290, 315],[1,1,1,1,1,1,1,1,1,1,1]),
        850:('Cylinder-Silicon','a',475,390,[ 58,67.5,74,77.5,84,87.5,92, 98.5,104.5,112 , 118,126],[0,20,47,73,143,192,235,279,301,322,337,355],[1,1,1,1,1,1,1,1,1,1,1,1]),
        1064:('Cylinder-Silicon','a',480,380,[80*.85,90*.85,95*.85,105*.85,115*.85,125*.85,135*.85,140*.85],[0,39,61,113,168,222,277,321],[1,1,1,1,1,1,1,1]),
        410000:('Cross-Silicon', 'a',150000,300000,[187000,201000,208000,212000,217000,225000,237000,267000],[0,40,88,133,181,226,269,315],[1,1,1,1,1,1,1,1],70000),
        8800:('Cross-Silicon', 'a',1850,7250,[1000,1523,2045,2568,3091,3614,4136,4659,5182,5705,6227,6750],[0, 3,10,23,53,127,225,277,302, 315,325,337],[1,1,1,1,1,1,1,1],1000),
        532:('Fin-TiO2', 'a', 600, 325,[0,30,60,90,120,150,180],[0,60,120,180,240,300,360],[1,1,1,1,1,1,1],95,250 ),
        405:('Fin-TiO2', 'a', 600, 200,[0,30,60,90,120,150,180],[0,60,120,180,240,300,360],[1,1,1,1,1,1,1],40,150 ),
}
Data_hex = {
    633:('Cylinder-Silicon','a',690,380,[50,55,60,65,70,75,80,85,90, 95, 100,105,110,115,120,125,130,135,140],[16, 20, 25, 30, 37, 44, 53, 62, 72, 84, 96, 109, 122, 136, 150, 164, 178, 192, 206],[0.96458,0.968,0.97208,0.97685,0.98205,0.98718,0.99156,0.99423,0.99418,0.99087,0.98454,0.97642,0.96869,0.96323,0.96107,0.96168,0.96273,0.96086,0.94883])
}

# --- Dual Wavelength (4-Cylinder) Data ---
# Structure: (R1, R2, R3, R4) tuple : { wavelength_nm: (phase_deg, transmittance) }
QuadRadiusData = {
    (50, 100, 55, 100):      {830: (33.734, 0.9848),  520: (83.885, 0.86461)},
    (105, 70, 105, 105):     {830: (54.568, 0.97378), 520: (110.32, 0.90108)},
    (120, 130, 120, 120):    {830: (89.917, 0.9991),  520: (144.34, 0.91269)},
    (135, 60, 135, 135):     {830: (119.45, 0.96332), 520: (177.02, 0.97682)},
    (145, 115, 145, 145):    {830: (146.69, 0.86621), 520: (202.78, 0.77284)},
    (170, 140, 170, 170):    {830: (184.77, 0.97329), 520: (233.49, 0.85072)},
    (190, 135, 190, 190):    {830: (209.3, 0.89957),  520: (264.76, 0.81976)},
    (190, 80, 190, 190):     {830: (243.67, 0.78004), 520: (296.71, 0.89614)},
    (100, 175, 200, 200):    {830: (269.02, 0.89148), 520: (315.43, 0.8221)},
}

def interpolData(dim,P): 
    Ph = np.array(P)
    x = np.array(dim)
    f1 = interp1d( Ph,x, kind='cubic')
    P = range(int(min(Ph)),int(max(Ph)),5)
    X = []
    for phi in P:
        try:
            X.append(f1(phi))
        except:
            pass
    return [X,P,f1]

# Finds the best (R1, R2, R3, R4) tuple for two target phases (P1, P2)
def find_quad_radii(wl1, wl2, P1_target, P2_target):
    
    # We are removing the hard 5.0 degree limit here to ensure we find a result, 
    # as the GDS output was empty otherwise. We will simply return the BEST match.
    
    min_combined_error = float('inf')
    best_quad = None
    
    # Iterate through all pre-simulated unit cells
    for r_tuple, wl_data in QuadRadiusData.items():
        if wl1 in wl_data and wl2 in wl_data:
            phase1_sim, _ = wl_data[wl1]
            phase2_sim, _ = wl_data[wl2]
            
            # Calculate the phase difference (error) with phase wrap-around (360 -> 0)
            error1 = min(abs(phase1_sim - P1_target), 360 - abs(phase1_sim - P1_target))
            error2 = min(abs(phase2_sim - P2_target), 360 - abs(phase2_sim - P2_target))
            
            # Evaluate based on minimum combined error
            total_error = error1 + error2
            
            if total_error < min_combined_error:
                min_combined_error = total_error
                best_quad = r_tuple
                
    # Use rounded radii for the key to maximize GDS cell reuse
    if best_quad:
        radii_key = tuple(np.around(best_quad, 1))
        # The second return value is the unrounded key
        return radii_key, best_quad 
    
    # Fallback: if no suitable cell is found, return the null cell and a dummy key
    return (0.0, 0.0, 0.0, 0.0), (0, 0, 0, 0)


def plot_quad_wavelength(data, wl1, wl2, nD): # nD added as parameter
    # This function is used to plot the pre-calculated FDTD data for a specific dual-wavelength pair (wl1, wl2)
    fig, ax = plt.subplots(figsize=(5.3, 4.4)) 

    # --- 1. Data Preparation and Sorting ---
    plot_data = []
    for r_tuple, wavelengths in data.items():
        if wl1 in wavelengths and wl2 in wavelengths:
            phase_1, t_1 = wavelengths[wl1]
            phase_2, t_2 = wavelengths[wl2]
            plot_data.append({
                'r_tuple': r_tuple,
                'label': str(r_tuple).replace(' ', ''), # Remove spaces for cleaner label
                'phase1': phase_1, 't1': t_1,
                'phase2': phase_2, 't2': t_2,
            })
            
    # Sort data by the phase of the first wavelength (wl1) to ensure a clean, increasing curve
    plot_data.sort(key=lambda x: x['phase1'])

    x_labels = [d['label'] for d in plot_data]
    x_pos = np.arange(len(x_labels)) 
    
    phases1 = [d['phase1'] for d in plot_data]
    phases2 = [d['phase2'] for d in plot_data]
    trans1 = [d['t1'] for d in plot_data]
    trans2 = [d['t2'] for d in plot_data]
    
    # --- 2. Plotting Lines (Phase) ---
    # Use different marker shapes for better distinction
    ax.plot(x_pos, phases1, color='blue', marker='o', linestyle='-', linewidth=1, 
            label=f'Phase for {wl1} nm', markerfacecolor='white', markersize=5)
    ax.plot(x_pos, phases2, color='red', marker='s', linestyle='-', linewidth=1, 
            label=f'Phase for {wl2} nm', markerfacecolor='white', markersize=5)

    # --- 3. Plotting Scatter (Transmittance) ---
    # Use the scatter points to represent transmittance via size (s=t*500) and color/border.
    # The circle/square markers from the lines will be visually overwritten by these large scatter points.
    
    # Scatter for wl1 (Blue-filled circles)
    ax.scatter(x_pos, phases1, 
               s=[t * 500 for t in trans1], 
               color='blue', 
               alpha=0.6, 
               edgecolors='black',
               linewidth=1.5,
               zorder=3) # Ensure these points are on top
               
    # Scatter for wl2 (Red-filled squares)
    ax.scatter(x_pos, phases2, 
               s=[t * 500 for t in trans2], 
               color='red', 
               alpha=0.6, 
               edgecolors='black',
               linewidth=1.5,
               marker='s', # Use square markers for the second wavelength
               zorder=3)

    # --- 4. Styling and Labels ---
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel('(R1, R2, R3, R4)', fontsize=10) 
    ax.set_ylabel('Phase', fontsize=12)
    # nD access is now safe because it's passed as an argument
    ax.set_title(f'Phase and Transmittance vs. (R1, R2, R3, R4) for Period = {nD.period} nm and Height = {nD.height} nm', fontsize=10) 

    # --- 5. Legend Creation ---
    
    # Phase handles (lines/small markers)
    phase1_handle = plt.Line2D([0], [0], color='blue', marker='o', markersize=5, linewidth=1, label=f'Phase for {wl1} nm')
    phase2_handle = plt.Line2D([0], [0], color='red', marker='s', markersize=5, linewidth=1, label=f'Phase for {wl2} nm')

    # Transmittance handles (scatter size) - Mocking two representative sizes
    t_handle1 = ax.scatter([], [], s=0.95 * 500, color='blue', alpha=0.6, edgecolors='black', linewidth=1.5, label=f'Transmittance for {wl1} nm')
    t_handle2 = ax.scatter([], [], s=0.80 * 500, color='red', alpha=0.6, edgecolors='black', linewidth=1.5, marker='s', label=f'Transmittance for {wl2} nm')
    
    ax.legend(handles=[phase1_handle, t_handle1, phase2_handle, t_handle2], 
              loc='upper left',
              fontsize=8,
              title=f'Legend:')

    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    plt.tight_layout()
    
    return fig
