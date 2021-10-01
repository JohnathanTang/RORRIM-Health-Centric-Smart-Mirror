#import Pi Camera library 
from picamera import PiCamera
from time import sleep

#initialize pi camera
camera = PiCamera()

#rotate camera view 180, change back to 0 for default orientation 
camera.rotation = 180 

#start camera preivew
camera.start_preview()
#sleep for 5 seconds before capturing image
sleep(5)
#capture picture and store to Desktop
camera.capture('/home/pi/Desktop/image.jpg')
#close preview window
camera.close()
