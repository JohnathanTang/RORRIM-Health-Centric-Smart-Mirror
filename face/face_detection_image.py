import cv2

# default cascade provided by openCV
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# take in image (currently for testing purposes)
img = cv2.imread(input("Enter name of image: "))

# facial detection needs to convert image to grayscale first, then does edge detection
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

## shows grayscale
#cv2.imshow('gray', gray)
#cv2.waitKey()

## edge detection
#edge = cv2.Canny(gray,100,200)
#cv2.imshow('edge', edge)
#cv2.waitKey()

# detects face
faces = face_cascade.detectMultiScale(gray, 1.1, 4)

# draws rectangle around face(s)
for (x, y, w, h) in faces:
  cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

# display output in new window
cv2.imshow('img', img)
cv2.waitKey()
