"""This program uses FDTD data of a dielectric resonator and creates a GDSII file for a given metasurface phsae mask"""

__author__ = "Raghu Dharmavarapu"
__copyright__ = "Copyright 2019, Raghu Dharmavarapu"
__credits__ = ["Raghu Dharmavarapu"]
__version__ = 1.2 # Updated version for dual-wavelength support
__maintainer__ = "Raghu Dharmavarapu"
__email__ = "raghu.d@ee.iitm.ac.in"
__status__ = "Stable release"

from tkinter import *
import tkinter.filedialog
from PIL import ImageTk, Image
import numpy as np
import os
import sys
import tkinter.ttk
from tkinter.ttk import Progressbar
import metaData
import gdsModule
import xlrd
import matplotlib.pyplot as plt
from io import BytesIO

plt.rcParams["font.family"] = "Times New Roman"

#############Instructions################
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
        base_path = sys._MEIPASS  # Extract temp folder
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))  # Script's directory

    return os.path.join(base_path, relative_path)



# ── Colour palette ────────────────────────────────────────────────────────────
C_ACCENT   = '#4169E1'   # RoyalBlue1
C_ACCENT2  = '#27408B'   # RoyalBlue3 (hover / active)
C_ACCENT3  = '#27408B'   # RoyalBlue3 (step-bar highlight)
C_BG_TOP   = '#4169E1'   # top frame background
C_BG_MID   = '#FAF6F3'   # middle frame (warm off-white)
C_BG_BOT   = '#F0EAE5'   # bottom frame
C_FG_TITLE = '#27408B'   # heading text on light bg
C_FG_BODY  = '#1a1a2e'   # body text
C_FG_MUTED = '#4a5568'   # muted / caption text
C_WHITE    = '#FFFFFF'
C_STEP_HI  = '#FFFFFF'   # active step label fg
C_STEP_BG  = C_ACCENT    # active step label bg


def render_instructions(parent):
    """Native interactive welcome / instructions panel."""
    for w in parent.winfo_children():
        w.destroy()

    # ── scrollable canvas so nothing ever gets clipped ──────────────────────
    canvas = Canvas(parent, bg=C_BG_MID, highlightthickness=0)
    sb     = Scrollbar(parent, orient=VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side=RIGHT, fill=Y)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    inner = Frame(canvas, bg=C_BG_MID)
    win_id = canvas.create_window((0, 0), window=inner, anchor=NW)

    def _on_configure(e):
        canvas.configure(scrollregion=canvas.bbox('all'))
        canvas.itemconfig(win_id, width=e.width)
    inner.bind('<Configure>', _on_configure)
    canvas.bind('<Configure>', lambda e: canvas.itemconfig(win_id, width=e.width))

    # ── bind mousewheel to this canvas only ─────────────────────────────
    def _on_wheel(e):
        try:
            canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units')
        except TclError:
            pass
    canvas.bind('<MouseWheel>', _on_wheel)
    canvas.bind('<Enter>', lambda e: canvas.focus_set())

    pad = dict(padx=28)

    # Title
    Frame(inner, bg=C_ACCENT, height=4).pack(fill=X)
    Label(inner, text='MetaOptics  3.0', font='Times 22 bold',
          bg=C_BG_MID, fg=C_FG_TITLE).pack(anchor=W, pady=(16, 0), **pad)
    Label(inner, text='Design a metasurface phase mask and export a fabrication-ready GDSII layout.',
          font='Times 12 italic', bg=C_BG_MID, fg=C_FG_MUTED,
          wraplength=650, justify=LEFT).pack(anchor=W, pady=(4, 18), **pad)

    steps = [
        ("1 · Wavelength", [
            "Select an operating wavelength from the built-in list (Visible, Infrared, Terahertz). "
            "Enable Dual-Wavelength mode to design a single metasurface that works at two wavelengths "
            "simultaneously (830 nm + 520 nm) using a Quad-Radius hexagonal layout.",
        ]),
        ("2 · Phase Curve", [
            "Inspect the pre-computed FDTD transmission-phase vs. geometry curve "
            "(pillar radius, cross arm length, fin rotation, etc.).",
            "Optionally upload your own phase data as an Excel file: Column 1 = dimension (nm), "
            "Column 2 = phase (0 – 360°). Include as many data points as possible.",
        ]),
        ("3 · Phase Design", [
            "Import a grayscale phase-mask image, or generate one from the built-in library: "
            "Fresnel Zone Lens (FZL), Axicon, or Spiral Phase Plate (SPP).",
            "Set meta-atoms per pixel (n × n) and phase levels. "
            "Pixel size in your image must equal periodicity × n.",
        ]),
        ("4 · GDSII Export", [
            "Choose a save path and click Generate GDS. "
            "The tool places the correct nanopillar geometry at every lattice site and writes a "
            ".gds file ready for e-beam lithography or photomask fabrication.",
        ]),
    ]

    for title, bullets in steps:
        # section header bar
        hdr = Frame(inner, bg=C_ACCENT, pady=4)
        hdr.pack(fill=X, pady=(10, 0))
        Label(hdr, text=title, font='Times 13 bold',
              bg=C_ACCENT, fg=C_WHITE, padx=28).pack(anchor=W)

        for b in bullets:
            row = Frame(inner, bg=C_BG_MID)
            row.pack(anchor=W, fill=X, padx=28, pady=(4, 0))
            Label(row, text='▸', font='Times 12', bg=C_BG_MID,
                  fg=C_FG_TITLE).pack(side=LEFT, anchor=N, padx=(0, 6))
            Label(row, text=b, font='Times 11', bg=C_BG_MID,
                  fg=C_FG_BODY, wraplength=610,
                  justify=LEFT).pack(side=LEFT, anchor=W)

    # Call-to-action
    Frame(inner, bg=C_ACCENT, height=1).pack(fill=X, pady=(20, 0))
    cta = Frame(inner, bg=C_BG_MID)
    cta.pack(fill=X, pady=(12, 16), **pad)
    Label(cta, text='Click  Next  or the button below to begin.',
          font='Times 12', bg=C_BG_MID, fg=C_FG_MUTED).pack(side=LEFT)
    tkinter.ttk.Button(cta, text='Get Started  →',
                       command=lambda: Next(),
                       width=16, takefocus=False,
                       style='Accent.TButton').pack(side=LEFT, padx=12)


