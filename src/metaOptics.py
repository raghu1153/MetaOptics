"""This program uses FDTD data of a dielectric resonator and creates a GDSII file for a given metasurface phsae mask"""

__author__ = "Raghu Dharmavarapu"
__copyright__ = "Copyright 2019, Raghu Dharmavarapu"
__credits__ = ["Raghu Dharmavarapu"]
__version__ = 1.1
__maintainer__ = "Raghu Dharmavarapu"
__email__ = "raghu.d@ee.iitm.ac.in"
__status__ = "Stable release"


from tkinter import *
import tkinter.filedialog
import PIL
from PIL import ImageTk, Image
import numpy as np
from scipy import misc
import imageio
import os
from tkinter.ttk import *
import metaData
import gdsModule
import xlrd
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"

#############Instructions################
'''
Change the base_path to the location where you have this .py file and logo2.ico file
'''

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS,
        # and places our data files in a folder relative to that temp
        # folder named as specified in the datas tuple in the spec file
        base_path = os.path.join(sys._MEIPASS, 'data')
    except Exception:
        # sys._MEIPASS is not defined, so use the original path
        base_path = '/home/raghu/pythonProjects/MetaOptics/src/' #Change this to current working directory where the logo.ico file exists

    return os.path.join(base_path, relative_path)

root = Tk()    

### Removes from running processes after closed ###
def destroyer():
    root.quit()
    root.destroy()
    sys.exit()

root.protocol("WM_DELETE_WINDOW", destroyer)


###Styling###
style = Style(root)
style.theme_use("clam")
style.configure('Small.TButton', font = ("Times 10 bold"))
style.configure('user.TButton', font = ("Times 12 bold"),background = 'SkyBlue2')
style.configure('TButton', fg='white',background ='RoyalBlue1',activefg = 'black', font = ("Times 15 bold"),bordercolor = 'blue')
style.configure("TProgressbar", foreground= 'black', background='forest green')
style.configure('TLabel', foreground='black',background = 'RoyalBlue1',font = ("Times 13"))


###Starting Window###
root.title('MetaOptics')
root.geometry("736x610") #You want the size of the app to be 620x400
if "nt" == os.name:
    root.wm_iconbitmap(resource_path(logo.ico))
#else:
    #ilogoImg = PhotoImage(file=logo.ico)
    #root.iconphoto('wm', 'iconphoto', root._w, img)
#root.iconbitmap(resource_path('logo.ico'))
root.resizable(0, 0) #Don't allow resizing in the x or y direction
fileLoc = StringVar(root)
tFrame = tkinter.Frame(root, borderwidth = 3, bg = 'RoyalBlue1') 
tFrame.pack( fill = X)
tFrame.bind("<1>", lambda event: tFrame.focus_set())
mFrame = tkinter.Frame(root, borderwidth = 3,bg = 'gray95') 
mFrame.pack( fill = X,expand=True)
mFrame.bind("<1>", lambda event: mFrame.focus_set())
bFrame = tkinter.Frame(root,borderwidth = 3,bg = 'gray88', pady = 10)
bFrame.pack(fill = X,expand=True)
bFrame.bind("<1>", lambda event: bFrame.focus_set())

####Opening Layout####  
rm = Image.open(resource_path('Instructions.png'))
width, height = rm.size
m = max(width,height)
if m > 690:
    scale = 690.0/m
    rm = rm.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
rm = ImageTk.PhotoImage(rm)
redLabel = tkinter.Label(mFrame,image = rm)
redLabel.image = rm
redLabel.pack(pady = 10)


### Global variable declerations ###
global mes
mes = ' '
global r 
r = IntVar(root)  
r.set(0) 
global  r2
r2 = IntVar(root)  
r2.set(0)    
global canvas


