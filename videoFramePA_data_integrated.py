"""
Created on Mon Oct 31 08:24:16 2022

@author: Nils, Pranil, Prashant
"""

"""
Code for taking average pixel intensity data from a raspberry pi HQ camera
GUI consists of:
    1) Inputting information on file name for data storage: When pressing Record, the average pixel data is stored in a csv with time stamps and corresponding snapshots of the cropped region are also stored
    2) Setting camera exposure
    3) Setting fps for saving: this is very approximate. Basically the code sleeps for 1/SaveFPS seconds before logging data and saving image
    4) Setting region for calculating average pixel intensity in the image
    5) Display of maximum and current average pixel intensity
    6) Record: to start recording. Pushing it again stops the recording. Change file name and push again to start another experiment otherwise old data is re-written
    7) Quit: to exit the GUI
    8) Display for recording status
    9) Display of file name that will be saved    
"""
from cgitb import text
from tkinter import *
from PIL import ImageTk, Image
import numpy as np
import cv2
import time
import matplotlib.pyplot as plt
import threading
import os, sys
import folder_assgn as folders

#creating folder and file names

def folder_file_def():
    global device, freq, volt, trial, foldname, filename, imfoldname, csvname
    names=folders.casedef(device,freq,volt,trial)
    foldname=names[0]
    filename=names[1]
    imfoldname=names[2]
    #creating csv file for storing pixel data
    csvname=foldname+"/"+filename+".csv"
    f=open(csvname,"w+")
    f.close()
    f=open(csvname,"a")
    f.write("Time (s)"+","+"Counter"+","+"Pixel intensity"+"\n")
    f.close()

stop_threads=False
continueRecording = False
expo=100
SaveFPS=2
sliderposshift=4

def change_state(): 
    global continueRecording
    if continueRecording == True: 
        continueRecording = False 
    else: 
        continueRecording = True 

#Global Variables
#Set default values for x y w h sliders
defaultResX = 640
defaultResY = 480
sliderFrom = 00
sliderTo = 100
resXScaler = defaultResX/(sliderTo-sliderFrom)
resYScaler = defaultResY/(sliderTo-sliderFrom)
defaultX = defaultY = 0.40*((sliderTo-sliderFrom)+sliderFrom)
defaultW = defaultH = 0.20*((sliderTo-sliderFrom)+sliderFrom)

#Main Window
root = Tk()
#root.attributes('-zoomed', True)
#Video and GUI inside root
video = Label(root, text='Live video')
video.grid(row=1, column=3)
gui = Label(root)
gui.grid(row=1, column=0)

DeviceLabel=Label(gui, text="Device").grid(row=1, column=0, padx=0, pady=0)
Devicetxt = Text(gui, height = 1, width = 20)
Devicetxt.grid(row=1, column=1, padx=0, pady=0)

Param1Label=Label(gui, text="Frequency").grid(row=2, column=0, padx=0, pady=0)
Param1txt = Text(gui, height = 1, width = 20)
Param1txt.grid(row=2, column=1, padx=0, pady=0)

Param2Label=Label(gui, text="Voltage").grid(row=3, column=0, padx=0, pady=0)
Param2txt = Text(gui, height = 1, width = 20)
Param2txt.grid(row=3, column=1, padx=0, pady=0)

TrialLabel=Label(gui, text="Trial").grid(row=4, column=0, padx=0, pady=0)
Trialtxt = Text(gui, height = 1, width = 20)
Trialtxt.grid(row=4, column=1, padx=0, pady=0)

def getTextVals():
    global device, freq, volt, trial
    device=Devicetxt.get(1.0, "end-1c")
    freq=Param1txt.get(1.0, 'end-1c')
    volt=Param2txt.get(1.0, 'end-1c')
    trial=Trialtxt.get(1.0, 'end-1c')

expoEntry = Scale(gui, from_=0, to=400, orient=HORIZONTAL, label='Exposure')
expoEntry.set(expo)
expoEntry.grid(row=sliderposshift+1, column=0, padx=0, pady=0)

SfpsEntry = Scale(gui, from_=0, to=20, orient=HORIZONTAL, label='SaveFPS')
SfpsEntry.set(SaveFPS)
SfpsEntry.grid(row=sliderposshift+1, column=1, padx=0, pady=0)

#Define x and y entry box labels and boxes
xEntry = Scale(gui, from_=sliderFrom, to=sliderTo, orient=HORIZONTAL, label='Pixel X')
xEntry.set(defaultX)
xEntry.grid(row=sliderposshift+3, column=0, padx=0, pady=0)

xpEntry = Scale(gui, from_=sliderFrom, to=sliderTo, orient=HORIZONTAL, label='Image X')
xpEntry.set(defaultX)
xpEntry.grid(row=sliderposshift+3, column=1, padx=0, pady=0)

wEntry = Scale(gui, from_=sliderFrom, to=sliderTo, orient=HORIZONTAL, label='Pixel width')
wEntry.set(defaultW)
wEntry.grid(row=sliderposshift+4, column=0, padx=0, pady=0)
wpEntry = Scale(gui, from_=sliderFrom, to=sliderTo, orient=HORIZONTAL, label='Image width')
wpEntry.set(defaultX)
wpEntry.grid(row=sliderposshift+4, column=1, padx=0, pady=0)

yEntry = Scale(gui, from_=sliderFrom, to=sliderTo, orient=HORIZONTAL, label='Pixel Y')
yEntry.set(defaultY)
yEntry.grid(row=sliderposshift+5, column=0, padx=0, pady=0)
ypEntry = Scale(gui, from_=sliderFrom, to=sliderTo, orient=HORIZONTAL, label='Image Y')
ypEntry.set(defaultX)
ypEntry.grid(row=sliderposshift+5, column=1, padx=0, pady=0)