def render_about(parent):
    """Native About panel."""
    for w in parent.winfo_children():
        w.destroy()

    canvas = Canvas(parent, bg=C_BG_MID, highlightthickness=0)
    sb     = Scrollbar(parent, orient=VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side=RIGHT, fill=Y)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    inner = Frame(canvas, bg=C_BG_MID)
    win_id = canvas.create_window((0, 0), window=inner, anchor=NW)

    def _on_configure(e):
        canvas.configure(scrollregion=canvas.bbox('all'))
        canvas.itemconfig(win_id, width=e.width)
    inner.bind('<Configure>', _on_configure)
    canvas.bind('<Configure>', lambda e: canvas.itemconfig(win_id, width=e.width))

    def _on_wheel(e):
        try:
            canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units')
        except TclError:
            pass
    canvas.bind('<MouseWheel>', _on_wheel)
    canvas.bind('<Enter>', lambda e: canvas.focus_set())

    pad = dict(padx=28)

    Frame(inner, bg=C_ACCENT, height=4).pack(fill=X)
    Label(inner, text='About MetaOptics', font='Times 22 bold',
          bg=C_BG_MID, fg=C_FG_TITLE).pack(anchor=W, pady=(16, 0), **pad)

    # ── Software description ─────────────────────────────────────────────────
    hdr = Frame(inner, bg=C_ACCENT, pady=4)
    hdr.pack(fill=X, pady=(14, 0))
    Label(hdr, text='About the Software', font='Times 13 bold',
          bg=C_ACCENT, fg=C_WHITE, padx=28).pack(anchor=W)

    Label(inner, text=(
        "MetaOptics is free, open-source software written in Python. It uses gdstk, SciPy, and NumPy "
        "to convert FDTD phase-vs-dimension simulation data into a GDSII layout file. Each pixel of "
        "a target phase distribution is replaced by an n × n array of dielectric resonator unit cells. "
        "The software also provides a built-in library of standard optical elements "
        "(Fresnel Zone Lens, Axicon, Spiral Phase Plate) and supports both square and hexagonal lattices, "
        "including a dual-wavelength Quad-Radius hexagonal mode."
    ), font='Times 11', bg=C_BG_MID, fg=C_FG_BODY,
       wraplength=660, justify=LEFT).pack(anchor=W, pady=(10, 4), **pad)

    # ── Author 1: Raghu ──────────────────────────────────────────────────────
    hdr2 = Frame(inner, bg=C_ACCENT, pady=4)
    hdr2.pack(fill=X, pady=(18, 0))
    Label(hdr2, text='Original Author  —  v1.1', font='Times 13 bold',
          bg=C_ACCENT, fg=C_WHITE, padx=28).pack(anchor=W)

    Label(inner, text=(
        "Raghu Dharmavarapu — MS in Electrical Engineering, IIT Madras. "
        "Currently pursuing a joint PhD in Nanophotonics at Swinburne University of Technology, "
        "Melbourne, and IIT Madras.\n\n"
        "Built the original MetaOptics tool (v1.1) from the ground up: single-wavelength GDSII "
        "generation, phase-curve visualisation, and the built-in optical element library.\n\n"
        "Email: raghu1153@gmail.com"
    ), font='Times 11', bg=C_BG_MID, fg=C_FG_BODY,
       wraplength=660, justify=LEFT).pack(anchor=W, pady=(10, 4), **pad)

    # ── Author 2: Sarthak ────────────────────────────────────────────────────
    hdr3 = Frame(inner, bg=C_ACCENT, pady=4)
    hdr3.pack(fill=X, pady=(18, 0))
    Label(hdr3, text='Extended by  —  v1.2', font='Times 13 bold',
          bg=C_ACCENT, fg=C_WHITE, padx=28).pack(anchor=W)

    Label(inner, text=(
        "Sarthak Verma — B.Tech in Electrical Engineering, IIT Madras.\n\n"
        "Extended MetaOptics to v1.2 with hexagonal lattice support and dual-wavelength "
        "Quad-Radius GDS generation: four independently-tuned nanopillars per unit cell allow "
        "a single metasurface to impose independent phase profiles at two operating wavelengths "
        "simultaneously."
    ), font='Times 11', bg=C_BG_MID, fg=C_FG_BODY,
       wraplength=660, justify=LEFT).pack(anchor=W, pady=(10, 4), **pad)

    # ── Meta info ─────────────────────────────────────────────────────────────
    Frame(inner, bg=C_ACCENT, height=1).pack(fill=X, pady=(20, 0))
    info_frame = Frame(inner, bg=C_BG_MID)
    info_frame.pack(anchor=W, pady=(12, 0), **pad)
    for lbl, val in [
        ('Current version', '1.2'),
        ('Original version', '1.1  (Raghu Dharmavarapu, 2019)'),
        ('License', 'CC BY-NC'),
    ]:
        row = Frame(info_frame, bg=C_BG_MID)
        row.pack(anchor=W, pady=2)
        Label(row, text=f'{lbl}:', font='Times 11 bold', bg=C_BG_MID,
              fg=C_FG_BODY, width=18, anchor=W).pack(side=LEFT)
        Label(row, text=val, font='Times 11', bg=C_BG_MID,
              fg=C_FG_BODY).pack(side=LEFT)

    Label(inner,
          text='© 2019 Raghu Dharmavarapu · © 2024 Sarthak Verma · All rights reserved.',
          font='Times 10 italic', bg=C_BG_MID, fg=C_FG_MUTED).pack(
              anchor=W, pady=(14, 18), **pad)


root = Tk()

# Set icon dynamically
icon_path = resource_path("logo.ico")
if os.path.exists(icon_path):
    try:
        root.iconbitmap(icon_path)
    except Exception:
        pass

### Removes from running processes after closed ###
def destroyer():
    root.quit()
    root.destroy()
    sys.exit()

root.protocol("WM_DELETE_WINDOW", destroyer)

###Styling###
style = tkinter.ttk.Style(root)
style.theme_use("clam")
style.configure('Small.TButton',  font=("Times 10 bold"),
                background=C_ACCENT, foreground=C_WHITE,
                bordercolor=C_ACCENT3)
style.map('Small.TButton',
          background=[('active', C_ACCENT2), ('pressed', C_ACCENT3)])
style.configure('user.TButton',   font=("Times 12 bold"),
                background='#C05020', foreground=C_WHITE)
style.map('user.TButton',
          background=[('active', C_ACCENT2)])
style.configure('TButton',        foreground=C_WHITE, background=C_ACCENT,
                font=("Times 14 bold"), bordercolor=C_ACCENT3, padding=6)
style.map('TButton',
          background=[('active', C_ACCENT2), ('pressed', C_ACCENT3)])
style.configure('Accent.TButton', foreground=C_WHITE, background=C_ACCENT,
                font=("Times 12 bold"), bordercolor=C_ACCENT3, padding=5)
style.map('Accent.TButton',
          background=[('active', C_ACCENT2)])
style.configure("TProgressbar",   foreground='black', background='#6B8E23')
style.configure('TLabel',         foreground=C_FG_BODY, background=C_BG_TOP,
                font=("Times 13"))
style.configure('TEntry',         fieldbackground='#FFF8F5')

###Starting Window###
root.title('MetaOptics  3.0')
root.geometry("800x680")
root.minsize(740, 580)
root.resizable(1, 1)

fileLoc = StringVar(root)
tFrame = Frame(root, bg=C_BG_TOP, pady=6)
tFrame.pack(fill=X)
tFrame.bind("<1>", lambda event: tFrame.focus_set())
mFrame = Frame(root, bg=C_BG_MID)
mFrame.pack(fill=BOTH, expand=True)
mFrame.bind("<1>", lambda event: mFrame.focus_set())
bFrame = Frame(root, bg=C_BG_BOT, pady=8)
bFrame.pack(fill=X)
bFrame.bind("<1>", lambda event: bFrame.focus_set())

