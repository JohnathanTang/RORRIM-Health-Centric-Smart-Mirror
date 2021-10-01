#!/usr/bin/env python3
import RPi.GPIO as GPIO
import threading
import atexit
import time 

class PIR_Sensor():
    def __init__(self):
        self.init_time = 60 #seconds
        self.__sensor_pin = 22
        self.__valid = threading.Event()
        self.__setup()

        threading.Thread(target=lambda: self.__start_up(self.init_time)).start()

    def __setup(self):
        #set up motion sensor
        GPIO.setmode(GPIO.BOARD)        # use PHYSICAL GPIO Numbering
        GPIO.setup(self.__sensor_pin, GPIO.IN)
        pass

    def __start_up(self, delay):
        print("Start up function called")
        
        finish_time = time.time() + delay 
        time.sleep(max(0, finish_time - time.time()))
        print("Setting on Valid Bit")
        self.__set_valid()

        #thread kills itself
		
    def __set_valid(self):
        self.__valid.set()

    def is_valid(self):
        return self.__valid.is_set()

    def is_on(self):
        return True if (GPIO.input(self.__sensor_pin) == GPIO.HIGH) else False

    def motion_detected(self):
        return self.is_valid() and self.is_on()

    @atexit.register
    def __cleanup():
        print("Cleaning up")
        GPIO.cleanup()

if __name__ == "__main__":
    print ('Program is starting...')
    print ('Sensor will be inactive for 1 minute')
    
    p = PIR_Sensor()
    time.sleep(59)
    while True:
        print("Valid: ", p.is_valid())
        print("Is On: ", p.is_on())
        print("Motion Detected: ", p.motion_detected())
        time.sleep(0.5)
