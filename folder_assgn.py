import os
import time

today=time.localtime(time.time())
date=str(today.tm_year)+'-'+str(today.tm_mon)+'-'+str(today.tm_mday)

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory.' + directory)

def casedef(geom,freq,volt,trial):
    fname=geom+'_'+freq+'_'+volt+'_t'+trial
    createFolder(date)
    foldname=date
    imfoldname=foldname+'/'+fname
    createFolder(foldname)
    createFolder(imfoldname)
	
    return foldname, fname, imfoldname