def Previous():
    global mes
    global r  
    mFrame.grid_propagate(0)
    if nD.state<=1:
        nD.state = 0
        StartNew()
        return
    else:
        nD.state -= 1
    i = nD.state 
    ###Updating Top Frame####
    tbg = 'RoyalBlue1'
    tfg = 'black'
    fgcol = {1:['white',tfg,tfg,tfg],2:[tfg,'white',tfg,tfg],3:[tfg,tfg,'white',tfg],4:[tfg,tfg,tfg,'white']}
    bgcol = {1:['RoyalBlue3',tbg,tbg,tbg],2:[tbg,'RoyalBlue3',tbg,tbg],3:[tbg,tbg,'RoyalBlue3',tbg],4:[tbg,tbg,tbg,'RoyalBlue3']}
    tl1 = tkinter.Label(tFrame, text="Wavelength",borderwidth=2, font = 'Times 13 bold', fg=fgcol[i][0],bg = bgcol[i][0], padx = 5,pady = 5)
    tl1.grid(row = 0, column = 0, padx = 50)
    tl1 = tkinter.Label(tFrame, text="Phase curve", borderwidth=2, font = 'Times 13 bold', fg=fgcol[i][1],bg = bgcol[i][1],padx = 5,pady = 5)
    tl1.grid(row = 0, column = 1, padx = 20)
    tl1 = tkinter.Label(tFrame, text="Phase Design", borderwidth=2, font = 'Times 13 bold', fg=fgcol[i][2],bg = bgcol[i][2],padx = 5,pady = 5)
    tl1.grid(row = 0, column = 2, padx = 20)
    tl1 = tkinter.Label(tFrame, text="GDSII Design",borderwidth=2, font = 'Times 13 bold', fg=fgcol[i][3],bg = bgcol[i][3],padx = 5,pady = 5)
    tl1.grid(row = 0, column = 3, padx = 50)
    tFrame.columnconfigure(2, weight=1)
    tFrame.columnconfigure(1, weight=1)
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
    global canvas
    global mes
    global um
    mFrame.grid_propagate(0)
    if nD.state>=4:
        nD.state =4
    else:
        nD.state += 1
    i = nD.state 
    for widget in tFrame.winfo_children():
        widget.destroy()
    ###Updating Top Frame####
    tbg = 'RoyalBlue1'
    tfg = 'black'
    fgcol = {1:['white',tfg,tfg,tfg],2:[tfg,'white',tfg,tfg],3:[tfg,tfg,'white',tfg],4:[tfg,tfg,tfg,'white']}
    bgcol = {1:['RoyalBlue3',tbg,tbg,tbg],2:[tbg,'RoyalBlue3',tbg,tbg],3:[tbg,tbg,'RoyalBlue3',tbg],4:[tbg,tbg,tbg,'RoyalBlue3']}
    tl1 = tkinter.Label(tFrame, text="Wavelength",borderwidth=2, font = 'Times 13 bold', fg=fgcol[i][0],bg = bgcol[i][0], padx = 5,pady = 5)
    tl1.grid(row = 0, column = 0, padx = 50)
    tl1 = tkinter.Label(tFrame, text="Phase curve", borderwidth=2, font = 'Times 13 bold', fg=fgcol[i][1],bg = bgcol[i][1],  padx = 5,pady = 5)
    tl1.grid(row = 0, column = 1, padx = 20)
    tl1 = tkinter.Label(tFrame, text="Phase Design", borderwidth=2, font = 'Times 13 bold', fg=fgcol[i][2],bg = bgcol[i][2], padx = 5,pady = 5)
    tl1.grid(row = 0, column = 2, padx = 20)
    tl1 = tkinter.Label(tFrame, text="GDSII Design",borderwidth=2, font = 'Times 13 bold', fg=fgcol[i][3],bg = bgcol[i][3], padx = 5,pady = 5)
    tl1.grid(row = 0, column = 3, padx = 50)
    tFrame.columnconfigure(2, weight=1)
    tFrame.columnconfigure(1, weight=1)
    
    ###Updating middle frame###
    for widget in mFrame.winfo_children():
        widget.destroy()
    if i == 1:
        def userData():
            global um
            nD.isUserData = 1
            r.set(0)
            nD.state = 0
            um = ''
            Next()
        if nD.isUserData == 0:    
            tkinter.Label(mFrame,text = "Visible", font = 'Times 15 bold underline').grid(row = 0, column = 1, padx =40)
            tkinter.Label(mFrame,text = "Infrared", font = 'Times 15 bold underline').grid(row = 0, column = 2, padx =40)
            tkinter.Label(mFrame,text = "Tera Hertz", font = 'Times 15 bold underline').grid(row = 0, column = 3, padx =40)
            mFrame.grid_columnconfigure(0, weight=1)
            mFrame.grid_columnconfigure(4, weight=1)
            R11 = tkinter.Radiobutton(mFrame, text="405 nm", variable=r, value=405,font = 'Times 12 ')
            R11.grid(row = 1, column = 1, sticky = W,padx = 40, pady = 5)
            R21 = tkinter.Radiobutton(mFrame, text="532 nm", variable=r, value=532,font = 'Times 12 ')
            R21.grid(row = 2, column = 1, sticky = W,padx =40, pady = 10)
            R31 = tkinter.Radiobutton(mFrame, text="633 nm", variable=r, value=633,font = 'Times 12 ')
            R31.grid(row = 3, column = 1, sticky = W,padx = 40, pady = 5)
            R41 = tkinter.Radiobutton(mFrame, text="715 nm", variable=r, value=715,font = 'Times 12 ')
            R41.grid(row = 4, column = 1, sticky = W,padx = 40, pady = 5)
            R51 = tkinter.Radiobutton(mFrame, text="850 nm", variable=r, value=850,font = 'Times 12 ')
            R51.grid(row = 5, column = 1, sticky = W,padx = 40, pady = 5)
            
            
            R12 = tkinter.Radiobutton(mFrame, text="1064 nm", variable=r, value=1064,font = 'Times 12 ')
            R12.grid(row = 1, column = 2, sticky = W,padx = 40, pady = 10)
            R22 = tkinter.Radiobutton(mFrame, text= u"8.8 \u03bcm", variable=r, value=8800,font = 'Times 12 ')
            R22.grid(row = 2, column = 2, sticky = W,padx = 40, pady = 5)
            
            R13 = tkinter.Radiobutton(mFrame, text= u"410 \u03bcm", variable=r, value=410000,font = 'Times 12 ')
            R13.grid(row = 1, column = 3, sticky = W,padx = 40, pady = 10)
            
            message = tkinter.Label(mFrame, text = mes, font = 'calibri 12 bold', fg = 'red')
            message.grid(row = 6,column = 0,columnspan = 3,sticky = S+W,pady = (230,5),padx = 20)
            userInput = Button(mFrame,text = 'Upload my data', command = userData,style = 'user.TButton')
            userInput.grid(row = 6,column = 4,sticky = S+E,pady = (0,10),padx = 20)
            
            
        elif nD.isUserData == 1:
            def imMaker(path,n):
                rem = Image.open(path)
                width, height = rem.size
                scale = float(n)/max(width,height)
                r = rem.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
                ret = ImageTk.PhotoImage(r)
                return ret
            def importData():
                try:
                    if userWl.get() <= 0 or userHeight.get() <= 0 or userPeriod.get() <=0:
                        um = 'Enter valid input for Period Wavelength and Height'
                        uMessage.config(text = um)
                        uMessage.text = um,
                        return
                except:
                        um = 'Invalid values for Period, Wavelength and Height'
                        uMessage.config(text = um)
                        uMessage.text = um
                        return
                else:
                    nD.wl  = userWl.get()
                    nD.period  = userPeriod.get()
                    nD.height  = userHeight.get()
                    nD.shape = userShape.get()
                    if nD.shape == "Cylinder":
                        pass
                    elif nD.shape == "Cross":
                        try:
                            if crossWidth.get() <= 0:
                                um = 'Enter valid W for Cross shape'
                                uMessage.config(text = um,fg = 'red')
                                uMessage.text = um,
                                return
                        except:
                            um = 'Invalid input for W of the Cross shape'
                            uMessage.config(text = um,fg = 'red')
                            uMessage.text = um
                            return
                        else:
                            nD.crossW = crossWidth.get() 
                            
                    elif nD.shape == "Fin":
                        try:
                            if finWidth.get() <= 0 and finL.get() <= 0:
                                um = 'Enter valid W and L for the Fin'
                                uMessage.config(text = um,fg = 'red')
                                uMessage.text = um
                                return
                        except:
                            um = 'Invalid input for W or L of Fin'
                            uMessage.config(text = um,fg = 'red')
                            uMessage.text = um,
                            return
                        else:
                            nD.fW = finWidth.get() 
                            nD.fL = finL.get()
                            
                    userDataLoc = tkinter.filedialog.askopenfilename(initialdir = "/",title = "Select file",
                                filetypes = (("Supported formats","*.xlsx"),("Supported formats","*.xls")))        
                    userP = []
                    userDim = []
                    userT = []
                    workbook = xlrd.open_workbook(userDataLoc)
                    sheet =  workbook.sheets()[0]
                    for i in range(sheet.nrows):
                        if type(sheet.row_values(i)[0]) == unicode or type(sheet.row_values(i)[1]) == unicode:
                            um = 'Error: Data cannot be strings and both x y data must be equal length'
                            uMessage.config(text = um,fg = 'red')
                            uMessage.text = um
                            return
                        userDim.append(int(sheet.row_values(i)[0]))
                        userP.append( int(sheet.row_values(i)[1]))
                        userT.append(1)
                    if min(userP) <0 or max(userP) >360:
                        um = 'Error: Phase range must be with in 0 to 360 degrees'
                        uMessage.config(text = um,fg ='red')
                        uMessage.text = um
                        
                    if nD.shape == 'Cylinder':
                        metaData.Data.update({userWl.get():(userShape.get()+'-Unknown','a',userHeight.get(),userPeriod.get(),userDim,userP,userT)})
                    elif nD.shape == 'Cross':
                        metaData.Data.update({userWl.get():(userShape.get()+'-Unknown','a',userHeight.get(),userPeriod.get(),userDim,userP,userT,nD.crossW)})
                    elif nD.shape == 'Fin':
                        metaData.Data.update({userWl.get():(userShape.get()+'-Unknown','a',userHeight.get(),userPeriod.get(),userDim,userP,userT,nD.fW,nD.fL)})
                    um = 'Data uploaded successfully'
                    uMessage.config(text = um,fg = 'blue')
                    uMessage.text = um
                    r.set(nD.wl)
                
            for widget in mFrame.winfo_children():
                widget.destroy()
            #r.set(633)
            #shapesList = ["Cylinder","Cross","V Antenna"]
            shapesList = ["Cylinder","Cross","Fin"]
            global userShape
            userShape = StringVar()
            def shapeCh(*args):
                um = 'Shape changed. Import data again!'
                try:
                    if nD.shape != userShape.get() and nD.wl != 0:
                        uMessage.config(text = um,fg = 'red')
                        uMessage.text = um
                        r.set(0)
                        
                except:
                    pass
            userShape.trace("w", shapeCh)
            userShape.set(nD.shape)
            shapesMenu = OptionMenu(mFrame, userShape,shapesList[shapesList.index(nD.shape)], *shapesList)
            shapesMenu.config(width=15)
            shapesMenu.grid(row = 0 , column = 1,padx = 20,sticky = W,pady = 20)
            tkinter.Label(mFrame, text = 'Select a shape: ', font = 'Times 14').grid(row = 0, column = 0, padx = 20, pady = 20, sticky = W)
            
            tkinter.Label(mFrame, text = 'Wavelength (nm): ', font = 'Times 14').grid(row = 0, column = 2, padx = 20, pady = 20, sticky = W)
            global userWl
            userWl = IntVar()
            userWl.set(nD.wl)
            Entry(mFrame, textvariable = userWl, width = 12,cursor = 'xterm').grid(row = 0, column = 3, sticky = W, pady =20,padx = 20,columnspan = 2) 
            
            tkinter.Label(mFrame, text = 'Period (nm): ', font = 'Times 14').grid(row = 1, column = 0, padx = 20, pady = 20, sticky = W)
            global userPeriod
            userPeriod = IntVar()
            userPeriod.set(nD.period)
            Entry(mFrame, textvariable = userPeriod, width = 12,cursor = 'xterm').grid(row = 1, column = 1, sticky = W, pady =20,padx = 20) 
            
            tkinter.Label(mFrame, text = 'Height (nm): ', font = 'Times 14').grid(row = 2, column = 0, padx = 20, pady = 20, sticky = W)
            global userHeight
            userHeight = IntVar()
            userHeight.set(nD.height)
            Entry(mFrame, textvariable = userHeight, width = 12,cursor = 'xterm').grid(row = 2, column = 1, sticky = W, pady =20,padx = 20)
            
            importData = Button(mFrame,text = 'Import Data', command = importData,style = 'user.TButton')
            importData.grid(row = 3,column = 0,sticky = W,pady = 20,padx = 20)
            
            cIm = imMaker(resource_path('Cross.png'),180)
            cL = tkinter.Label(mFrame,image = cIm)
            cL.imag = cIm
            cL.grid(row = 1, column = 2,columnspan = 1, sticky = W,rowspan = 2)
            
            tkinter.Label(mFrame, text = 'W (nm): ', font = 'Times 12').grid(row = 1, column = 3, padx = 0, pady = 20, sticky = W,rowspan = 2)
            global crossWidth
            crossWidth = IntVar()
            crossWidth.set(nD.crossW)
            Entry(mFrame, textvariable = crossWidth, width = 8,cursor = 'xterm').grid(row = 1, column = 4, sticky = W, pady =20,padx = 0,rowspan = 2)
            
            vIm = imMaker(resource_path('Fin.png'),220)
            vL = tkinter.Label(mFrame,image = vIm)
            vL.imag = vIm
            vL.grid(row = 3, column = 2,columnspan = 1, sticky = W,rowspan = 2)
            
            tkinter.Label(mFrame, text = 'W (nm): ', font = 'Times 12').grid(row = 3, column = 3, padx = 0, pady = 20, sticky = W,rowspan = 1)
            global finWidth
            finWidth = IntVar()
            finWidth.set(nD.fW)
            Entry(mFrame, textvariable = finWidth, width = 8,cursor = 'xterm').grid(row = 3, column = 4, sticky = W, pady =20,padx = 0,rowspan = 1)
            
            
            tkinter.Label(mFrame, text = 'L (nm): ', font = 'Times 12').grid(row = 4, column = 3, padx = 0, pady = 20, sticky = W,rowspan = 1)
            global finL
            finL = IntVar()
            finL.set(nD.fL)
            Entry(mFrame, textvariable = finL, width = 8,cursor = 'xterm').grid(row = 4, column = 4, sticky = W, pady =20,padx = 0,rowspan = 1)
            
            tkinter.Label(mFrame, text = 'Instruction: Please enter phase data in degrees and dimensions in nanometers (degrees for Fin).', font = 'calibri 12 bold', fg = 'blue').grid(row = 5,column = 0,columnspan = 5,sticky = S+W,pady = (0,5),padx = 20)
            #um = 'Phase data must be uploaded in degrees and dimensions in nanometers!'
            uMessage = tkinter.Label(mFrame, text = um, font = 'calibri 12 bold', fg = 'red')
            uMessage.grid(row = 6,column = 0,columnspan = 4,sticky = S+W,pady = (10,5),padx = 20)
            nD.state = 1


    elif i == 2:
        if r.get() == 0:
            if nD.isUserData == 1:
                if nD.wl <=0 or r.get() == 0:
                    um = 'Error: Upload your data first.'
                    nD.height = userHeight.get()
                    nD.period = userPeriod.get()
                    nD.shape = userShape.get()
                    nD.state = 0
                    nD.wl = userWl.get()
                    Next()
                    return
            nD.state = 0
            mes = 'Select a wavelength!'
            Next()
            return
        else:
            # if nD.isUserData == 1:
            #     if userWl.get() ==0 or userHeight.get() ==0 or userPeriod.get() ==0:
            #         um = 'Enter valid values for period wavelength and height'
            #         uMessage.config(text = um)
            #         uMessage.text = um
            #         nD.state = 0
            #         Next()
            #         return
            um = ''    
            nD.wl = int(r.get())
            nD.shape = metaData.Data[nD.wl][0].split('-')[0]
            nD.material = metaData.Data[nD.wl][0].split('-')[1]
            Type = metaData.Data[nD.wl][1]
            nD.type = Type
            nD.height = metaData.Data[nD.wl][2]
            P = metaData.Data[nD.wl][5]
            T = metaData.Data[nD.wl][6]
            if nD.shape == 'Cross':
                nD.crossW = metaData.Data[nD.wl][7]
                xl = 'Length L (nm)'
            else:
                nD.crossW = 'NA'
            
            if nD.shape == 'Cylinder':
                xl = 'Radius r (nm)'
                
            if nD.shape == 'Fin':
                nD.fW = metaData.Data[nD.wl][7]
                nD.crossW = nD.fW
                nD.fL = metaData.Data[nD.wl][8]
                xl = u'Rotation \u03b8 (degrees)'

            if Type == 'a':
                nD.period = metaData.Data[nD.wl][3]
                nD.dim = metaData.Data[nD.wl][4]

                interData = metaData.interpolData(nD.dim,P)
                param = r'Period: '+str(nD.period)+' nm'
                nD.pData = [nD.dim,P]
            elif Type == 'b':
                nD.dim = metaData.Data[nD.wl][3]
                nD.period = metaData.Data[nD.wl][4]
                interData = metaData.interpolData(nD.period,P)
                xl = r'Period $\Lambda$'
                param = r'Radius r: '+str(nD.dim)+' nm'
                nD.pData = [nD.period,P]
            interX = interData[0]
            interP = interData[1]
            fig = plt.figure(1,figsize=(5.3,4.4))
            plt.cla()
            plt.ylabel('Phase (degrees)',size = 13)
            plt.xlabel(xl,size = 13)
            plt.title('Transmission Phase vs '+xl,size = 13)
            plt.ion()
            plt.plot(interX,interP,'bo-',markevery=7)
            plt.xticks(fontsize = 12)
            plt.yticks(fontsize = 12)
            plt.grid()
            def fig2data ( fig ):
                """
                @brief Convert a Matplotlib figure to a numpy array with RGBA channels and return it
                @param fig a matplotlib figure
                @return a numpy 3D array of RGBA values
                """
                # draw the renderer
                fig.canvas.draw ( )
            
                # Get the RGBA buffer from the figure
                w,h = fig.canvas.get_width_height()
                buf = np.frombuffer( fig.canvas.tostring_argb(), dtype=np.uint8 )
                buf.shape = ( w, h,4 )
 
                # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
                buf = np.roll ( buf, 3, axis = 2 )
                return buf
            def fig2img (fig):
                """
                @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
                @param fig a matplotlib figure
                @return a Python Imaging Library ( PIL ) image
                """
                # put the figure pixmap into a numpy array
                buf = fig2data ( fig )
                w, h, d = buf.shape
                return Image.frombytes( "RGBA", ( w ,h ), buf.tostring( ) )
                
            pltIm = fig2img(fig)   
            PlotIm = ImageTk.PhotoImage(pltIm)
                    
            ###Image space###
            Plotlabel = tkinter.Label(mFrame, image = PlotIm, padx = 165)
            Plotlabel.image = PlotIm
            Plotlabel.grid(row=0, column=0,rowspan= 7,sticky = W)    
        
            ##### These lines are causing the exe to fail - display the plot #####
            #canvas = FigureCanvasTkAgg(fig, master=mFrame)
            #plot_widget = canvas.get_tk_widget()
            #plot_widget.grid(row=0, column=0,rowspan= 6,sticky = W)   
            
              
            tkinter.Label(mFrame,text = "Design parameters", font = 'Times 14 bold underline').grid(row = 0, column = 1,sticky = E)
            tkinter.Label(mFrame,text = "Wavelength: "+str(nD.wl)+' nm', font = 'Times 14 ').grid(row = 1, column = 1,sticky = E)
            tkinter.Label(mFrame,text = "Height: "+str(nD.height)+" nm", font = 'Times 14 ').grid(row = 2, column = 1,sticky = E)
            tkinter.Label(mFrame,text = "Width: "+str(nD.crossW)+" nm", font = 'Times 14 ').grid(row = 3, column = 1,sticky = E)
            tkinter.Label(mFrame,text = param, font = 'Times 14  ').grid(row = 4, column = 1,sticky = E)
            tkinter.Label(mFrame,text = "Material: "+str(nD.material), font = 'Times 14  ').grid(row = 5, column = 1,sticky = E)
            tkinter.Label(mFrame,text = "Shape: "+nD.shape, font = 'Times 14  ').grid(row = 6, column = 1,sticky = E)
    elif i==3:
        if mes ==  'Select a wavelength!':
            mes = ' '
        def libFunc():
            global mes
            nD.px = dv1.get()
            nD.lev = dv2.get()
            if r2.get() == 0:
                mes2 = 'Select an optical element!'
                me2.configure(text = mes2)
                me2.text = mes2
            elif r2.get() == 1:
                try:
                    if fzlf.get() == 0 or fzldia.get() == 0:
                        mes2 = 'Enter meaningful parameters for the FZL'
                        me2.configure(text = mes2,fg = 'red')
                        me2.text = mes2
                        return
                        
                except:
                        mes2 = 'Enter meaningful parameters for the FZL'
                        me2.configure(text = mes2,fg = 'red')
                        me2.text = mes2
                        return
                    
                else:
                    nD.fzlF = fzlf.get()
                    nD.fzlDia = fzldia.get()
                    R = nD.fzlDia/2.0
                    nD.pS = int(nD.px[0])*(nD.period/1000.0)
                    nP = int(R/nD.pS)
                    if 2*nP > 1000:
                        mes2 = 'Number of pixels = '+str(2*nP)+' chose smaller diameter or more unitcells per pixels'
                        me2.configure(text = mes2,fg = 'red')
                        me2.text = mes2 
                        nD.design = None
                        nD.dLoc = None
                        return
                    else:
                        points1 = np.linspace(-R,R,2*nP) #generates points 2001 points between -1000 to 1000
                        points2 = np.linspace(R,-R,2*nP) #generates points 2001 points between -1000 to 1000
                        x,y = np.meshgrid(points1 , points2)
                        x1,y1 = np.ogrid[-nP:nP ,-nP:nP]
                        FZL = 2*np.pi - ((2*np.pi/(nD.wl/1000.0))*(np.sqrt(x**2+y**2+nD.fzlF**2) - nD.fzlF))
                        #print np.max(FZL),np.min(FZL)
                        nD.design = FZL % (2*np.pi)
                        nD.design[(x1*x1 + y1*y1) >= nP**2] = 0
                        digitized = (nD.design -  np.min(nD.design)) * 255 / (np.max(nD.design) - np.min(nD.design)) + 0
                        im = Image.fromarray(digitized.astype('uint8'))
                        width, height = im.size
                        m = max(width,height)
                        if m > 330:
                            scale = 330.0/m
                        else:
                            scale = 1
                        globIm = im.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
                        globIm = ImageTk.PhotoImage(globIm)
                        label.config(image = globIm, padx = int((420-width*scale)/2) )
                        label.image = globIm
                        label.padx = int((420-width*scale)/2) 
                        label.update()
                        mFrame.pack_propagate(0)
                        mes2 = ' '
                        me2.config(text = mes)
                        me2.text = mes
                        nD.dLoc = 1
                    mes2 = 'FZL phase generated.'
                    me2.configure(text = mes2,fg = 'blue')
                    me2.text = mes2 
                    me2.fg = 'blue'
                    mes = ''
                    message.config(text = mes)
                    message.text = mes
                    return
                    

                                
                
            elif r2.get() == 2:
                try:
                    if alpha.get() == 0 or dia.get() == 0:
                        mes2 = 'Enter meaningful parameters for the Axicon'
                        me2.configure(text = mes2,fg = 'red')
                        me2.text = mes2    
                        return
                except:
                        mes2 = 'Enter meaningful parameters for the Axicon'
                        me2.configure(text = mes2,fg = 'red')
                        me2.text = mes2    
                        return
                    
                else:
                    nD.axialpha = alpha.get()
                    nD.axidia = dia.get()  
                    R = nD.axidia/2.0
                    nD.pS = int(nD.px[0])*(nD.period/1000.0)
                    nP = int(R/nD.pS)
                    if 2*nP > 1000:
                        mes2 = 'Number of pixels = '+str(2*nP)+' chose smaller diameter or more unitcells per pixels'
                        me2.configure(text = mes2,fg = 'red')
                        me2.text = mes2 
                        nD.design = None
                        nD.dLoc = None
                        return
                    else:
                        points1 = np.linspace(-R,R,2*nP) #generates points 2001 points between -1000 to 1000
                        points2 = np.linspace(R,-R,2*nP) #generates points 2001 points between -1000 to 1000
                        x,y = np.meshgrid(points1 , points2)
                        x1,y1 = np.ogrid[-nP:nP ,-nP:nP]
                        k = np.pi * 2 / (nD.wl/1000.0)
                        cA = np.radians(alpha.get())
                        Axicon  = k * (R-(x**2+y**2)**0.5) * np.tan(cA)
                        nD.design = Axicon % (2*np.pi)
                        nD.design[(x1*x1 + y1*y1) >= nP**2] = 0
                        digitized = (nD.design -  np.min(nD.design)) * 255 / (np.max(nD.design) - np.min(nD.design)) + 0
                        im = Image.fromarray(digitized.astype('uint8'))
                        width, height = im.size
                        m = max(width,height)
                        if m > 330:
                            scale = 330.0/m
                        else:
                            scale = 1
                        globIm = im.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
                        globIm = ImageTk.PhotoImage(globIm)
                        label.config(image = globIm, padx = int((420-width*scale)/2) )
                        label.image = globIm
                        label.padx = int((420-width*scale)/2) 
                        label.update()
                        mFrame.pack_propagate(0)
                        mes2 = ' '
                        me2.config(text = mes)
                        me2.text = mes
                        nD.dLoc = 1
                    mes2 = 'Axicon phase generated.'
                    me2.configure(text = mes2,fg = 'blue')
                    me2.text = mes2 
                    me2.fg = 'blue'
                    mes = ''
                    message.config(text = mes)
                    message.text = mes
                    return
                
            elif r2.get() == 3:
                try:
                    if sppl.get() == 0 or sppdia.get() == 0:
                        mes2 = 'Enter meaningful parameters for the SPP'
                        me2.configure(text = mes2,fg = 'red')
                        me2.text = mes2
                except:
                        mes2 = 'Enter meaningful parameters for the SPP'
                        me2.configure(text = mes2,fg = 'red')
                        me2.text = mes2
                    
                else:
                    nD.sppl = sppl.get()
                    nD.sppdia = sppdia.get()  
                    R = nD.sppdia/2.0
                    nD.pS = int(nD.px[0])*(nD.period/1000.0)
                    nP = int(R/nD.pS)
                    #print 2*nP
                    if 2*nP > 1000:
                        mes2 = 'Number of pixels = '+str(2*nP)+' chose smaller diameter'
                        me2.configure(text = mes2,fg = 'red')
                        me2.text = mes2 
                        nD.design = None
                        nD.dLoc = None
                        return
                    else:
                        points1 = np.linspace(-R,R,2*nP) #generates points 2001 points between -1000 to 1000
                        points2 = np.linspace(R,-R,2*nP) #generates points 2001 points between -1000 to 1000
                        x,y = np.meshgrid(points1 , points2)
                        x1,y1 = np.ogrid[-nP:nP ,-nP:nP]
                        r = np.sqrt(x**2 + y**2)
                        SPP =  nD.sppl*np.arctan2(y,x)
                        nD.design = SPP + nD.sppl*np.pi
                        nD.design = nD.design % (2*np.pi)
                        nD.design[(x1*x1 + y1*y1) >= nP**2] = 0
                        digitized = (nD.design -  np.min(nD.design)) * 255 / (np.max(nD.design) - np.min(nD.design)) + 0
                        im = Image.fromarray(digitized.astype('uint8'))
                        width, height = im.size
                        m = max(width,height)
                        if m > 330:
                            scale = 330.0/m
                        else:
                            scale = 1
                        globIm = im.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
                        globIm = ImageTk.PhotoImage(globIm)
                        label.config(image = globIm, padx = int((420-width*scale)/2) )
                        label.image = globIm
                        label.padx = int((420-width*scale)/2) 
                        label.update()
                        mFrame.pack_propagate(0)
                        mes2 = ' '
                        me2.config(text = mes)
                        me2.text = mes
                        nD.dLoc = 1
                    mes2 = 'SPP phase generated.'
                    me2.configure(text = mes2,fg = 'blue')
                    me2.text = mes2 
                    me2.fg = 'blue'
                    mes = ''
                    message.config(text = mes)
                    message.text = mes
                    return
                return
                
                
                
        def handler():
            global mes
            fileLoc = tkinter.filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("Supported formats","*.jpg"),("Supported formats","*.png"),("Supported formats","*.jpeg")))
            if fileLoc == "":
                nD.state = 2
                Next()
                return
            else:
                im = Image.open(fileLoc)
                width, height = im.size
                m = max(width,height)
                if m > 2001:
                    nD.state = 2
                    mes = 'Pixels must be  < 1000. Image not loaded.'
                    message.config(text = mes)
                    message.text = mes
                    nD.design = None
                    nD.dLoc = None
                    Next() 
                else:
                    if m > 330:
                        scale = 330.0/m
                    else:
                        scale = 1
                    globIm = im.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
                    globIm = ImageTk.PhotoImage(globIm)
                    label.config(image = globIm, padx = int((420-width*scale)/2) )
                    label.image = globIm
                    label.padx = int((420-width*scale)/2) 
                    label.update()
                    mFrame.pack_propagate(0)
                    imArray = imageio.imread(fileLoc, as_gray =  True)
                    nD.design = imArray
                    nD.dLoc = fileLoc
                    mes = ' '
                    message.config(text = mes)
                    message.text = mes
        tkinter.Label(mFrame,text = 'Unitcells per pixel',font = 'Times 13').grid(row = 0, column = 0, sticky = W, pady = (0,10)) 
        global ol1,ol2
        ol1 = ["1x1","2x2","3x3","4x4","5x5","6x6"]
        global dv1
        global dv2
        dv1=StringVar(root)
        dv1.set(nD.px)
        pm1 = OptionMenu(mFrame, dv1,ol1[int(nD.px[0])-1], *ol1)
        pm1.config(width=7)
        pm1.grid(row = 0 , column = 1, pady = (0,10),padx = 40)
        tkinter.Label(mFrame,text = 'Phase levels',font = 'Times 13').grid(row = 1, column = 0, sticky = W, pady = (0,10)) 
        ol2 = [2,4,8,16]
        dv2 = IntVar(root)
        dv2.set(nD.lev)
        pm2 = OptionMenu(mFrame, dv2,ol2[ol2.index(nD.lev)], *ol2)
        pm2.config(width=7)
        pm2.grid(row = 1 , column = 1, pady = (0,10),padx = 40)
        tkinter.Label(mFrame,text = 'Phase min(deg.)',font = 'Times 13').grid(row = 2, column = 0, sticky = W, pady = (0,10)) 
        tkinter.Label(mFrame,text = 'Phase max(deg.)',font = 'Times 13').grid(row = 3, column = 0, sticky = W, pady = (0,10)) 
        global minPh
        minPh = IntVar(root)
        minPh.set(nD.minph)
        global maxPh
        maxPh = IntVar(root)
        maxPh.set(nD.maxph)
        Entry(mFrame, textvariable = minPh, width = 12,cursor = 'xterm').grid(row = 2, column = 1, sticky = W, pady = (0,10),padx = 40) 
        Entry(mFrame, textvariable = maxPh, width = 12,cursor = 'xterm').grid(row = 3, column = 1, sticky = W, pady = (0,10),padx = 40) 
        global checkVar
        checkVar = IntVar(root)
        checkVar.set(nD.isCircular)
        tkinter.Checkbutton(mFrame, text="Apply circular aperture", variable=checkVar,font = 'Times 13').grid(row = 4, column = 0,columnspan = 2, sticky = W, pady = (0,10),padx = 0)
        
        message = tkinter.Label(mFrame, text = mes, font = 'calibri 12 bold', fg = 'red')
        message.grid(row = 5,column = 0,columnspan = 2,sticky = W,pady = (75,5))
        
        
        importPhase = Button(mFrame,text = 'Import Phase', command =  handler,width = 14, takefocus=False)
        importPhase.grid(row = 6, column = 0,columnspan = 2,padx = (15,0),sticky = W)
        
        ###Image space###
        label = tkinter.Label(mFrame, padx = 165)
        label.grid(row = 0, column = 2, rowspan = 7,columnspan = 4)
        
        
        tkinter.Label(mFrame, text = '-------------------------------------------Library Functions-------------------------------------------',fg='blue',font = 'Times 14  italic').grid(row  = 7,column =0,columnspan = 6,pady = (15,0))
        #mFrame.columnconfigure(0, weight=1)
        R1 = tkinter.Radiobutton(mFrame, text="FZL", variable=r2, value=1,font = 'Times 14  underline bold ')
        R1.grid(row = 8, column = 0,pady = (0,0),columnspan = 2)
        R2 = tkinter.Radiobutton(mFrame, text="Axicon", variable=r2, value=2,font = 'Times 14  underline bold ')
        R2.grid(row = 8, column = 2, pady = (0,0),columnspan = 2)
        R3 = tkinter.Radiobutton(mFrame, text="SPP", variable=r2, value=3,font = 'Times 14  underline bold')
        R3.grid(row = 8, column = 4,pady = (0,0),columnspan = 2)
        
        ###FZL###
        global fzlf
        global fzldia
        fzlf = IntVar(root)
        fzlf.set(nD.fzlF)
        fzldia = DoubleVar(root)
        fzldia.set(nD.fzlDia)
        tkinter.Label(mFrame,text = 'Focal length(um): ',font = 'Times 13' ).grid(row = 9, column = 0,pady = 0,padx = 0,sticky = W)
        Entry(mFrame, textvariable = fzlf, width = 8,cursor = 'xterm').grid(row = 9, column = 1, pady = 10) 
        tkinter.Label(mFrame,text = 'Diameter (um):',font = 'Times 13' ).grid(row = 10, column = 0,pady = 0, padx = 0,sticky = W)
        Entry(mFrame, textvariable = fzldia, width = 8,cursor = 'xterm').grid(row = 10, column = 1,pady = 0) 
        
        ###Axicon###
        global alpha
        global dia
        alpha = DoubleVar(root)
        alpha.set(nD.axialpha)
        dia = DoubleVar(root)
        dia.set(nD.axidia)
        tkinter.Label(mFrame,text = 'Cone angle: ',font = 'Times 13' ).grid(row = 9, column = 2,pady = 0,sticky = W)
        Entry(mFrame, textvariable = alpha, width = 8,cursor = 'xterm').grid(row = 9, column = 3, pady = 0,padx= (20,0)) 
        tkinter.Label(mFrame,text = 'Diameter (um):',font = 'Times 13' ).grid(row = 10, column = 2,pady = 0,sticky = W)
        Entry(mFrame, textvariable = dia, width = 8,cursor = 'xterm').grid(row = 10, column = 3, pady = 0,padx= (20,0)) 
        
        global sppl
        global sppdia
        sppl=IntVar(root)
        sppl.set(nD.sppl)
        sppdia = DoubleVar(root)
        sppdia.set(nD.sppdia)
        tkinter.Label(mFrame,text = 'Charge: ',font = 'Times 13' ).grid(row = 9, column = 4,pady = 0,padx = (20,20),sticky = W)
        Entry(mFrame, textvariable = sppl, width = 8,cursor = 'xterm').grid(row = 9 , column = 5, pady = 0,padx = (20,20))
        tkinter.Label(mFrame,text = 'Diameter (um):',font = 'Times 13' ).grid(row = 10, column = 4,pady = 0, padx = (20,20),sticky = W)
        Entry(mFrame, textvariable = sppdia, width = 8,cursor = 'xterm').grid(row = 10, column = 5,pady = 0,padx = (20,20)) 
        
        
        mes2 = ' '
        me2  = tkinter.Label(mFrame, text = mes2, font = 'calibri 12 bold', fg = 'red')
        me2.grid(row = 11,column = 0,columnspan = 5,sticky = W)
        libGen = Button(mFrame,text = 'Generate', command =  libFunc,width = 10, takefocus=False,style = 'Small.TButton')
        libGen.grid(row = 11,column = 5,sticky = E,pady = (2,0),padx = (0,20))
        
        if nD.dLoc != None:
            digitized = (nD.design -  np.min(nD.design)) * 255 / (np.max(nD.design) - np.min(nD.design)) + 0
            im = Image.fromarray(digitized.astype('uint8'))
            width, height = im.size
            m = max(width,height)
            if m > 330:
                scale = 330.0/m
            else:
                scale = 1
            globIm = im.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
            globIm = ImageTk.PhotoImage(globIm)
            label.config(image = globIm,padx = int((420-width*scale)/2))
            label.image = globIm
            label.padx = int((420-width*scale)/2) 
            label.update()
            mFrame.pack_propagate(0)
            
    elif i == 4:
        # if r2.get()==3:
        #     nD.px = '1x1' ###Special case for SPP
        # else:
        #     nD.px = dv1.get()
        nD.px = dv1.get()
        nD.lev = dv2.get()
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
            nD.pS = int(nD.px[0])*(nD.period/1000.0)
            nD.isCircular = checkVar.get()
            if nD.dLoc == None:
                nD.state = 2
                mes = 'Import Phase design!'
                Next()
            else:
                mes = ''
                bins = []
                phRange = nD.maxph - nD.minph
                design = (nD.design - np.min(nD.design)) * phRange / (np.max(nD.design) - np.min(nD.design))
                interval = phRange/float(nD.lev)
                for i in range(nD.lev):
                    bins.append(nD.minph+i*interval)    
                #print bins
                Phi = np.digitize(design, bins)
                # import pylab as py
                # py.imshow(Phi)
                # py.show()
                nD.bins = bins
                nD.mask = Phi
                digitized = (Phi -  np.min(Phi)) * 255 / (np.max(Phi) - np.min(Phi)) + 0
                im = Image.fromarray(digitized.astype('uint8'))
                width, height = im.size
                m = max(width,height)
                if m > 330:
                    scale = 330.0/m
                else:
                    scale = 1
                globIm = im.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
                globIm = ImageTk.PhotoImage(globIm)
                label = tkinter.Label(mFrame,image = globIm)
                label.image = globIm
                label.grid(padx = int((420-width*scale)/2),row = 0,column = 0,rowspan = 2)
                mFrame.pack_propagate(0)
                progressVar = DoubleVar(root)
                progress=Progressbar(mFrame,orient=HORIZONTAL,variable=progressVar, maximum = 100, length = 290)
                progress.grid(padx = 20,pady = 10,row = 2,column = 0)
                nD.progress = progressVar
                tkinter.Label(mFrame,text = 'Design parameters', font = 'Times 13 bold underline').grid(row = 0,column = 1,sticky = W)
                Info = tkinter.Label(mFrame,text = 'Wavelength: '+str(nD.wl)+' nm\n\n'
                'Unitcells per pixel: '+str(nD.px)+'\n\n'+
                'Unitcell period: '+str(nD.period)+'\n\n'+
                'Phase levels: '+str(nD.lev)+'\n\n'+
                'Pixel size (Unitcells per pixel X period): '+str(int(nD.px[0])*nD.period)+' nm\n\n'+
                'Pixels in Phase mask: '+ str(nD.design.shape[0])+' X '+str(nD.design.shape[1])+'\n\n'+
                'Phase mask radius: '+str(min(nD.design.shape[0],nD.design.shape[1])*int(nD.px[0])*nD.period/1000)+' um\n\n'+
                'Circular aperture applied: '+str(nD.isCircular == 1)+'\n\n',
                font = 'Times 12',anchor=W,justify=LEFT)
                Info.grid(row = 1,column = 1 ,sticky = W+N)
                
                gds = Button(mFrame,text = 'Generate GDS', command =  gdsGen,width = 14, takefocus=False)
                gds.grid(sticky = W,pady = 10,row = 2,column = 1)
                tkinter.Label(mFrame,text = 'Design parameters', font = 'Times 13 bold underline').grid(row = 0,column = 1,sticky = W)
                    
                TimeInfo = tkinter.Label(mFrame, text = '',justify = LEFT, anchor = W,font = 'Times 12')
                TimeInfo.grid(row = 3, column = 1, sticky = W)
                nD.tLab = TimeInfo
                
            