####Opening Layout####
render_instructions(mFrame)

### Global variable declerations ###
global mes
mes = ' '
global r
r = IntVar(root)
r.set(0)
global r2
r2 = IntVar(root)
r2.set(0)
global canvas

# Dual Wavelength variables
global dualVar, wl1Var, wl2Var
dualVar = IntVar(root)
dualVar.set(0) # Default to Single Wavelength
wl1Var = IntVar(root)
wl2Var = IntVar(root)
# The Quad-Radius library only contains pre-simulated cells for this pair;
# these are shown as read-only indicators (not user-editable).
DUAL_WL_1 = 830
DUAL_WL_2 = 520
wl1Var.set(DUAL_WL_1)
wl2Var.set(DUAL_WL_2)

# Single-wavelength radio button layout: (label, value, row, col)
SINGLE_WAVELENGTHS = [
    ("405 nm",   405,    2, 0), ("532 nm",   532,    3, 0),
    ("633 nm",   633,    4, 0), ("715 nm",   715,    5, 0),
    ("850 nm",   850,    6, 0), ("1064 nm",  1064,   2, 1),
    ("8.8 \u03bcm",  8800,   3, 1), ("410 \u03bcm",  410000, 2, 2),
]


def _render_step_bar(active_step):
    """Render the top step indicator with `active_step` (1..4) highlighted."""
    for widget in tFrame.winfo_children():
        widget.destroy()
    tbg = C_BG_TOP
    tfg = '#F5D8CC'
    fgcol = {1: [C_WHITE, tfg, tfg, tfg], 2: [tfg, C_WHITE, tfg, tfg],
             3: [tfg, tfg, C_WHITE, tfg], 4: [tfg, tfg, tfg, C_WHITE]}
    bgcol = {1: [C_ACCENT3, tbg, tbg, tbg], 2: [tbg, C_ACCENT3, tbg, tbg],
             3: [tbg, tbg, C_ACCENT3, tbg], 4: [tbg, tbg, tbg, C_ACCENT3]}
    i = active_step if active_step in fgcol else 1
    for col_idx, txt in enumerate(["\u2460 Wavelength", "\u2461 Phase Curve",
                                    "\u2462 Phase Design", "\u2463 GDSII Export"]):
        _px = 30 if col_idx in (0, 3) else 20
        Label(tFrame, text=txt, font='Times 13 bold',
              fg=fgcol[i][col_idx], bg=bgcol[i][col_idx],
              padx=10, pady=5).grid(row=0, column=col_idx, padx=_px)
    tFrame.columnconfigure(2, weight=1)
    tFrame.columnconfigure(1, weight=1)


def toggleDual():
    """Re-render the wavelength page whenever the Dual-Wavelength checkbox flips."""
    if nD.state == 1:
        nD.state = 0
        Next()

def Previous():
    global mes
    mFrame.grid_propagate(0)
    if nD.state <= 1:
        nD.state = 0
        StartNew()
        return
    else:
        nD.state -= 1
    i = nD.state
    _render_step_bar(i)
    if i == 1:
        nD.state = 0
        Next()
    if i == 2:
        nD.state = 1
        mes = ' '
        Next()
    if i == 3:
        nD.state = 2
        Next()


global um
um = ' '


