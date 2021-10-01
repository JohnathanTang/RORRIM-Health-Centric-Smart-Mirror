import face_recognition
import cv2
import os
import io
import picamera
#from google.colab.patches import cv2_imshow

#import Pi Camera library
from picamera import PiCamera
from time import sleep
from skimage.transform import rotate

import imageio
import numpy as np

# #initialize pi camera
# camera = PiCamera()
# 
# #rotate camera view 180, change back to 0 for default orientation
# camera.rotation = 180

KNOWN_DIR = "face/known_faces"

def resize_img(img):
	(h, w) = img.shape[:2]
	width = 500
	ratio = width / float(w)
	height = int(h * ratio)
	return cv2.resize(img, (width, height))

def read_img(path):
	img = cv2.imread(path)
	return resize_img(img)

def reload_BGR(img):
	return resize_img(rotate(img, angle=int(0)))

def save_img(name, img):
	img_uint8 = img.astype(np.uint8)
	imageio.imsave(name, img_uint8)

def rotate_image(img, degree):
	r1 = rotate(img, angle=(int(degree)))
	neg = int(degree) * -1
	r2 = rotate(img, angle=(neg))
	
	r1 = resize_img(r1)
	r2 = resize_img(r2)
	
	save_img('temp1.jpg', r1)
	save_img('temp2.jpg', r2)
	
	temp1 = read_img('temp1.jpg')
	temp2 = read_img('temp2.jpg')

	r1 = reload_BGR(temp1)
	r2 = reload_BGR(temp2)

	save_img('temp1.jpg', r1)
	save_img('temp2.jpg', r2)

	r1 = read_img('temp1.jpg')
	r2 = read_img('temp2.jpg')
	
	if os.path.exists('temp1.jpg'):
		os.remove('temp1.jpg')

	if os.path.exists('temp2.jpg'):
		os.remove('temp2.jpg')
	
    # return tuple
	return resize_img(r1), resize_img(r2);

# captures image, returns openCV image object
def capture_to_cv():
    # create in-memory stream
    stream = io.BytesIO()
    
    with picamera.PiCamera() as camera:
        camera.rotation = 180
        camera.start_preview()
        sleep(2)
        camera.capture(stream, format='jpeg')
    
    # construct numpy array from stream
    data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
    
    # decode stream data into CV2 image object
    image = cv2.imdecode(data, 1)
    
    return resize_img(image)