def gdsGen():
    nD.sLoc =  tkinter.filedialog.asksaveasfilename()
    if nD.sLoc == "":
        nD.state = 3
        Next()
    else:
        gdsModule.gdsGen(nD)
    return
    
def StartNew():
    for widget in mFrame.winfo_children():
        widget.destroy()
    tl1 = tkinter.Label(tFrame, text="Wavelength", font = 'Times 13 bold',background = 'RoyalBlue1', padx = 5,pady = 5)
    tl1.grid(row = 0, column = 0, padx = 50)
    tl1 = tkinter.Label(tFrame, text="Phase curve", font = 'Times 13 bold',background = 'RoyalBlue1',padx = 5,pady = 5)
    tl1.grid(row = 0, column = 1, padx = 20)
    tl1 = tkinter.Label(tFrame, text="Phase Design",  font = 'Times 13 bold',background = 'RoyalBlue1',padx = 5,pady = 5)
    tl1.grid(row = 0, column = 2, padx = 20)
    tl1 = tkinter.Label(tFrame, text="GDSII Design", font = 'Times 13 bold',background = 'RoyalBlue1',padx = 5,pady = 5)
    tl1.grid(row = 0, column = 3, padx = 50)
    tFrame.columnconfigure(2, weight=1)
    tFrame.columnconfigure(1, weight=1)
    rm = Image.open(resource_path('Instructions.png'))
    width, height = rm.size
    m = max(width,height)
    if m > 690:
        scale = 690.0/m
        rm = rm.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
    rm = ImageTk.PhotoImage(rm)
    iL = tkinter.Label(mFrame,image = rm)
    iL.image = rm
    iL.pack(pady = 10)
    nD.state = 0
    nD.dLoc = None
    nD.design = None
    nD.px = '1x1'
    nD.lev = 2
    nD.minph = 0
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
    #Library reset#
    nD.axialpha = 0.0
    nD.axidia = 0.0
    nD.sppl = 1
    nD.sppdia = 0.0
    nD.fzlF = 0.0
    nD.fzlDia = 0.0
    nD.isCircular = 0
    nD.fL = 0
    nD.material = None
    