def Next():
    global r
    global mes
    
    # ------------------ Wavelength and Mode Check ------------------
    if dualVar.get() == 1:
        nD.isDualWl = True
        # Wavelengths are fixed (matching the Quad-Radius library), not editable.
        nD.wl1 = DUAL_WL_1
        nD.wl2 = DUAL_WL_2
        wl1Var.set(DUAL_WL_1)
        wl2Var.set(DUAL_WL_2)
    else:
        nD.isDualWl = False
        if r.get() == 0 and nD.isUserData == 0:
            if nD.state == 1:
                mes = 'Select a wavelength or check Dual Wavelength mode!'
                # Stay on step 1 and re-render with the error message.
                nD.state = 0
                Next()
                return

        nD.wl = int(r.get()) # Only used for single wavelength checks

    # ------------------ Advance State ------------------
    mFrame.grid_propagate(0)
    if nD.state >= 4:
        nD.state = 4
    else:
        nD.state += 1
    i = nD.state

    _render_step_bar(i)

    ###Updating middle frame###
    for widget in mFrame.winfo_children():
        widget.destroy()

    if i == 1:
        # --- State 1: Wavelength Selection ---
        def userData():
            global um
            nD.isUserData = 1
            r.set(0)
            nD.state = 0
            um = ''
            Next()

        Label(mFrame, text='Lattice Arrangement', font='Times 13').grid(row=0, column=0, sticky=W, pady=(10, 5))

        latticeOptions = ["Hexagonal", "Square"]
        # Reuse the persistent StringVar from Design.__init__ instead of
        # creating a new one on every render (which silently reset the choice).
        if nD.arrangement.get() not in latticeOptions:
            nD.arrangement.set("Square")

        latticeMenu = tkinter.ttk.OptionMenu(mFrame, nD.arrangement, nD.arrangement.get(), *latticeOptions)
        latticeMenu.config(width=12)
        latticeMenu.grid(row=0, column=1, pady=(10, 5), padx=20)

        # Dual Wavelength Checkbox
        Checkbutton(mFrame, text="Dual Wavelength \n(Quad-Radius Hex)", variable=dualVar,
                    command=toggleDual, font='Times 13 bold').grid(row=7, column=0, sticky=W, pady=(0, 5))

        if dualVar.get() == 1:
            # Dual-Wavelength mode: fixed, read-only wavelength pair.
            # Hex arrangement is mandatory for Quad-Radius.
            nD.arrangement.set("Hexagonal")
            Label(mFrame,
                  text="Dual-Wavelength mode uses the pre-simulated Quad-Radius library.\n"
                       "Operating wavelengths are fixed (not user-editable):",
                  font='Times 12', fg=C_FG_MUTED, justify=LEFT).grid(
                row=1, column=0, columnspan=4, sticky=W, padx=20, pady=(10, 6))
            Label(mFrame, text=f"Wavelength 1:  {DUAL_WL_1} nm",
                  font='Times 14 bold', fg=C_FG_TITLE).grid(
                row=2, column=0, columnspan=2, sticky=W, padx=30, pady=4)
            Label(mFrame, text=f"Wavelength 2:  {DUAL_WL_2} nm",
                  font='Times 14 bold', fg=C_FG_TITLE).grid(
                row=3, column=0, columnspan=2, sticky=W, padx=30, pady=4)
        else:
            Label(mFrame, text="Visible",   font='Times 15 bold underline').grid(row=1, column=0, padx=30, pady=10)
            Label(mFrame, text="Infrared",  font='Times 15 bold underline').grid(row=1, column=1, padx=30, pady=10)
            Label(mFrame, text="Tera Hertz",font='Times 15 bold underline').grid(row=1, column=2, padx=30, pady=10)

            mFrame.grid_columnconfigure(0, weight=1)
            mFrame.grid_columnconfigure(4, weight=1)

            for text, value, row, col in SINGLE_WAVELENGTHS:
                Radiobutton(mFrame, text=text, variable=r, value=value, font='Times 12').grid(
                    row=row, column=col, sticky=W, padx=20, pady=5
                )

        message = Label(mFrame, text=mes, font='calibri 12 bold', fg='red')
        message.grid(row=9, column=0, columnspan=3, sticky=S + W, pady=(50, 10), padx=20)

        userInput = tkinter.ttk.Button(mFrame, text='Upload my data', command=userData, style='user.TButton')
        userInput.grid(row=10, column=4, sticky=S + E, pady=(40, 10), padx=4)

    elif i == 2:
        # --- State 2: Phase Curve ---
        param = ''
        wl_data = None
        
        if nD.isDualWl:
            # Dual Wavelength (Quad-Radius) Logic
            wl1 = nD.wl1
            wl2 = nD.wl2
            
            # Check if data exists for the two wavelengths
            data_available = all(wl in metaData.QuadRadiusData[list(metaData.QuadRadiusData.keys())[0]] for wl in [wl1, wl2])
            if not data_available:
                nD.state = 0
                mes = f'Quad-Radius data for {wl1}nm and {wl2}nm is not fully available!'
                Next()
                return

            # Set design parameters for Quad-Radius Hex
            nD.shape = 'Cylinder'
            nD.material = 'Silicon'
            nD.height = 830 # Example height
            nD.period = 460 # Example period
            nD.crossW = 'NA'
            
            # Plot the Quad Data
            fig = metaData.plot_quad_wavelength(metaData.QuadRadiusData, wl1, wl2,nD)
            xl = f'Radius Quadruplet (r1,r2,r3,r4)'
            param = f'Period: {nD.period} nm'

        else:
            # Single Wavelength Logic
            nD.wl = int(r.get())
            data_source = metaData.Data_hex if nD.arrangement.get() == "Hexagonal" else metaData.Data
            
            if nD.wl not in data_source:
                nD.state = 0
                mes = f'Single Wavelength data for {nD.wl} nm in {nD.arrangement.get()} is not available!'
                Next()
                return
            
            # (Rest of single wavelength data parsing for single plots remains here)
            wl_data = data_source[nD.wl]
            nD.shape = wl_data[0].split('-')[0]
            nD.material = wl_data[0].split('-')[1]
            Type = wl_data[1]
            nD.type = Type
            nD.height = wl_data[2]
            P = wl_data[5]
            T = wl_data[6]

            if nD.shape == 'Cross':
                nD.crossW = wl_data[7]
                xl = 'Length L (nm)'
            elif nD.shape == 'Cylinder':
                xl = 'Radius r (nm)'
            elif nD.shape == 'Fin':
                nD.fW = wl_data[7]
                nD.crossW = nD.fW
                nD.fL = wl_data[8]
                xl = 'Rotation \u03b8 (degrees)'

            nD.period = wl_data[3] if Type == 'a' else wl_data[4]
            nD.dim = wl_data[4] if Type == 'a' else wl_data[3]
            
            if Type == 'a':
                interData = metaData.interpolData(nD.dim, P)
                param = r'Period: ' + str(nD.period) + ' nm'
            else:
                interData = metaData.interpolData(nD.period, P)
                xl = r'Period $\Lambda$'
                param = r'Radius r: ' + str(nD.dim) + ' nm'
            nD.pData = [nD.dim, P]

            # Single wavelength plot
            interX = interData[0]
            interP = interData[1]
            fig = plt.figure(1, figsize=(5.3, 4.4))
            plt.cla()
            plt.ylabel('Phase (degrees)', size=13)
            plt.xlabel(xl, size=13)
            plt.title('Transmission Phase vs ' + xl, size=13)
            plt.ion()
            plt.plot(interX, interP, 'bo-', markevery=7)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            plt.grid()


        # Plot conversion function
        def fig2img(fig):
            buf = BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            return Image.open(buf)
        
        plt.tight_layout()
        pltIm = fig2img(fig)
        PlotIm = ImageTk.PhotoImage(pltIm)
        plt.close(fig)

        ###Image space###
        Plotlabel = Label(mFrame, image=PlotIm, padx=165)
        Plotlabel.image = PlotIm
        Plotlabel.grid(row=0, column=0, rowspan=7, sticky=W)
        
        Label(mFrame, text="Design parameters", font='Times 14 bold underline').grid(row=0, column=1, sticky=E)
        
        # Parameter display depends on mode
        wl_display = f"Wavelengths: {nD.wl1} / {nD.wl2} nm" if nD.isDualWl else f"Wavelength: {nD.wl} nm"
        
        Label(mFrame, text=wl_display, font='Times 14 ').grid(row=1, column=1, sticky=E)
        Label(mFrame, text="Height: " + str(nD.height) + " nm", font='Times 14 ').grid(row=2, column=1, sticky=E)
        Label(mFrame, text="Width: " + str(nD.crossW) + " nm", font='Times 14 ').grid(row=3, column=1, sticky=E)
        Label(mFrame, text=param, font='Times 14  ').grid(row=4, column=1, sticky=E)
        Label(mFrame, text="Material: " + str(nD.material), font='Times 14  ').grid(row=5, column=1, sticky=E)
        Label(mFrame, text="Shape: " + nD.shape, font='Times 14  ').grid(row=6, column=1, sticky=E)
    
    elif i == 3:
        # --- State 3: Phase Design (Optical Element Selection) ---
        if mes == 'Select a wavelength!':
            mes = ' '
            
        def generate_and_display_phase(design_array, label_widget):
            # Normalizes phase design array (0 to 2pi) to an 8-bit grayscale image (0 to 255)
            if design_array is None: return
            design_array = np.array(design_array)
            digitized = (design_array.astype(np.float32) - np.min(design_array)) * 255 / (np.max(design_array) - np.min(design_array)) + 0
            im = Image.fromarray(digitized.astype('uint8'))
            width, height = im.size
            m = max(width, height)
            if m > 330:
                scale = 330.0 / m
            else:
                scale = 1
            globIm = im.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
            globIm = ImageTk.PhotoImage(globIm)
            label_widget.config(image=globIm, padx=int((420 - width * scale) / 2))
            label_widget.image = globIm
            label_widget.padx = int((420 - width * scale) / 2)
            label_widget.update()
            mFrame.pack_propagate(0)

        def libFunc():
            nonlocal label1
            global mes
            try:
                _libFunc_impl()
            except Exception as _e:
                mes2 = f'Could not generate phase: {type(_e).__name__}: {_e}'
                try:
                    me2.configure(text=mes2, fg='red')
                    me2.text = mes2
                except Exception:
                    pass

        def _libFunc_impl():
            nonlocal label1
            global mes
            nD.px = dv1.get()
            nD.lev = dv2.get()
            
            if r2.get() == 0:
                mes2 = 'Select an optical element!'
                me2.configure(text=mes2)
                me2.text = mes2
                return
            
            # Determine the wavelength(s) for the phase calculation
            wl_calc_1 = nD.wl1 / 1000.0 if nD.isDualWl else nD.wl / 1000.0
            wl_calc_2 = nD.wl2 / 1000.0 if nD.isDualWl else wl_calc_1
            
            # --- FZL Calculation ---
            if r2.get() == 1:
                try:
                    R = fzldia.get() / 2.0
                    F = fzlf.get()
                    if F == 0 or R == 0: raise ValueError
                except (ValueError, TclError):
                    mes2 = 'Enter meaningful parameters for the FZL'
                    me2.configure(text=mes2, fg='red')
                    me2.text = mes2
                    return
                
                nD.fzlF = F
                nD.fzlDia = R * 2.0
                nD.pS = int(nD.px[0]) * (nD.period / 1000.0) # Pixel size in um
                nP = int(R / nD.pS)
                if 2 * nP > 1000:
                    mes2 = f'Number of pixels = {2 * nP}. Chose smaller diameter or more unitcells per pixels.'
                    me2.configure(text=mes2, fg='red')
                    me2.text = mes2
                    nD.design = None
                    nD.dLoc = None
                    return
                
                points = np.linspace(-R, R, 2 * nP)
                x, y = np.meshgrid(points, points)
                x1, y1 = np.ogrid[-nP:nP, -nP:nP]
                
                # FZL phase calculation function
                fzl_func = lambda wL: (2 * np.pi - ((2 * np.pi / wL) * (np.sqrt(x ** 2 + y ** 2 + F ** 2) - F))) % (2 * np.pi)

                if nD.isDualWl:
            # Modified: Single image label for Dual Wavelength (Centered)
                    Label(mFrame, text=f"Phase Mask", font='Times 13 bold').grid(row=0, column=2, columnspan=4, sticky=S, padx=10)
                    
                    label1 = Label(mFrame, padx=165)
                    label1.grid(row=1, column=2, rowspan=7, columnspan=4)
                    label2 = None # Disable the second label

                    nD.design_1 = fzl_func(wl_calc_1)
                    nD.design_2 = fzl_func(wl_calc_2)
                    nD.design_1[(x1 * x1 + y1 * y1) >= nP ** 2] = 0
                    nD.design_2[(x1 * x1 + y1 * y1) >= nP ** 2] = 0
                    generate_and_display_phase(nD.design_1, label1)
                else:
                    # Single image label
                    label1 = Label(mFrame, padx=165)
                    label1.grid(row=0, column=2, rowspan=7, columnspan=4)
                    label2 = None

                    nD.design = fzl_func(wl_calc_1)
                    nD.design[(x1 * x1 + y1 * y1) >= nP ** 2] = 0
                    generate_and_display_phase(nD.design, label1)

                # FZL is a circular optical element by definition; auto-check the
                # circular aperture option so the exported footprint matches the
                # circular region actually used to compute this phase profile.
                checkVar.set(1)

                nD.dLoc = 1
                mes2 = 'FZL phase generated.'
                me2.configure(text=mes2, fg='blue')
                me2.text = mes2
                return
            
            # --- Axicon Calculation (Only adapted for display logic) ---
            elif r2.get() == 2:
                # Axicon logic remains single-wavelength for now, but applies to both designs if in dual mode
                try:
                    R = dia.get() / 2.0
                    cA = np.radians(alpha.get())
                    if R == 0 or cA == 0: raise ValueError
                except (ValueError, TclError):
                    mes2 = 'Enter meaningful parameters for the Axicon'
                    me2.configure(text=mes2, fg='red')
                    me2.text = mes2
                    return
                
                nD.axialpha = alpha.get()
                nD.axidia = R * 2.0
                nD.pS = int(nD.px[0]) * (nD.period / 1000.0)
                nP = int(R / nD.pS)
                
                if 2 * nP > 1000:
                    mes2 = f'Number of pixels = {2 * nP}. Chose smaller diameter or more unitcells per pixels.'
                    me2.configure(text=mes2, fg='red')
                    me2.text = mes2
                    nD.design = None
                    nD.dLoc = None
                    return
                
                points = np.linspace(-R, R, 2 * nP)
                x, y = np.meshgrid(points, points)
                x1, y1 = np.ogrid[-nP:nP, -nP:nP]
                
                axicon_func = lambda wL: ((np.pi * 2 / wL) * (R - (x ** 2 + y ** 2) ** 0.5) * np.tan(cA)) % (2 * np.pi)

                if nD.isDualWl:
                    # In a real dual-wl design, alpha would be different, but here we must apply the same profile to both
                    nD.design_1 = axicon_func(wl_calc_1)
                    nD.design_2 = axicon_func(wl_calc_2)
                    nD.design_1[(x1 * x1 + y1 * y1) >= nP ** 2] = 0
                    nD.design_2[(x1 * x1 + y1 * y1) >= nP ** 2] = 0
                    generate_and_display_phase(nD.design_1, label1)
                    # generate_and_display_phase(nD.design_2, label2)
                else:
                    nD.design = axicon_func(wl_calc_1)
                    nD.design[(x1 * x1 + y1 * y1) >= nP ** 2] = 0
                    generate_and_display_phase(nD.design, label1)

                # Axicon is a circular optical element by definition; auto-check the
                # circular aperture option so the exported footprint matches the
                # circular region actually used to compute this phase profile.
                checkVar.set(1)

                nD.dLoc = 1
                mes2 = 'Axicon phase generated.'
                me2.configure(text=mes2, fg='blue')
                me2.text = mes2
                return
            
            # --- SPP Calculation (Achromatic, but needs to be stored in dual designs if in dual mode) ---
            elif r2.get() == 3:
                try:
                    R = sppdia.get() / 2.0
                    L = sppl.get()
                    if R == 0 or L == 0: raise ValueError
                except (ValueError, TclError):
                    mes2 = 'Enter meaningful parameters for the SPP'
                    me2.configure(text=mes2, fg='red')
                    me2.text = mes2
                    return
                
                nD.sppl = L
                nD.sppdia = R * 2.0
                nD.pS = int(nD.px[0]) * (nD.period / 1000.0)
                nP = int(R / nD.pS)
                
                if 2 * nP > 1000:
                    mes2 = f'Number of pixels = {2 * nP}. Chose smaller diameter.'
                    me2.configure(text=mes2, fg='red')
                    me2.text = mes2
                    nD.design = None
                    nD.dLoc = None
                    return
                
                points = np.linspace(-R, R, 2 * nP)
                x, y = np.meshgrid(points, points)
                x1, y1 = np.ogrid[-nP:nP, -nP:nP]
                
                SPP = L * np.arctan2(y, x)
                spp_design = (SPP + L * np.pi) % (2 * np.pi)
                spp_design[(x1 * x1 + y1 * y1) >= nP ** 2] = 0
                
                if nD.isDualWl:
                    nD.design_1 = spp_design
                    nD.design_2 = spp_design
                    generate_and_display_phase(nD.design_1, label1)
                    # generate_and_display_phase(nD.design_2, label2)
                else:
                    nD.design = spp_design
                    generate_and_display_phase(nD.design, label1)

                # SPP is a circular optical element by definition; auto-check the
                # circular aperture option so the exported footprint matches the
                # circular region actually used to compute this phase profile.
                checkVar.set(1)

                nD.dLoc = 1
                mes2 = 'SPP phase generated.'
                me2.configure(text=mes2, fg='blue')
                me2.text = mes2
                return
            
            return

        def handler():
            global mes
            fileLoc = tkinter.filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(
            ("Supported formats", "*.jpg"), ("Supported formats", "*.png"), ("Supported formats", "*.jpeg")))
            if fileLoc == "":
                nD.state = 2
                Next()
                return
            else:
                im = Image.open(fileLoc).convert('L') # Convert to grayscale
                imArray = np.array(im)
                width, height = im.size
                m = max(width, height)
                
                if m > 2001:
                    nD.state = 2
                    mes = 'Pixels must be < 1000. Image not loaded.'
                    message.config(text=mes)
                    message.text = mes
                    nD.design = None
                    nD.dLoc = None
                    nD.design_1 = None
                    nD.design_2 = None
                    Next()
                    return
                
                # Imported image is stored as the base phase profile (normalized 0 to 2pi in the next step)
                if nD.isDualWl:
                    nD.design_1 = imArray
                    nD.design_2 = imArray # Apply to both designs
                    generate_and_display_phase(nD.design_1, label1)
                    # generate_and_display_phase(nD.design_2, label2)
                else:
                    nD.design = imArray
                    generate_and_display_phase(nD.design, label1)
                        
                nD.dLoc = fileLoc
                mes = ' '
                message.config(text=mes)
                message.text = mes

        # GUI layout for Phase Design
        Label(mFrame, text='Unitcells per pixel', font='Times 13').grid(row=0, column=0, sticky=W, pady=(0, 10))
        global ol1, ol2
        ol1 = ["1x1", "2x2", "3x3", "4x4", "5x5", "6x6"]
        global dv1, dv2
        dv1 = StringVar(root)
        dv1.set(nD.px)
        pm1 = tkinter.ttk.OptionMenu(mFrame, dv1, ol1[int(nD.px[0]) - 1], *ol1)
        pm1.config(width=7)
        pm1.grid(row=0, column=1, pady=(0, 10), padx=40)
        
        Label(mFrame, text='Phase levels', font='Times 13').grid(row=1, column=0, sticky=W, pady=(0, 10))
        ol2 = [2, 4, 8, 9, 16]
        dv2 = IntVar(root)
        dv2.set(nD.lev)
        pm2 = tkinter.ttk.OptionMenu(mFrame, dv2, ol2[ol2.index(nD.lev)], *ol2)
        pm2.config(width=7)
        pm2.grid(row=1, column=1, pady=(0, 10), padx=40)
        
        Label(mFrame, text='Phase min(deg.)', font='Times 13').grid(row=2, column=0, sticky=W, pady=(0, 10))
        Label(mFrame, text='Phase max(deg.)', font='Times 13').grid(row=3, column=0, sticky=W, pady=(0, 10))
        global minPh, maxPh
        minPh = IntVar(root)
        minPh.set(nD.minph)
        maxPh = IntVar(root)
        maxPh.set(nD.maxph)
        tkinter.ttk.Entry(mFrame, textvariable=minPh, width=12, cursor='xterm').grid(row=2, column=1, sticky=W, pady=(0, 10), padx=40)
        tkinter.ttk.Entry(mFrame, textvariable=maxPh, width=12, cursor='xterm').grid(row=3, column=1, sticky=W, pady=(0, 10), padx=40)
        
        global checkVar
        checkVar = IntVar(root)
        checkVar.set(nD.isCircular)
        Checkbutton(mFrame, text="Apply circular aperture", variable=checkVar, font='Times 13').grid(row=4, column=0, columnspan=2, sticky=W, pady=(0, 10), padx=0)
        
        # Dual/Single Phase Mask Display
        if nD.isDualWl:
            # Two image labels for dual wavelength visualization
            # Label(mFrame, text=f"{nD.wl1} nm Phase", font='Times 13 bold').grid(row=0, column=2, sticky=W, padx=10)
            # Label(mFrame, text=f"{nD.wl2} nm Phase", font='Times 13 bold').grid(row=0, column=4, sticky=W, padx=10)
            
            label1 = Label(mFrame, padx=165)
            label1.grid(row=0, column=2, rowspan=7, columnspan=4)
            label2 = None
            # label2 = Label(mFrame, padx=80)
            # label2.grid(row=1, column=4, rowspan=6, columnspan=2, padx=10)
        else:
            # Single image label
            label1 = Label(mFrame, padx=165)
            label1.grid(row=0, column=2, rowspan=7, columnspan=4)
            label2 = None 
        
        message = Label(mFrame, text=mes, font='calibri 12 bold', fg='red')
        message.grid(row=5, column=0, columnspan=2, sticky=W, pady=(75, 5))

        importPhase = tkinter.ttk.Button(mFrame, text='Import Phase', command=handler, width=14, takefocus=False)
        importPhase.grid(row=6, column=0, columnspan=2, padx=(15, 0), sticky=W)

        # Library Functions (FZL, Axicon, SPP)
        Label(mFrame,
              text='-------------------------------------------Library Functions-------------------------------------------',
              fg='blue', font='Times 14  italic').grid(row=7, column=0, columnspan=6, pady=(15, 0))
        R1 = Radiobutton(mFrame, text="FZL", variable=r2, value=1, font='Times 14  underline bold ')
        R1.grid(row=8, column=0, pady=(0, 0), columnspan=2)
        R2 = Radiobutton(mFrame, text="Axicon", variable=r2, value=2, font='Times 14  underline bold ')
        R2.grid(row=8, column=2, pady=(0, 0), columnspan=2)
        R3 = Radiobutton(mFrame, text="SPP", variable=r2, value=3, font='Times 14  underline bold')
        R3.grid(row=8, column=4, pady=(0, 0), columnspan=2)

        # Parameter entries for FZL, Axicon, SPP (Code for entry fields omitted for brevity, assumed correct)
        # FZL
        global fzlf, fzldia
        fzlf = IntVar(root); fzlf.set(nD.fzlF)
        fzldia = DoubleVar(root); fzldia.set(nD.fzlDia)
        Label(mFrame, text='Focal length(um): ', font='Times 13').grid(row=9, column=0, pady=0, padx=0, sticky=W)
        tkinter.ttk.Entry(mFrame, textvariable=fzlf, width=8, cursor='xterm').grid(row=9, column=1, pady=10)
        Label(mFrame, text='Diameter (um):', font='Times 13').grid(row=10, column=0, pady=0, padx=0, sticky=W)
        tkinter.ttk.Entry(mFrame, textvariable=fzldia, width=8, cursor='xterm').grid(row=10, column=1, pady=0)
        
        # Axicon
        global alpha, dia
        alpha = DoubleVar(root); alpha.set(nD.axialpha)
        dia = DoubleVar(root); dia.set(nD.axidia)
        Label(mFrame, text='Cone angle: ', font='Times 13').grid(row=9, column=2, pady=0, sticky=W)
        tkinter.ttk.Entry(mFrame, textvariable=alpha, width=8, cursor='xterm').grid(row=9, column=3, pady=0, padx=(20, 0))
        Label(mFrame, text='Diameter (um):', font='Times 13').grid(row=10, column=2, pady=0, sticky=W)
        tkinter.ttk.Entry(mFrame, textvariable=dia, width=8, cursor='xterm').grid(row=10, column=3, pady=0, padx=(20, 0))
        
        # SPP
        global sppl, sppdia
        sppl = IntVar(root); sppl.set(nD.sppl)
        sppdia = DoubleVar(root); sppdia.set(nD.sppdia)
        Label(mFrame, text='Charge: ', font='Times 13').grid(row=9, column=4, pady=0, padx=(20, 20), sticky=W)
        tkinter.ttk.Entry(mFrame, textvariable=sppl, width=8, cursor='xterm').grid(row=9, column=5, pady=0, padx=(20, 20))
        Label(mFrame, text='Diameter (um):', font='Times 13').grid(row=10, column=4, pady=0, padx=(20, 20), sticky=W)
        tkinter.ttk.Entry(mFrame, textvariable=sppdia, width=8, cursor='xterm').grid(row=10, column=5, pady=0, padx=(20, 20))

        mes2 = ' '
        me2 = Label(mFrame, text=mes2, font='calibri 12 bold', fg='red')
        me2.grid(row=11, column=0, columnspan=5, sticky=W)
        libGen = tkinter.ttk.Button(mFrame, text='Generate', command=libFunc, width=10, takefocus=False, style='Small.TButton')
        libGen.grid(row=11, column=5, sticky=E, pady=(2, 0), padx=(0, 20))
        
        # Re-display design if generated previously
        if nD.dLoc != None:
            if nD.isDualWl:
                generate_and_display_phase(nD.design_1, label1)
                # generate_and_display_phase(nD.design_2, label2)
            else:
                 generate_and_display_phase(nD.design, label1)


    elif i == 4:
        # --- State 4: GDSII Design ---
        nD.px =  dv1.get()
        nD.lev = dv2.get()
        nD.isDualWl = dualVar.get()
        
        try:
            if minPh.get() == maxPh.get() or maxPh.get() > 360 or minPh.get() < 0: 
                nD.state = 2
                nD.maxph = 360
                nD.minph = 0
                mes = 'Invalid phase values'
                Next()
                return
        except:
            nD.state = 2
            nD.maxph = 360 
            nD.minph = 0
            mes = 'Invalid phase values'
            Next()
        else:
            nD.minph = minPh.get()
            nD.maxph = maxPh.get()
            nD.isCircular = checkVar.get()
            
            if nD.dLoc == None:
                nD.state = 2
                mes = 'Import Phase design!'
                Next()
                return
            
            mes = ''
            bins = []
            phRange = nD.maxph - nD.minph
            interval = phRange / float(nD.lev)
            for k in range(nD.lev):
                bins.append(nD.minph + k * interval)
            
            # Phase Digitization
            if nD.isDualWl:
                # Digitization is done separately for both phase designs
                nD.bins1 = bins
                nD.bins2 = bins
                design_1 = (nD.design_1.astype(np.float32) - np.min(nD.design_1)) * phRange / (np.max(nD.design_1) - np.min(nD.design_1))
                design_2 = (nD.design_2.astype(np.float32) - np.min(nD.design_2)) * phRange / (np.max(nD.design_2) - np.min(nD.design_2))
                
                nD.mask_1 = np.digitize(design_1, nD.bins1)
                nD.mask_2 = np.digitize(design_2, nD.bins2)
                
                # Use mask 1 for visualization
                Phi_vis = nD.mask_1
                pixels = nD.mask_1.shape
                wl_str = f'Wavelengths: {nD.wl1} / {nD.wl2} nm'
                nD.pS = int(nD.px[0]) * (nD.period / 1000.0) # Pixel size in um

            else:
                # Single Wavelength Mode
                nD.bins = bins
                design = (nD.design.astype(np.float32) - np.min(nD.design)) * phRange / (np.max(nD.design) - np.min(nD.design))
                Phi_vis = np.digitize(design, nD.bins)
                nD.mask = Phi_vis
                pixels = nD.design.shape
                wl_str = 'Wavelength: ' + str(nD.wl) + ' nm'
                nD.pS = int(nD.px[0]) * (nD.period / 1000.0) # Pixel size in um

            # Visualization
            digitized = (Phi_vis - np.min(Phi_vis)) * 255 / (np.max(Phi_vis) - np.min(Phi_vis)) + 0
            im = Image.fromarray(digitized.astype('uint8'))
            width, height = im.size
            m = max(width, height)
            if m > 330:
                scale = 330.0 / m
            else:
                scale = 1
            globIm = im.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
            globIm = ImageTk.PhotoImage(globIm)
            label = Label(mFrame, image=globIm)
            label.image = globIm
            label.grid(padx=int((420 - width * scale) / 2), row=0, column=0, rowspan=2)
            mFrame.pack_propagate(0)

            # Info Display
            progressVar = DoubleVar(root)
            progress = Progressbar(mFrame, orient=HORIZONTAL, variable=progressVar, maximum=100, length=290)
            progress.grid(padx=20, pady=10, row=2, column=0)
            nD.progress = progressVar
            
            Label(mFrame, text='Design parameters', font='Times 13 bold underline').grid(row=0, column=1, sticky=W)
            
            # Display factor of 2 for period only in the dual-wavelength hexagonal case where the pixel size is 2xperiod
            period_factor = 1 
            if nD.isDualWl and nD.arrangement.get() == "Hexagonal":
                 period_factor = 2 # The pixel size is 2x the base period for the 4-cylinder layout (2x2 supercell)

            Info = Label(mFrame, text=wl_str + '\n\n'
                                        'No of matrices per unitcell: ' + str(nD.px) + '\n\n' +
                                        'Centre to Centre Nano-pillar distance: ' + str(nD.period) + ' nm\n\n' +
                                        'Phase levels: ' + str(nD.lev) + '\n\n' +
                                        'Pixel size (Unitcells per pixel X period): ' + str(
                    int(nD.px[0]) * period_factor * nD.period) + ' nm\n\n' +
                                        'Pixels in Phase mask: ' + str(pixels[0]) + ' X ' + str(
                    pixels[1]) + '\n\n' +
                                        'Phase mask diameter: ' + str(
                    min(pixels[0], pixels[1]) * int(nD.px[0]) * period_factor * nD.period / 1000) + ' um\n\n' +
                                        'Circular aperture applied: ' + str(nD.isCircular == 1) + '\n\n',
                             font='Times 12', anchor=W, justify=LEFT)
            Info.grid(row=1, column=1, sticky=W + N)

            gds = tkinter.ttk.Button(mFrame, text='Generate GDS', command=gdsGen, width=14, takefocus=False)
            gds.grid(sticky=W, pady=10, row=2, column=1)
            Label(mFrame, text='Design parameters', font='Times 13 bold underline').grid(row=0, column=1, sticky=W)

            TimeInfo = Label(mFrame, text='', justify=LEFT, anchor=W, font='Times 12')
            TimeInfo.grid(row=3, column=1, sticky=W)
            nD.tLab = TimeInfo


