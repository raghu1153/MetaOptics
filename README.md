
# MetaOptics

(C) 2019-2021 Raghu Dharmavarapu. This is free software, released under the CC - BY - NC 4.0 license.

MetaOptics Generates metasurface GDSII layouts for a given phase mask and FDTD dimension vs phase data.

# Setup and requirements

The Python code is for Python 3. The following packages must be installed before running the source code.
1. gdsCAD 
** Note ** The current gdsCAD from PyPI wont support Python 3.0. You must build and install the python 3 compatible gdsCAD from github from the following link. https://github.com/hohlraum/gdsCAD/tree/2and3.   

Steps: a. Clone the repo. 
       b. Do git branch -r to see all branches.  
       c. Checkout to the branch named '2and3'  
       d. Run the following command python setup.py install  
2. Numpy
3. Scipy
4. Matplotlib
5. PIL
6. xlrd
7. tkinter
8. imageio

The source files can be found in the src folder. The main python file of the software is metaOptics.py, which contains all the code for GUI and framework of the software. The metaData.py file contains the FDTD Transmission phase vs varying dimensions for some standard wavelengths. The gdsModule.py file will contain the code that converts the phase profiles in PNG/JPG fromats to metasurface GDSII layouts.