def about():
    for widget in mFrame.winfo_children():
        widget.destroy()
    tl1 = tkinter.Label(tFrame, text="Wavelength", font = 'Times 13 bold',background = 'RoyalBlue1', padx = 5,pady = 5)
    tl1.grid(row = 0, column = 0, padx = 50)
    tl1 = tkinter.Label(tFrame, text="Phase curve", font = 'Times 13 bold',background = 'RoyalBlue1',padx = 5,pady = 5)
    tl1.grid(row = 0, column = 1, padx = 20)
    tl1 = tkinter.Label(tFrame, text="Phase Design",  font = 'Times 13 bold',background = 'RoyalBlue1',padx = 5,pady = 5)
    tl1.grid(row = 0, column = 2, padx = 20)
    tl1 = tkinter.Label(tFrame, text="GDSII Design", font = 'Times 13 bold',background = 'RoyalBlue1',padx = 5,pady = 5)
    tl1.grid(row = 0, column = 3, padx = 50)
    tFrame.columnconfigure(2, weight=1)
    tFrame.columnconfigure(1, weight=1)
    rm = Image.open(resource_path('About.png'))
    width, height = rm.size
    m = max(width,height)
    if m > 689:
        scale = 689.0/m
        rm = rm.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
    rm = ImageTk.PhotoImage(rm)
    iL = tkinter.Label(mFrame,image = rm)
    iL.image = rm
    iL.pack(pady = 10) 

