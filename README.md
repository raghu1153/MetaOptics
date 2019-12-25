# MetaOptics

(C) 2019-2021 Raghu Dharmavarapu. This is free software, released under the CC - BY - NC 4.0 license.

MetaOptics Generates metasurface GDSII layouts for a given phase mask and FDTD dimension vs phase data.

# Setup and requirements

The Python code is for Python 2.7 or later. The following packages must be installed before running the source code.
1. gdsCAD
2. Numpy
3. Scipy
4. Matplotlib
5. PIL
6. xlrd

The source files can be found in the src folder. The main python file of the software is metaOptics.py, which contains all the code for GUI and framework of the software. The metaData.py file contains the FDTD Transmission phase vs varying dimensions for some standard wavelengths. The gdsModule.py file will contain the code that converts the phase profiles in PNG/JPG fromats to metasurface GDSII layouts.
