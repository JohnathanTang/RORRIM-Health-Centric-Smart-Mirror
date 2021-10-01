import serial
import RPi.GPIO as GPIO
import time
import csv
import pandas as pd
import os 

import asyncio
# SER=serial.Serial("/dev/ttyACM0",9600)  #change ACM number as found from ls /dev/tty/ACM*
# SER.baudrate=9600

MAX_ROW = 30

class Arduino(object):
    def __init__(self):
        self.setup()

    def setup(self):
        #TODO: change ACM number as found from ls /dev/tty/ACM*

        self.ser=serial.Serial("/dev/ttyACM0",9600)
        self.ser.baudrate=9600
        self.ser.flush()

    async def get_response(self, fut):
        
        while self.ser.in_waiting < 0: #going to give error for now
            await asyncio.sleep(self.check_delay)
        
        #there is a response
        response = ""
        try:
            response = self.ser.readline().decode().rstrip()

        except(UnicodeDecodeError):
            print(response)
        
        if " " in response:
            fut.set_result(response.split())
            return response.split()
        
        #print(float(response))
        fut.set_result(float(response))
        return float(response)
    
    def get_ambTempC(self):
        self.ser.write(b'0')
       
    def get_objTempC(self):
        self.ser.write(b'1')
       
    def get_ambTempF(self):
        self.ser.write(b'2')
       
    def get_objTempF(self):
        self.ser.write(b'3')
    
    def get_spo2(self):
        self.ser.write(b'4')
        
    def get_spo2objtempF(self):
        self.ser.write(b'5')
        
    def write_file(self,user_id, spo2 = None, temp = None ):
        file_path = 'user_data/user'+str(user_id)+'/spo2_temp.csv'
        date = time.strftime("%m-%d-%y_%H:%M:%S", time.localtime())
        
        if not os.path.isfile(file_path):
            
            with open(file_path,'a') as f:
                f.write("Date_Time, SPO2, Temperature")
                
        df = pd.read_csv(file_path)
        num_rows = len(df)
        
        if num_rows >= MAX_ROW:
            df =  df.drop([0])
        
        df.loc[num_rows] = [date, spo2, temp]
        
        df.to_csv(file_path, index = False)


            
            