class FR():
    def __init__(self):
        self.__known_encodings = []
        self.__known_names = []
        self.__known_dir = KNOWN_DIR
        self.__tolerance = 0.55
    
    # checks if cache exists
    def check_cache(self):
        known_list = []
        if os.path.exists('face/cache.txt'):
            with open('face/cache.txt') as f:
                content = f.readlines()
            content = [x.strip() for x in content]

            for file in os.listdir(self.__known_dir):
                known_list.append(file.split('.')[0])
            # checks to make sure cache is equal to the known_faces directory. if same, load. if not, rebuild
            if (len(content)==len(known_list)) and all (content.count(i)==known_list.count(i) for i in content):
                self.__load_encodings()
            else:
                self.__update_known_encodings()
        else:
            self.__update_known_encodings()
        #print("Done w cache")
            
    # loads known encodings from cache
    def __load_encodings(self):
        temp = ()
        with open('face/known_encodings.txt') as f:
            # splits text into encoding tuples
            for line in f:
                line = line.strip()
                if '[' in line:
                    line = line.replace('[','')
                curr = line.split(' ')
                for x in curr:
                    if ']' in x:
                        x = x.replace(']', '')
                        temp = temp + (float(x),)
                        self.__known_encodings.append(temp)
                        temp = ()
                    elif x.strip() == "":
                        pass
                    else:
                        temp = temp + (float(x), )
        
        with open('face/cache.txt') as f:
            for line in f:
                self.__known_names.append(line.strip())

    # update known_encodings
    def __update_known_encodings(self):
        for file in os.listdir(self.__known_dir):
            img = read_img(self.__known_dir + '/' + file)
            img_enc = face_recognition.face_encodings(img)[0]
            self.__known_encodings.append(img_enc)
            self.__known_names.append(file.split('.')[0])
            
            #data_augment_img = FR_IMAGE(img)
            #r1, r2 = data_augment_img.rotate_image(30)
            r1, r2 = rotate_image(img, 30)

            r1_enc = face_recognition.face_encodings(r1)
            self.__append_encodings(r1_enc, self.__known_encodings, self.__known_names, file)
            
            r2_enc = face_recognition.face_encodings(r2)
            self.__append_encodings(r1_enc, self.__known_encodings, self.__known_names, file)
            
            x1, x2 = rotate_image(img, 10)
            #x1, x2 = data_augment_img.rotate_image(10)
            
            x1_enc = face_recognition.face_encodings(x1)
            self.__append_encodings(x1_enc, self.__known_encodings, self.__known_names, file)
            
            x2_enc = face_recognition.face_encodings(x2)
            self.__append_encodings(x2_enc, self.__known_encodings, self.__known_names, file)
        
        # checks for no duplicates in cache
        no_duplicates = []
        for i in self.__known_names:
            if i not in no_duplicates:
                no_duplicates.append(i)

        f = open('face/cache.txt', 'w')
        for elem in no_duplicates:
            f.write(elem + '\n')
        f.close()

        f = open('face/known_encodings.txt', 'w')
        for elem in self.__known_encodings:
            f.write(str(elem) + '\n')
        f.close()

    # appends the encoding into known_encodings, appends file name into known_names
    def __append_encodings(self, enc, known_encodings, known_names, file):
        if len(enc) > 0:
            known_encodings.append(enc[0])
            known_names.append(file.split('.')[0])
    
    # compare face encodings
    def compare_encodings(self):
        pass
    
    # get captured image encoding
    # return boolean, id_associated (string)
    def __process_image(self, new_user_bool):
        retake_counter = 0
        
        # retake whenever you have 1 good face, more than 1 matches to known encodings
        while(retake_counter < 3):
            img = capture_to_cv()
            #print(type(img))
            img_enc = face_recognition.face_encodings(img, face_recognition.face_locations(img), 2)
            
            ## CHECK FOR 1 FACE ONLY
            # checks to make sure there's only 1 encoding total (sees 1 good face)
            if len(img_enc) > 1:
                # return something to say redo capture
                print("TOO MANY FACES")
                raise Exception('Identified multiple faces. Please try again.')
                
            elif len(img_enc) == 0:
                # return something to say no good faces
                print("NO FACES FOUND")
                raise Exception('Unable to identify face. Please try again.')
                
            elif len(img_enc) == 1:
            
                ## CHECK FOR MATCHING ENCODINGS
                # results is a boolean list of known_faces. if the img_encoding has a face with high confidence, then it will be true
                results = face_recognition.compare_faces(self.__known_encodings, img_enc[0], self.__tolerance)
                
                id_associated = []
                for i in range(len(results)):
                    if results[i]:
                        id_associated.append(self.__known_names[i])
                        
                
                if len(id_associated) == 1:
                    # successful identification
                    # return boolean: no need to make new user. return int: name
                    return False, id_associated[0]
                elif len(id_associated) == 0:
                    # doesnt match any in system
                    #s = input ("ARE YOU A NEW USER??? (yes/no)")
                    if new_user_bool:
                        cwd = os.getcwd()
                        os.chdir(self.__known_dir)
                        cv2.imwrite( str(len(results)+1) + ".jpg" , img)
                        os.chdir(cwd)
                        return True, len(results) + 1
                    
                        
                    # throw exception
                
                #compare_encodings()
            
            retake_counter += 1
        
        if retake_counter == 3:
            raise Exception('Could not identify face. Please try again.')
        
    
    def recognize_face(self,new_user_bool):
        self.check_cache()
        bool, id = self.__process_image(new_user_bool)
        return bool, id

# END OF FR CLASS

if __name__ == "__main__":
    print ("COMPILED")
    f = FR()
    try:
        bool, id = f.recognize_face(False)
        print(id)
    except Exception as e:
        raise e
    exit()

# known_encodings = []
# known_names = []
# known_dir = "known_faces"

# def take_picture(): 
	# #start camera preivew
	# camera.start_preview()
	# #sleep for 5 seconds before capturing image
	# sleep(5)
	# #capture picture and store to Desktop
	# camera.capture('known_faces/sampleimage.jpg')
	# #close preview window

# def append_encodings(enc, known_encodings, known_names, file):
	# if len(enc) > 0:
		# known_encodings.append(enc[0])
		# known_names.append(file.split('.')[0])