def gdsGen():
    nD.sLoc = tkinter.filedialog.asksaveasfilename()
    if nD.sLoc == "":
        nD.state = 3
        Next()
    else:
        gdsModule.gdsGen(nD)
    return


def StartNew():
    for widget in mFrame.winfo_children():
        widget.destroy()
    _render_step_bar(1)
    render_instructions(mFrame)
    nD.state = 0
    nD.dLoc = None
    nD.design = None
    nD.design_1 = None
    nD.design_2 = None
    nD.mask = None
    nD.mask_1 = None
    nD.mask_2 = None
    nD.bins = None
    nD.bins1 = None
    nD.bins2 = None
    nD.pData = None
    nD.px = '1x1'
    nD.lev = 2
    nD.minph = 0
    nD.maxph = 360
    global mes
    mes = ' '
    nD.period = 0
    nD.wl = 0
    r.set(0)
    r2.set(0)
    nD.isUserData = 0
    nD.height = 0
    nD.shape = 'Cylinder'
    nD.crossW = 0
    nD.fW = 0
    # Library reset#
    nD.axialpha = 0.0
    nD.axidia = 0.0
    nD.sppl = 1
    nD.sppdia = 0.0
    nD.fzlF = 0.0
    nD.fzlDia = 0.0
    nD.isCircular = 0
    nD.fL = 0
    nD.material = None
    nD.tLab = None
    global dualVar
    dualVar.set(0)
    nD.isDualWl = False
    nD.wl1 = 0
    nD.wl2 = 0
    nD.arrangement.set("Square")
    # Reset widget-bound Tk variables so previously entered values don't
    # silently persist across a Start New (see release notes B4).
    wl1Var.set(DUAL_WL_1)
    wl2Var.set(DUAL_WL_2)
    for _v_name in ('minPh', 'maxPh', 'checkVar', 'fzlf', 'fzldia',
                    'alpha', 'dia', 'sppl', 'sppdia', 'dv1', 'dv2'):
        _v = globals().get(_v_name)
        if _v is None:
            continue
        try:
            if _v_name == 'minPh':      _v.set(0)
            elif _v_name == 'maxPh':    _v.set(360)
            elif _v_name == 'checkVar': _v.set(0)
            elif _v_name == 'fzlf':     _v.set(0)
            elif _v_name == 'fzldia':   _v.set(0.0)
            elif _v_name == 'alpha':    _v.set(0.0)
            elif _v_name == 'dia':      _v.set(0.0)
            elif _v_name == 'sppl':     _v.set(1)
            elif _v_name == 'sppdia':   _v.set(0.0)
            elif _v_name == 'dv1':      _v.set('1x1')
            elif _v_name == 'dv2':      _v.set(2)
        except (TclError, Exception):
            pass


