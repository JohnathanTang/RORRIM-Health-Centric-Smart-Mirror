import cv2
from picamera import PiCamera
from time import sleep

cam = cv2.VideoCapture(0)


#cv2.namedWindow("EECS 159 Senior Design Test")

img_counter = 0

while True:
    success, frame = cam.read()
    if not success:
        print("failed to grab frame")
        break
    cv2.imshow("video", frame)

    k = cv2.waitKey(1)  ################################################# HERE WAITKEY PRESS KEY TO TAKE PIC 
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()

#cv2.destroyAllWindows()