import face_recognition
import cv2
import os
from picamera import PiCamera
import time
from PIR import *
#from google.colab.patches import cv2_imshow

camera = PiCamera()  #create single-use camera
camera.rotation = 180 #rotate camera view (0 = default)
CAMERA_WAIT = 5 #seconds before capture

known_encodings = []
known_names = []
known_dir = "known_faces"
unknown_dir = 'unknown_faces'
DEFAULT_PIC_NAME = "sampleimage.jpg"

PIR = PIR_Sensor()

class Rectangle:
	def __init__(self, top, right, bottom, left):
		self.top = top
		self.right = right
		self.bottom = bottom
		self.left = left

def read_img(path):
	img = cv2.imread(path)
	(h, w) = img.shape[:2]
	width = 500
	ratio = width/ float(w)
	height = int(h * ratio)
	return cv2.resize(img, (width, height))

def get_rel_path_string(name=None):
	if name is None:
		return known_dir + "/" + DEFAULT_PIC_NAME
	
	return known_dir + "/" + name

def update_known_image(file):
	img = read_img(known_dir + '/' + file)
	img_enc = face_recognition.face_encodings(img)[0]
	known_encodings.append(img_enc)
	known_names.append(file.split('.')[0]) # ADD LIST OF NAMES + FILE ORGANIZATION


def setup():
	#retrieve encodings and pictures
	for file in os.listdir(known_dir):
		update_known_image(file)

def destroy():
	#camera.close() # need to make camera None - so we can open close camera, to later destory
	pass

def take_picture(name=None):
	#take pictures for new users only
	cwd = os.getcwd()
	rel_save_path = get_rel_path_string(name)

	camera.start_preview()
	sleep(CAMERA_WAIT)
	camera.capture(rel_save_path)
	camera.close()
	
	if name is None: #keyboard input, make separate function
		os.chdir(known_dir)
		name = input("Type your name here: ") #create new id
		old_path = DEFAULT_PIC_NAME
		new_path = name + ".jpg"
		os.rename(old_path, new_path)
		os.chdir(cwd)
	
	#append to known encodings
	update_known_image(name + ".jpg")
	return name

# takes picture if motion is detected
def motion_triggered_camera():
	count = 0
	print("Start")
	while(True):
		if PIR.motion_detected():		# if detect motion, take pic, then sleep for 3 seconds
			print("Motion is detected!!! sleep for 3")
			#take_picture()
			count = 0
			time.sleep(3)
		else:
			count = count + 1

		if count == 100:	# if no pic for 1 second, sleep 3 seconds
			print("NO motion detected!!! sleep for 3")
			count = 0
			time.sleep(3)
		else:
			time.sleep(.1)	# detect motion every .1 sec, for 1 second	

def main():
	take_picture()

	for file in os.listdir(unknown_dir): #has problems with pngs -- list dir has issues 
		print("Processing", file)
		img = read_img(unknown_dir + "/" +file) 

		all_locations = face_recognition.face_locations(img)

		img_enc = face_recognition.face_encodings(img, all_locations, 2)

		#print(results)
		#print(face_recognition.face_distance(known_encodings, img_enc))

		for j in range(len(img_enc)):
			results = face_recognition.compare_faces(known_encodings, img_enc[j], 0.55)
			#print("face #: " + str(j))
			
			for i in range(len(results)):
				if results[i]:
					(top, right, bottom, left) = all_locations[j]
					name = known_names[i]
					
					cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255) , 2)
					cv2.putText(img, name, (left+2, bottom+20), cv2.FONT_HERSHEY_PLAIN, 0.8, (255, 255, 255), 1)
					#cv2.imshow('img', img)
					#cv2.waitKey()
		cv2.imshow('img', img)
		cv2.waitKey()
	#needs to return and concat all the rectangles(class) and return + name 
	

if __name__ == "__main__":
	setup()
	motion_triggered_camera()
	#main()