def about():
    for widget in mFrame.winfo_children():
        widget.destroy()
    # (Top frame update logic omitted for brevity)
    render_about(mFrame)


class Design():
    def __init__(self):
        self.isUserData = 0
        self.wl = 0
        self.wl1 = 0 # Dual wavelength 1
        self.wl2 = 0 # Dual wavelength 2
        self.isDualWl = False # Flag for dual wavelength mode
        self.pData = None
        self.design = None
        self.design_1 = None # Phase mask 1
        self.design_2 = None # Phase mask 2
        self.state = 0
        self.sLoc = None
        self.dLoc = None
        self.shape = "Cylinder"
        self.period = 0
        self.px = '1x1'
        self.lev = 2
        self.minph = 0
        self.maxph = 360 
        self.dim = 0
        self.height = 0
        self.bins = None
        self.bins1 = None # Bins for phase mask 1
        self.bins2 = None # Bins for phase mask 2
        self.type = 'a'
        self.progress = 0
        self.root = root
        self.sLoc = None
        self.pS = 0
        self.mask = None
        self.mask_1 = None # Digitized mask 1
        self.mask_2 = None # Digitized mask 2
        ### Library design parameters ###
        self.axialpha = 0.0
        self.axidia = 0.0
        self.sppl = 1
        self.sppdia = 0.0
        self.fzlF = 0.0
        self.fzlDia = 0.0
        self.isCircular = 0
        self.cTime = [0, 0]  # Conversion time
        self.tLab = None
        self.crossW = 0
        self.fW = 0
        self.fL = 0
        self.material = None
        self.arrangement = StringVar(root)
        self.arrangement.set("Square")


