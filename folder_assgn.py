import os
import time

today=time.localtime(time.time())
date=str(today.tm_year)+'-'+f"{today.tm_mon:02}"+'-'+f"{today.tm_mday:02}"

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory.' + directory)

def casedef(geom,freq,volt,trial):
    fname=geom+'_'+freq+'Hz_'+volt+'ulmin_t'+trial
    createFolder(date)
    foldname=date
    imfoldname=foldname+'/'+fname
    createFolder(foldname)
    createFolder(imfoldname)
	
    return foldname, fname, imfoldname