# def get_known_encodings():
	# for file in os.listdir(known_dir):
		# img = read_img(known_dir + '/' + file)
		# img_enc = face_recognition.face_encodings(img)[0]
		# known_encodings.append(img_enc)
		# known_names.append(file.split('.')[0])
	
		# r1, r2 = rotate_image(img, 30)

		# r1_enc = face_recognition.face_encodings(r1)
		# append_encodings(r1_enc, known_encodings, known_names, file)
		
		# r2_enc = face_recognition.face_encodings(r2)
		# append_encodings(r1_enc, known_encodings, known_names, file)
		
		# x1, x2 = rotate_image(img, 10)
		
		# x1_enc = face_recognition.face_encodings(x1)
		# append_encodings(x1_enc, known_encodings, known_names, file)
		
		# x2_enc = face_recognition.face_encodings(x2)
		# append_encodings(x2_enc, known_encodings, known_names, file)

	# no_duplicates = []
	# for i in known_names:
		# if i not in no_duplicates:
			# no_duplicates.append(i)

	# f = open('cache.txt', 'w')
	# for elem in no_duplicates:
		# f.write(elem + '\n')
	# f.close()

	# f = open('known_encodings.txt', 'w')
	# for elem in known_encodings:
		# f.write(str(elem) + '\n')
	# f.close()
	
# def load_encodings():
	# temp = ()
	# with open('known_encodings.txt') as f:
		# for line in f:
			# line = line.strip()
			# if '[' in line:
				# line = line.replace('[','')
			# curr = line.split(' ')
			# for x in curr:
				# if ']' in x:
					# x = x.replace(']', '')
					# temp = temp + (float(x),)
					# known_encodings.append(temp)
					# temp = ()
				# elif x.strip() == "":
					# pass
				# else:
					# temp = temp + (float(x), )
	
	# with open('cache.txt') as f:
		# for line in f:
			# known_names.append(line.strip())

# take sample picture
#take_picture()
#camera.close()

# if os.path.exists('cache.txt'):
	# with open('cache.txt') as f:
		# content = f.readlines()
	# content = [x.strip() for x in content]

	# known_list = []
	# for file in os.listdir(known_dir):
		# known_list.append(file.split('.')[0])
	# if (len(content)==len(known_list)) and all (content.count(i)==known_list.count(i) for i in content):
		# load_encodings()
	# else:
		# get_known_encodings()
# else:
	# get_known_encodings()	

# known_faces_in_frame = []
# unknown_dir = 'unknown_faces'
# for file in os.listdir(unknown_dir):
	# print("Processing", file)
	
	# img = read_img(unknown_dir + "/" +file)

	# all_locations = face_recognition.face_locations(img)

	# img_enc = face_recognition.face_encodings(img, all_locations, 2)
	
	# print("# of faces found: " + str(len(img_enc)))
	# # iterates over all faces in the image
	# for j in range(len(img_enc)):
		# # results is a boolean list of known_faces. if the img_encoding has a face with high confidence, then it will be true
		# results = face_recognition.compare_faces(known_encodings, img_enc[j], 0.55)
		# #print("face #: " + str(j))
		# #print(results)
		# #print(face_recognition.face_distance(known_encodings, img_enc))
		
		# # draws rectangle around known faces
		# for i in range(len(results)):
			# #print("comparing to known_faces: " + str(i))
			# #print(str(face_recognition.face_locations(img)))
			# if results[i]:
				# #print(str(face_recognition.face_locations(img)[0]))
				# (top, right, bottom, left) = all_locations[j]
				
				# cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255) , 2)

				# name = known_names[i]
				# known_faces_in_frame.append(name)
				# #print("found: " + name)
				# cv2.putText(img, name, (left+2, bottom+20), cv2.FONT_HERSHEY_PLAIN, 0.8, (255, 255, 255), 1)
				
				# # display after each face identified
				# #cv2.imshow('img', img)
				# #cv2.waitKey()
		
	# # displays final image with rectangles and known faces			
	# cv2.imshow('img', img)
	# cv2.waitKey()

# # assume that you pass in only 1 image to get encoding, to compare to known_faces folder
# if len(known_faces_in_frame) > 1:
	# print("TOO MANY FACES")
	# # return something to say redo img

# elif len(known_faces_in_frame) == 1:
	# print("PERFECT 1 FACE")
	# # return boolean: no need to make new user. return int: int(known_faces_in_frame[0])

# else:
	# print("NO FACES. UGLY")
	# # return something that there's no faces

