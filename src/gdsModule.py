######GDS Creation#######
from gdsCAD import *
import numpy as np
import metaData
#from tqdm import *
import time
import os

def gdsGen(nD,t = 'a' ):
    pxSiz = nD.pS * 1000
    Phi = nD.mask
    bins = nD.bins
    f1 =  metaData.interpolData(nD.pData[0],nD.pData[1])[2]
    cell = core.Cell('Layout')
    p = nD.period
    layout = core.Layout('Metasurface',unit = 1e-9, precision = 1e-11)
    d = dict()
    row,col = Phi.shape
    if nD.isCircular == 1:
        m = min(row,col)
        n = min(row,col)
    else:
        #print nD.isCircular
        m = min(row,col)
        n = min(row,col)*3
    t = time.time()
    ttext = 'Conversion in progress......'
    nD.tLab.config(text = ttext, fg = 'blue')
    nD.tLab.text = ttext
    
    ### Method to create boundary points of cross###
    def crossShape(cl):
        w = float(nD.crossW)
        l = float(cl)
        pts = [(-w/2,-l/2),(w/2,-l/2),(w/2,-w/2),(l/2,-w/2),(l/2,w/2),(w/2,w/2),(w/2,l/2),(-w/2,l/2),(-w/2,w/2),(-l/2,w/2),(-l/2,-w/2),(-w/2,-w/2)]
        return pts
    ### Method to create boundary points of Fin ###
    def finShape(theta):
        theta = np.radians(theta)
        def cTrans(x,y):
            xt = x*np.cos(theta) + y*np.sin(theta)
            yt = -x*np.sin(theta) + y*np.cos(theta)
            return (xt,yt)
        fl = float(nD.fL)
        fw = float(nD.fW)
        pts = [cTrans(-fl/2,-fw/2), cTrans(fl/2,-fw/2),cTrans(fl/2,fw/2),cTrans(-fl/2,fw/2)]
        return pts
                  
    for i in range(row):
        k = (float(i)/row)*100
        nD.progress.set(k)
        time.sleep(0.001)
        nD.root.update()
        for j in range(col):
            if (i-m/2)**2+(j-m/2)**2>=(n/2)**2:
                pass
            else:
                phase = bins[Phi[row-i-1,j]-1]
                if phase >= np.max(metaData.Data[nD.wl][5]):
                    phase = np.max(metaData.Data[nD.wl][5])
                elif phase <= np.min(metaData.Data[nD.wl][5]):
                    phase = np.min(metaData.Data[nD.wl][5])
                r = np.round((f1(phase)),1)
                if r not in d:
                    c = core.Cell('cell'+str(r))
                    
                    ##### Logic 1######
                    
                    if nD.shape == 'Cylinder':
                        c.add(shapes.Disk((0,0),r))
                    elif nD.shape == 'Cross':
                        c.add(core.Boundary(crossShape(r)))
                    elif nD.shape == 'Fin':
                        c.add(core.Boundary(finShape(r)))
                    cellArray = core.Cell('cellArray'+str(r))
                    cellArray.add(core.CellArray(c,int(nD.px[0]),int(nD.px[0]),(int(nD.period),int(nD.period))))
                    d[r] = cellArray
                    
                    
                    ##### Logic 2########
                    
                    # for k in range(int(nD.px[0])):
                    #     for l in range(int(nD.px[0])):
                    #         if nD.shape == 'Cylinder':
                    #             c.add(shapes.Disk ((p*k,p*l),r))
                    #         elif nD.shape == 'Cross':
                    #             pass
                    # d[r] = c
                    
                    cell.add(core.CellReference(d[r],origin = (j*pxSiz,i*pxSiz)))
                else:
                    cell.add(core.CellReference(d[r],origin = (j*pxSiz,i*pxSiz)))
    layout.add(cell)
    layout.save(nD.sLoc+'.gds')
    tot = int((time.time() - t))
    m = int(tot/60)
    s  = int(tot%60)
    nD.cTime = [m,s]
    outSize = os.path.getsize(nD.sLoc+'.gds')/1024
    ttext = 'Metasurface GDS Generated. \n\n'+'Conversion time: '+str(nD.cTime[0])+' minutes and '+str(nD.cTime[1])+' seconds\n\n'+'Output GDS file size: '+str(outSize)+' KB'
    nD.tLab.config(text = ttext)
    nD.tLab.text = ttext
    nD.root.update()
    return tot