#######Main Layout and Buttons#####
nD = Design()

_step_lbl_kw = dict(font='Times 13 bold', background=C_BG_TOP,
                    foreground='#F5D8CC', padx=10, pady=5)
tl1 = Label(tFrame, text="① Wavelength", **_step_lbl_kw)
tl1.grid(row=0, column=0, padx=30)
tl1 = Label(tFrame, text="② Phase Curve", **_step_lbl_kw)
tl1.grid(row=0, column=1, padx=20)
tl1 = Label(tFrame, text="③ Phase Design", **_step_lbl_kw)
tl1.grid(row=0, column=2, padx=20)
tl1 = Label(tFrame, text="④ GDSII Export", **_step_lbl_kw)
tl1.grid(row=0, column=3, padx=30)
tFrame.columnconfigure(2, weight=1)
tFrame.columnconfigure(1, weight=1)

bFrame.columnconfigure(0, weight=1)
bFrame.columnconfigure(1, weight=1)
bFrame.columnconfigure(2, weight=1)
bFrame.columnconfigure(3, weight=1)
bFrame.columnconfigure(4, weight=1)

tkinter.ttk.Button(bFrame, text='About',     command=about,    width=12, takefocus=False).grid(row=0, column=0, padx=10, pady=4)
tkinter.ttk.Button(bFrame, text='Start New', command=StartNew, width=12, takefocus=False).grid(row=0, column=1, padx=10, pady=4)
tkinter.ttk.Button(bFrame, text='◀  Previous', command=Previous, width=14, takefocus=False).grid(row=0, column=3, padx=10, pady=4)
tkinter.ttk.Button(bFrame, text='Next  ▶',   command=Next,    width=14, takefocus=False).grid(row=0, column=4, padx=10, pady=4)

if __name__ == '__main__':
    root.mainloop()