class Design():
    def __init__(self):
        self.isUserData = 0
        self.wl = 0
        self.pData = None
        self.design  = None
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
        self.type = 'a'
        self.progress = 0
        self.root = root
        self.sLoc = None
        self.pS = 0
        self.mask = None
        ### Library design parameters ###
        self.axialpha = 0.0
        self.axidia = 0.0
        self.sppl = 1
        self.sppdia = 0.0
        self.fzlF = 0.0
        self.fzlDia = 0.0
        self.isCircular = 0
        self.cTime = [0,0]   #Conversion time
        self.tLab = None
        self.crossW = 0
        self.fW = 0
        self.fL =0
        self.material = None
        


#######Main Layout and Buttons#####
nD = Design()

tl1 = tkinter.Label(tFrame, text="Wavelength", font = 'Times 13 bold', background = 'RoyalBlue1', padx = 5,pady = 5)
tl1.grid(row = 0, column = 0, padx = 50)
tl1 = tkinter.Label(tFrame, text="Phase curve",  font = 'Times 13 bold', background = 'RoyalBlue1',padx = 5,pady = 5)
tl1.grid(row = 0, column = 1, padx = 20)
tl1 = tkinter.Label(tFrame, text="Phase Design",  font = 'Times 13 bold', background = 'RoyalBlue1',padx = 5,pady = 5)
tl1.grid(row = 0, column = 2, padx = 20)
tl1 = tkinter.Label(tFrame, text="GDSII Design", font = 'Times 13 bold', background = 'RoyalBlue1',padx = 5,pady = 5)
tl1.grid(row = 0, column = 3, padx = 50)
tFrame.columnconfigure(2, weight=1)
tFrame.columnconfigure(1, weight=1)


previous = Button(bFrame,text = 'About', command =  about,width = 14, takefocus=False)
previous.grid(row = 0,column = 0, padx = 13)

start = Button(bFrame,text = 'Start New', command =  StartNew,width = 14, takefocus=False)
start.grid(row = 0,column = 1, padx = 13)

previous = Button(bFrame,text = 'Previous', command =  Previous,width = 14, takefocus=False)
previous.grid(row = 0,column = 2, padx = 13)

nexst = Button(bFrame,text = 'Next', command =  Next,width = 14, takefocus=False)
nexst.grid(row = 0,column = 4, padx = 13)
root.mainloop()