hEntry = Scale(gui, from_=sliderFrom, to=sliderTo, orient=HORIZONTAL, label='Pixel height')
hEntry.set(defaultH)
hEntry.grid(row=sliderposshift+6, column=0, padx=0, pady=0)
hpEntry = Scale(gui, from_=sliderFrom, to=sliderTo, orient=HORIZONTAL, label='Image height')
hpEntry.set(defaultX)
hpEntry.grid(row=sliderposshift+6, column=1, padx=0, pady=0)


#Display for pixel intensity
basepix = Label(gui, text='Current Pix: Val')
basepix.grid(row=sliderposshift+7, column=1, padx=1, pady=1) 

maxpix = Label(gui, text='Max Pix: Val', background='black', foreground='white')
maxpix.grid(row=sliderposshift+8, column=1, padx=1, pady=1)

statusLabel = Label(gui, text='Status:', foreground='black')
statusLabel.grid(row=sliderposshift+9, column=0, padx=1, pady=1) 
status = Label(gui, text='Not recording', foreground='red')
status.grid(row=sliderposshift+9, column=1, padx=1, pady=1) 

fileLabeltxt = Label(gui, text='File name:')
fileLabeltxt.grid(row=sliderposshift+10, column=0, padx=1, pady=1) 
fileLabel = Label(gui, text='NA')
fileLabel.grid(row=sliderposshift+10, column=1, padx=1, pady=1) 

# Capture from camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
#cap.set(cv2.CAP_PROP_FPS, 20)

# function for video streaming (640x480)
def video_stream():
    global x, y, w, h, xp, yp, wp, hp
    setVariables()
    cap.set(cv2.CAP_PROP_EXPOSURE, int(expoEntry.get()))
    _, frame = cap.read()
    cv2image = cv2.rectangle(frame,(x,y),((x+w),(y+h)),(255,255,255),2)
    cv2image = cv2.rectangle(cv2image,(xp,yp),((xp+wp),(yp+hp)),(125,125,125),3)
    #cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2RGBA)
    cv2image = cv2.cvtColor(cv2image, cv2.COLOR_BGR2GRAY)
    img = Image.fromarray(cv2image)
    #img=img.resize((450,450))
    imgtk = ImageTk.PhotoImage(image=img)
    video.imgtk = imgtk
    video.configure(image=imgtk)
    video.after(1, video_stream)
    
#setting values for x y w h window for cropping
def setVariables():
    global x, xp, y, yp, w, wp, h, hp, resXScaler, resYScaler
    x = int(float(xEntry.get()) * resXScaler)
    xp = int(float(xpEntry.get()) * resXScaler)
    y = int(float(yEntry.get()) * resYScaler)
    yp = int(float(ypEntry.get()) * resYScaler)
    w = int(float(wEntry.get()) * resXScaler)
    wp = int(float(wpEntry.get()) * resXScaler)
    h = int(float(hEntry.get()) * resYScaler)
    hp = int(float(hpEntry.get()) * resYScaler)
    
#Capturing instant snapshot
# def image_capture():
#     _, frame = cap.read()
#     folder_file_def()
#     cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
#     cv2.imwrite(imfoldname+"/"+filename+ ".jpg",cv2image)

def recorder():
    counter=0
    maximumpix=0
    sleeptime=1/SfpsEntry.get()
    timestart=time.time()
    while continueRecording:       
        with open(csvname,"a") as log:
            counter += 1
            time.sleep(sleeptime)
            #image cropper
            _, frame = cap.read()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            img_crop=cv2image[y:y+h, x:x+w]
            img_crop2=cv2image[yp:yp+hp, xp:xp+wp]
            #calculating average pixel intensity and storing in excel
            pix=np.mean(img_crop)            
            log.write(str(time.time()-timestart)+","+str(counter)+","+str(pix)+"\n")
            log.flush()
            #saving image at time instant
            cvfilename = imfoldname+"/"+filename+"_" +  f"{counter:05}" + ".jpg"
            #cvfilename_crop = imfoldname+"/"+filename+"_crop_000" +  str(counter) + ".jpg"
            #cv2.imwrite(cvfilename, cv2image)
            cv2.imwrite(cvfilename, img_crop2)
            #For displaying pixel intensity
            maximumpix=max(maximumpix, pix)            
            maxpix.config(text='Max Pix: '+ str(int(maximumpix)))
            basepix.config(text='Current Pix: '+ str(int(pix)), foreground='red')
            if stop_threads:
                cap.release()
                break
            
def gui_handler(): 
    change_state()
    if continueRecording:
        stop_threads=False
        RecordButton.configure(text='Recording',bg='green', fg='white')
        getTextVals()
        folder_file_def()
        fileLabel.config(text=csvname)
        status.config(text='Recording', foreground='green')
        threading.Thread(target=recorder).start()
    else:
        RecordButton.configure(text='Record', bg='red', fg='black')
        status.config(text='Not Recording')
        stop_threads=True
    
def quit_handle():
    global stop_threads
    stop_threads=True
    cap.release()
    root.destroy()
    #root.quit()
    exit()
    
#Call video function
video_stream()

# SnapButton = Button(gui, text="Snap",command = image_capture).grid(row=sliderposshift+7, column=0, padx=1, pady=1)
RecordButton = Button(gui, text='Record',command = gui_handler, bg='red')
RecordButton.grid(row=sliderposshift+7, column=0, padx=1, pady=1)
QuitButton = Button(gui, text="Quit",command = quit_handle, activebackground='red').grid(row=sliderposshift+8, column=0, padx=1, pady=1)

#Loop the code
root.mainloop()