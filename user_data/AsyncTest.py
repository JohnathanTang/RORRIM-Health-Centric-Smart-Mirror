import asyncio
import datetime
import serial

some_var = False

ARDUINO_CHECK_UPDATE = 1
class RPI_SIM():
    def __init__(self):
        print("Class created")
        self.check_delay = ARDUINO_CHECK_UPDATE
        self.global_var = -1
        
        self.ser=serial.Serial("/dev/ttyACM0",9600)
        self.ser.baudrate=9600
        self.ser.flush()

    def start_job(self, job_encoding):
        self.arduino_get_spo2objTempF(job_encoding)
        self.loop = asyncio.get_event_loop()
        print("loop object: ", self.loop)
        future = asyncio.ensure_future(self.get_response())
        #print(future)
        #future = asyncio.ensure_future(self.get_test)
        result = self.loop.run_until_complete(future) #run future task until complete
        #print(result)
        return result
    
    def arduino_get_spo2objTempF(self, job_encoding):
        self.ser.write(b'5')
        print("Encoding: ", job_encoding)
        
    async def get_response(self):
        print("I am running the function")
        while self.ser.in_waiting < 0: #going to give error for now
            await asyncio.sleep(self.check_delay)
        
        #there is a response
        response = ""
        try:
            response = self.ser.readline().decode().rstrip()

        except(UnicodeDecodeError):
            print(response)
        
        if " " in response:
            return response.split()
        
        #print(float(response))
        return float(response)

    async def get_test(self):
        print("I am running the function")
        while self.get_global() < 0: #going to give error for now
            await asyncio.sleep(self.check_delay)
            print("Get test stalling")
        
        #there is a response/ do I need to await for future 
        response = ""
        try:
            response = self.get_global()  
        except(UnicodeDecodeError):
            print(response)
        
        print(response)
        
        return response
    
    def get_global(self):
        return self.global_var