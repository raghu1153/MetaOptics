import gdstk
import numpy as np
import metaData
import time
import os
from metaData import QuadRadiusData, find_quad_radii # Import the lookup function and data
from metaData import interpolData # Need this for single-wl mode fallback

def circle_polygon(center, radius, num_points=199):
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    points = [(center[0] + radius * np.cos(a), center[1] + radius * np.sin(a)) for a in angles]
    return points

def gdsGen(nD, t='a'):
    # pxSiz is the physical size of one meta-pixel in nanometers (Unitcells per pixel * period)
    pxSiz = nD.pS * 1000 
    
    # Determine if it is a dual-wavelength design based on nD.isDualWl flag
    is_dual_wavelength = nD.isDualWl
    
    if is_dual_wavelength:
        Phi1 = nD.mask_1  # Digitized mask for Wavelength 1
        Phi2 = nD.mask_2  # Digitized mask for Wavelength 2
        bins = nD.bins1   # Bins are the same for both P1 and P2 digitization
        wl1 = nD.wl1
        wl2 = nD.wl2
    else:
        # Single-wavelength mode (Fallback to old logic for single-wl)
        Phi = nD.mask
        bins = nD.bins
        # Ensure interpolData is accessible for single mode
        f1 = metaData.interpolData(nD.pData[0], nD.pData[1])[2] 

    lib = gdstk.Library(unit=1e-9, precision=1e-12)
    main_cell = gdstk.Cell('Metasurface')
    lib.add(main_cell)
    
    # Dictionary to store positions for cell reuse: {radius_or_quad_key: [(x1, y1), (x2, y2), ...]}
    pos_dict = {} 

    row, col = Phi1.shape if is_dual_wavelength else Phi.shape
    
    start_time = time.time()
    ttext = 'Conversion in progress......'
    def _safe_tlab(text, fg=None):
        try:
            if nD.tLab is not None:
                if fg is not None:
                    nD.tLab.config(text=text, fg=fg)
                else:
                    nD.tLab.config(text=text)
                nD.tLab.text = text
        except Exception:
            pass
    _safe_tlab(ttext, fg='blue')

    # Helper functions (Cross and Fin shapes kept for single-wl compatibility)
    def cross_shape(cl):
        w = float(nD.crossW)
        # Safety clamp: cap the arm length so it can't extend past the
        # neighboring unit cell, mirroring the clamp used for Cylinder radii.
        l = min(float(cl), period * 0.98)
        pts = [
            (-w / 2, -l / 2), (w / 2, -l / 2), (w / 2, -w / 2), (l / 2, -w / 2),
            (l / 2, w / 2), (w / 2, w / 2), (w / 2, l / 2), (-w / 2, l / 2),
            (-w / 2, w / 2), (-l / 2, w / 2), (-l / 2, -w / 2), (-w / 2, -w / 2)
        ]
        return pts

    def fin_shape(theta):
        theta_rad = np.radians(theta)
        def ctrans(x, y):
            xt = x * np.cos(theta_rad) + y * np.sin(theta_rad)
            yt = -x * np.sin(theta_rad) + y * np.cos(theta_rad)
            return xt, yt
        # Safety clamp: cap the fin length so a rotated fin can't extend past
        # the neighboring unit cell, mirroring the clamp used for Cylinder radii.
        fl = min(float(nD.fL), period * 0.98)
        fw = float(nD.fW)
        pts = [
            ctrans(-fl / 2, -fw / 2),
            ctrans(fl / 2, -fw / 2),
            ctrans(fl / 2, fw / 2),
            ctrans(-fl / 2, fw / 2)
        ]
        return pts

    # Unit cell spacing variables
    period = nD.period # Periodicity in nm
    uc_per_pix = int(nD.px[0]) # Unit cells per pixel (usually 1)
    
    # --- Define dx and dy based on the true supercell size and lattice type. ---
    
    # In dual-wavelength mode, the effective pitch is 2*period for the supercell.
    effective_pitch_x = 2 * period * uc_per_pix 
    
    # Vertical step for Hexagonal Supercell (should be sqrt(3)/2 * effective_pitch_x)
    effective_pitch_y = np.sqrt(3) / 2 * effective_pitch_x 
    
    if is_dual_wavelength:
        dx = effective_pitch_x
        dy = effective_pitch_y
        is_hexagonal_layout = True
    else:
        # Single-wavelength logic: pitch is 1*period.
        dx = pxSiz 
        is_hexagonal_layout = nD.arrangement.get() == 'Hexagonal'
        
        if is_hexagonal_layout:
            dy = np.sqrt(3) / 2 * pxSiz # Traditional hexagonal spacing
        else: # Square
            dy = pxSiz # Square spacing

    # --- Physical Dimension Setup (Fix for Hexagonal Symmetry) ---
    # Determine the "radius" of the aperture in physical units (nm), not pixels
    # nD.pS is in microns, so we convert everything to nanometers consistent with 'dx'
    
    # m is the smaller dimension in pixels (from original logic)
    m = min(row, col)
    
    # If the user selected a circular aperture size logic in pixels:
    # n is diameter of aperture in pixels
    pixel_diameter = m * 3 if nD.isCircular == 0 else m 
    
    # Calculate the Physical Radius Squared for the check
    # We use 'dx' as the scaling factor. 
    phys_radius_nm = (pixel_diameter / 2.0) * dx
    phys_radius_sq = phys_radius_nm ** 2

    # Calculate Physical Center of the mask
    phys_cx = (col * dx) / 2.0
    phys_cy = (row * dy) / 2.0

    # -------------------------------------------------------------

    for i in range(row):
        k = (float(i) / row) * 100
        try:
            nD.progress.set(k)
            nD.root.update()
        except Exception:
            pass
        for j in range(col):
            
            # 1. Calculate Pixel Center Coordinates (X_pix, Y_pix)
            x_center = j * dx
            y_center = i * dy
            
            # Apply the necessary row shift for the hexagonal arrangement
            if is_hexagonal_layout:
                # Add a shift of dx/2 for every alternating row
                x_center += (i % 2) * (dx / 2)
                
            # 2. Circular Aperture Check (PHYSICAL COORDINATES)
            # This ensures the circle is round even if dx != dy
            if nD.isCircular == 1:
                dist_sq = (x_center - phys_cx) ** 2 + (y_center - phys_cy) ** 2
                if dist_sq >= phys_radius_sq:
                    continue

            # 3. Phase Lookup and Dimension Assignment
            if is_dual_wavelength:
                # Use Quad-Radius Logic
                phase_target1 = bins[Phi1[row - i - 1, j] - 1] 
                phase_target2 = bins[Phi2[row - i - 1, j] - 1]
                
                # r_key is the unique tuple of 4 rounded radii for dictionary lookup
                r_key, current_radii = find_quad_radii(wl1, wl2, phase_target1, phase_target2)
                
                if max(current_radii) <= 0:
                     continue
            else: 
                # Single-Wavelength Logic (Fallback)
                phase = bins[Phi[row - i - 1, j] - 1]
                r_single = np.around(f1(np.clip(phase, np.min(nD.pData[1]), np.max(nD.pData[1]))), 1)
                r_key = r_single
                current_radii = [r_single]
                if r_single <= 0.0:
                    continue

            # 4. Store Position for Cell Reuse (r_key is the key for the subcell geometry)
            # For numpy types, we must convert to standard types if needed, but tuple works for dict keys
            if r_key not in pos_dict:
                pos_dict[r_key] = []
            pos_dict[r_key].append((x_center, y_center))

    # --- GDSII Cell Creation and Instantiation ---
    
    cell_library = {}
    
    for r_key, positions in pos_dict.items():
        # 1. Create Subcell (Geometry Definition)
        
        # Max radius allowed before overlapping with a neighbor cylinder (period / 2.0)
        MAX_SAFE_RADIUS = (period / 2.0) * 0.98  # Use 98% of the max theoretical radius for safety gap
        
        # --- FIX FOR TYPE ERROR (Tuple vs Float) ---
        if isinstance(r_key, (list, tuple, np.ndarray)):
            # It's a list/tuple (Dual Wavelength)
            name_suffix = '_'.join(map(str, r_key))
        else:
            # It's a single number (Single Wavelength)
            name_suffix = str(r_key)
            
        cell_name = 'cell_' + name_suffix
        sub_cell = gdstk.Cell(cell_name)
        
        if is_dual_wavelength and nD.shape == 'Cylinder':
            # Dual-wavelength: Place 4 cylinders inside the supercell based on a hexagonal sub-grid
            r1, r2, r3, r4 = r_key # Use the rounded key for geometry dimensions
            
            # Clip radii to the safe limit to prevent overlap with adjacent cylinders
            r1 = min(r1, MAX_SAFE_RADIUS)
            r2 = min(r2, MAX_SAFE_RADIUS)
            r3 = min(r3, MAX_SAFE_RADIUS)
            r4 = min(r4, MAX_SAFE_RADIUS)
            
            # --- Hexagonal Sub-Grid Offsets ---
            # Center-to-center distance for sub-cylinders must be 'period'.
            sub_pitch_x = period
            sub_pitch_y = np.sqrt(3) / 2 * period
            
            # Sub-cylinders 1 & 2 are in the bottom row of the 2x2 grid
            sub_cell.add(gdstk.Polygon(circle_polygon((-sub_pitch_x/2, -sub_pitch_y/2), radius=r1), layer=1))
            sub_cell.add(gdstk.Polygon(circle_polygon((sub_pitch_x/2, -sub_pitch_y/2), radius=r2), layer=1))
            
            # Sub-cylinders 3 & 4 are in the top row
            sub_cell.add(gdstk.Polygon(circle_polygon((0, sub_pitch_y/2), radius=r3), layer=1))
            sub_cell.add(gdstk.Polygon(circle_polygon((sub_pitch_x, sub_pitch_y/2), radius=r4), layer=1))
            
            
        elif nD.shape == 'Cylinder':
            # Single-wavelength: Place 1 cylinder at (0, 0).
            r_single = r_key 
            # Apply safety margin for single-cylinder mode
            r_single = min(r_single, (period / 2.0) * 0.98)
            sub_cell.add(gdstk.Polygon(circle_polygon((0, 0), radius=r_single, num_points=199), layer=1))
            
        elif nD.shape == 'Cross':
             sub_cell.add(gdstk.Polygon(cross_shape(r_key), layer=1))
        elif nD.shape == 'Fin':
             sub_cell.add(gdstk.Polygon(fin_shape(r_key), layer=1))

        cell_library[r_key] = sub_cell
        lib.add(sub_cell) # Add subcell to the library
        
        # 2. Instantiate Subcell in Main Cell (Reference Creation)
        for origin in positions:
            # Place the reference at the calculated pixel center. 
            main_cell.add(gdstk.Reference(cell_library[r_key], origin=origin))

    # --- File Output and Timing ---

    try:
        lib.write_gds(nD.sLoc + '.gds')
        print("GDS file saved successfully using lib.write_gds.")
    except Exception as e:
        print(f"Error saving GDS file: {e}")
        return

    tot = int(time.time() - start_time)
    m, s = divmod(tot, 60)
    nD.cTime = [m, s]
    
    if os.path.exists(nD.sLoc + '.gds'):
        outSize = os.path.getsize(nD.sLoc + '.gds') / 1024
    else:
        outSize = 0.0
        
    ttext = (
        f"Metasurface GDS Generated. \n\nConversion time: {m} minutes and {s} seconds\n\n"
        f"Output GDS file size: {outSize:.2f} KB"
    )
    _safe_tlab(ttext)
    try:
        nD.root.update()
    except Exception:
        pass
    return tot