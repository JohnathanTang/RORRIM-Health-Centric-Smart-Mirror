# home_screen.py

# To run:
# > pip install requests

from tkinter import *
from tkinter import messagebox
import time
import threading
import requests
import traceback
from display.AcceptScreen import AcceptScreen
from user_data import user_info
from user_data.User import *
from user_data import fitbit
from user_data import arduino
from user_data import Firebase
from user_data import FileManager
from user_data import KNN
from face.facial_identification import *
#from face.PIR import *

from display.keyboard import Keyboard

import asyncio
import threading
from multiprocessing import Process, Queue
import random

# TODO update when pull facial_recog
# import PIR

CURR_USER = get_user(1)

# OpenWeatherMap
OWM_API = "https://api.openweathermap.org/data/2.5/onecall"
OWM_PARAMS = {
    "lat": "33.6695",
    "lon": "-117.8231",
    "exclude": "minutely,hourly,alerts",
    "units": "imperial",
    "appid": user_info.OWM_KEY
    }

WEATHER_ICON = {
    "01d" : "sun.png", "01n" : "sun.png",
    "02d" : "sun_cloud.png", "02n" : "sun_cloud.png",
    "03d" : "clouds.png", "03n" : "clouds.png", "04d" : "clouds.png", "04n" : "clouds.png", 
    "09d" : "rain.png", "09n" : "rain.png",
    "10d" : "sunshower.png", "10n" : "sunshower.png",
    "11d" : "thunder.png", "11n" : "thunder.png",
    "13d" : "snowflake.png", "13n" : "snowflake.png",
    "50d" : "fog.png", "50n" : "fog.png"
    }

FONT = {
    "heading" : "Trebuchet",
    "body" : "Bahnschrift"
    #Raleway, Ubuntu Light
    }

class AppTimer(object):
    """Timer to call given function repeatedly after given interval."""


    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class Application(Frame):
    """Opens the home screen of the smart mirror.
    
    Includes widgets for date, time, weather, and health (respiration, sleep, and body temperature).
    (Click the settings/gear icon to exit the Application)
    """

    def __init__(self, master=None):
        """Initializes outer frame and widgets for the Application."""
        # PIR.setup()

        # place frame (self) in window (take up full size)
        super().__init__(master, background="black", bd=20)
        self.master = master
        self.grid(row=0, column=0, sticky=NSEW)
        
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()

        # set up grid (3x3) in frame (take up full size)
        for x in range(3):
            Grid.rowconfigure(self, x, weight=1, uniform="row_third")
            Grid.columnconfigure(self, x, weight=1, uniform="col_third")

        # add a frame to each grid cell
        self.frame = [[Frame(self, bg="black") for m in range(3)] for n in range(3)]
        for i in range(3):
            for j in range(3):
                self.frame[i][j].grid(row=i, column=j, sticky=NSEW)

        # create timers for repeatedly updating widgets
        # datetime every 1 second
        # weather every 1 hour
        
        self.timer_dt = AppTimer(60, self.update_datetime)
        self.timer_w = AppTimer(3600, self.update_weather)
        self.timer_health = AppTimer(3600, self.update_health_stats)
        self.timer_fm = AppTimer(86400, self.update_fitbit_files)
        #self.timer_arduino = AppTimer(3, self.update_temp)
        
        
        
        #self.motion = PIR_Sensor()
        self.arduino = arduino.Arduino()
        self.Firebase = Firebase.Database() 
        #self.timer_motion = AppTimer(5, self.lock)
        self.FileManager = FileManager.FileManager(self.Firebase)
        self.KNN_Model = KNN.KNN()
        
        self.FR= FR()
        self.process = Process(target=self.FR.check_cache)
        self.process.start()
        self.create_widgets()
        
        
    
    def create_widgets(self):
        self.add_datetime()
        self.add_weather()
        self.add_health_stats()

        # TODO hardcoded rn; finish functionality/return later
        self.keyboard_w = Toplevel(self.master)
        self.keyboard_w.title("Keyboard")
        w, h = 1000, 500
        x, y = (self.width/2 - w/2), (self.height - h - 30)
        self.keyboard_w.geometry("%dx%d+%d+%d" % (w, h, x, y))
        self.keyboard = Keyboard(self.keyboard_w)
        self.keyboard_w.withdraw()

        self.add_user = Button(self.frame[2][2], bg="black", fg="white", text="Add User",
                                command=self.input_user, relief=FLAT)
        self.add_user.config(font=(FONT["body"], 25))

        self.change_user = Button(self.frame[2][2], bg="black", fg="white", text="Change User",
                                command=self.switch_user, relief=FLAT)
        self.change_user.config(font=(FONT["body"], 25))
        
        self.sleep = Button(self.frame[2][2], bg="black", fg="white", text="Sleep",
                            command=self.hibernate, relief=FLAT)
        self.sleep.config(font=(FONT["body"], 25))

        self.quit = Button(self.frame[2][2], bg="black", fg="white", text="QUIT",
                            command=self.close, relief=FLAT)
        self.quit.config(font=(FONT["body"], 25))
        
        self.gear = PhotoImage(file = r"./display/icons/gear.png").subsample(10,10)
        
        
        self.settings = Button(self.frame[2][2], image=self.gear, bg="black",
                              command=self.show_options, relief=FLAT)
        self.settings.pack(side=BOTTOM, anchor=E)

        self.user_name = Label(self.frame[0][1], bg = "black", fg="white", text=CURR_USER.name)
        self.user_name.config(font=(FONT["body"], 30))
        self.user_name.pack(anchor=CENTER)
        
        self.scan = PhotoImage(file = r"./display/icons/scan.png").subsample(10,10)
        
        self.spo2temp_button = Button(self.frame[1][0], image=self.scan,bg="black", fg="white",
                            command=self.get_spo2temp, relief=FLAT)
        self.spo2temp_button.config(font=(FONT["body"], 30))
        self.spo2temp_button.pack(side=BOTTOM,anchor=W)
        
        self.rec = Label(self.frame[1][2], bg = "black", fg="white", text="")
        self.rec.config(font=(FONT["body"], 15),justify=LEFT)
        self.rec.pack(side=RIGHT,anchor=E)
        
        self.status = StringVar()
    
        self.status_msg = Label(self.frame[2][1], bg = "black", fg="white", textvariable=self.status)
        self.status_msg.config(font=(FONT["body"], 15))
        self.status_msg.pack(side=BOTTOM,anchor=S)

        
        
        
#     def lock(self):
#         print(self.motion.is_valid(), self.motion.motion_detected())
#         if self.motion.motion_detected():
#             try:
#                 bool, id = self.FR.recognize_face()
#                 self.user_name["text"] = "Hi " + str(id)
#             except Exception as e:
#                 traceback.print_exc()
    
    def show_options(self):
        self.settings.config(command=self.hide_options)

        self.quit.pack(side=BOTTOM, anchor=E)
        self.sleep.pack(side=BOTTOM, anchor=E)
        self.change_user.pack(side=BOTTOM, anchor=E)
        self.add_user.pack(side=BOTTOM, anchor=E)

    def hide_options(self):
        self.settings.config(command=self.show_options)

        self.add_user.pack_forget()
        self.change_user.pack_forget()
        self.sleep.pack_forget()
        self.quit.pack_forget()

    def input_user(self):
        self.hide_options()
        self.process.join()
        try:
            # User_id should be passed in as a parameter (should be given by facial recognition)
            new_user, user_id = self.FR.recognize_face(True)
            if not new_user: #Trying to add user but recognize 
                self.accept_w = Toplevel(self.master)
                self.accept_w.title("Change User")
                w, h = 550,200
                x, y = (self.width/2 - w/2), (self.height/2 - h/2 - 30)
                self.accept_w.geometry("%dx%d+%d+%d" % (w, h, x, y))
                user = get_user(user_id)
                msg = "We recognize your face.\nAre you "+user.name+"?"
                self.accept = AcceptScreen(self.accept_w,msg)
                self.accept_w.wait_window(self.accept_w)
                if not self.accept.result: #If not verified as existing user 
                    return #exit 
            else: #new user 
                self.keyboard.prompt = "Please enter your name:\n"
                self.keyboard.refresh()
                self.wait_variable(self.keyboard.is_open)
                name = self.keyboard.result

                self.keyboard.prompt = "Please enter your location (ex: Irvine,CA,US):\n"
                self.keyboard.refresh()
                self.wait_variable(self.keyboard.is_open)
                location = self.keyboard.result

                # add new user to json file
                add_new_user(user_id, name, location, FITBIT, fitbit.USER_ID, fitbit.ACCESS_TOKEN)
                self.process = Process(target=self.FR.check_cache)
                self.process.start()

            # get user from json file
            CURR_USER = get_user(user_id)

            OWM_PARAMS["lat"] = CURR_USER.lat
            OWM_PARAMS["lon"] = CURR_USER.lon
            self.location["text"] = CURR_USER.location

            #update name in middle; remove later
            self.user_name["text"] = CURR_USER.name

            self.timer_w.stop()
            self.update_weather()
            self.timer_w.start()

            self.timer_health.stop()
            if CURR_USER.fbit is None and CURR_USER.oura is None:
                self.heart_rate["text"] = ""
                self.steps["text"] = ""
                # unpack if have pictures...but need to repack
            else:
                self.update_health_stats()
                self.timer_health.start()
        except Exception as e:
                print(str(e))

    def switch_user(self):
        """
        Assumes user_id is passed from facial recognition
        Switch between users that are already in database
        """
        self.status_msg.pack_forget()
        # TODO: hardcode rn; get id for facial recognition
        self.hide_options()
        self.process.join()
        try:
            new_user, user_id = self.FR.recognize_face(False)
        
            if new_user:
                raise Exception('Detected new user while switching')
                    
            else:
                CURR_USER = get_user(user_id)

                OWM_PARAMS["lat"] = CURR_USER.lat
                OWM_PARAMS["lon"] = CURR_USER.lon
                self.location["text"] = CURR_USER.location

                #update name in middle; remove later
                self.user_name["text"] = CURR_USER.name

                self.timer_w.stop()
                self.update_weather()
                self.timer_w.start()

                self.timer_health.stop()
                if CURR_USER.fbit is None and CURR_USER.oura is None:
                    self.heart_rate["text"] = ""
                    self.steps["text"] = ""
                    # unpack if have pictures...but need to repack
                else:
                    self.update_health_stats()
                    self.timer_health.start()
        except Exception as e:
            self.status.set(str(e))
            self.status_msg.pack(side=BOTTOM,anchor=S)

    def start_timers(self):
        self.timer_dt.start()
        self.timer_w.start()
        self.timer_health.start()
        self.timer_fm.start()
        #self.timer_motion.start()

    def stop_timers(self):
        self.timer_dt.stop()
        self.timer_w.stop()
        self.timer_health.stop()
        self.timer_fm.stop()
        #self.timer_motion.stop()

    def hibernate(self):
        self.hide_options()
        self.stop_timers()

        self.sleep_w = Toplevel(self.master)
        self.sleep_w.wm_attributes("-fullscreen","true")
        sleep_frame = Frame(self.sleep_w, background="black", bd=20)
        sleep_frame.pack(side=TOP, expand=YES, fill=BOTH)

        wake_button = Button(sleep_frame, image=self.gear, bg="black",
                              command=self.wake, relief=FLAT)
        wake_button.pack(side=BOTTOM, anchor=E)

    def wake(self):
        self.sleep_w.destroy()
        self.start_timers()
        self.update_datetime()
        self.update_weather()
        self.update_health_stats()

    def close(self):
        # PIR.destroy()

        self.stop_timers()
        self.master.destroy()

    def add_datetime(self):        
        self.clock = Label(self.frame[0][0], bg="black", fg="white")
        self.clock.config(font=(FONT["body"], 60))
        self.clock.pack(side=TOP, anchor=NW)
        
        self.date = Label(self.frame[0][0], bg="black", fg="white")
        self.date.config(font=(FONT["body"], 30, "bold"))
        self.date.pack(side=TOP, anchor=NW)

        self.update_datetime()
        self.timer_dt.start()

    def update_datetime(self):
        self.clock["text"] = time.strftime("%I:%M %p", time.localtime())
        self.date["text"] = time.strftime("%a, %B %d", time.localtime())

    def add_weather(self):
        self.location = Label(self.frame[0][2], bg="black", fg="white")
        self.location.config(font=(FONT["body"], 30))
        self.location["text"] = CURR_USER.location
        self.location.pack(side=TOP, anchor=NE)

        self.outdoor_main = Frame(self.frame[0][2], bg="black")
        self.outdoor_main.pack(side=TOP, anchor=NE)

        self.outdoor_temp = Label(self.outdoor_main, bg="black", fg="white")
        self.outdoor_temp.config(font=(FONT["body"], 60))
        self.outdoor_temp.pack(side=RIGHT, anchor=SE)

        self.outdoor_icon = Label(self.outdoor_main, bg="black", fg="white")
        self.outdoor_icon.pack(side=RIGHT, anchor=NE)

        self.outdoor_desc = Label(self.frame[0][2], bg="black", fg="white")
        self.outdoor_desc.config(font=(FONT["body"], 25))
        self.outdoor_desc.pack(side=TOP, anchor=NE)

        self.update_weather()
        self.timer_w.start()

    def update_weather(self):
        j = requests.get(url=OWM_API, params=OWM_PARAMS).json()
        icon_id = j["current"]["weather"][0]["icon"]
        self.icon = PhotoImage(file = r"./display/icons/" + WEATHER_ICON[icon_id]).subsample(10,10)

        self.outdoor_temp["text"] = str(int(j["current"]["temp"])) + u"\N{DEGREE SIGN}" + "F"
        self.outdoor_desc["text"] = j["current"]["weather"][0]["description"]
        self.outdoor_icon["image"] = self.icon

    def add_health_stats(self):
        date_time,spo2,temp = self.FileManager.get_last_readings(CURR_USER.id)
        
        self.timestamp = Label(self.frame[2][0],bg="black",fg="white")
        self.timestamp.config(font=(FONT["body"],15))
        self.timestamp["text"] = "Last Updated: "+date_time
        self.timestamp.pack(side=BOTTOM,anchor=W)
        
        # TODO: update internal temp
        self.therm = PhotoImage(file= r"./display/icons/thermometer.png").subsample(20,20)
        self.internal_temp = Label(self.frame[2][0],image=self.therm,compound=LEFT,bg="black", fg="white")
        self.internal_temp.config(font=(FONT["body"], 30))
        
        self.internal_temp["text"] = " "+temp+u"\N{DEGREE SIGN}"+ "F"
        self.internal_temp.pack(side=BOTTOM, anchor=W)
        

        # TODO: sleep cycles
        # self.sleep_info = Label(self.frame[2][0], bg="black", fg="white")
        # self.sleep_info.config(font=(FONT["body"], 30))
        # self.sleep_info["text"] = "Sleep Info"
        # self.sleep_info.pack(side=BOTTOM, anchor=W)

        # TODO: respiration
        self.blood_o2 = PhotoImage(file= r"./display/icons/blood_o2.png").subsample(20,20)
        self.respiration = Label(self.frame[2][0], image=self.blood_o2,compound=LEFT,bg="black", fg="white")
        self.respiration.config(font=(FONT["body"], 30))
        self.respiration["text"] = " "+spo2+"%"# "Respiration"
        self.respiration.pack(side=BOTTOM, anchor=W)
        self.heart = PhotoImage(file= r"./display/icons/heartrate.png").subsample(20,20)
        self.feet = PhotoImage(file= r"./display/icons/footprints.png").subsample(20,20)
        self.heart_rate = Label(self.frame[2][0],image=self.heart, compound=LEFT,bg="black", fg="white")
        self.heart_rate.config(font=(FONT["body"], 30))
        self.heart_rate.pack(side=BOTTOM, anchor=W)
        
        

        self.steps = Label(self.frame[2][0],image=self.feet,compound=LEFT, bg="black", fg="white")
        self.steps.config(font=(FONT["body"], 30))
        self.steps.pack(side=BOTTOM, anchor=W)
        


        self.update_health_stats()
        self.timer_health.start()
    

    def update_health_stats(self):
        if CURR_USER.fbit is not None:
            self.heart_rate["text"] = " "+str(CURR_USER.get_heart_rate()) + " BPM"
            self.steps["text"] = " "+str(CURR_USER.get_steps())+ " steps"


    def get_spo2temp(self):
        # send signal to arduino that we want to get obj temp in F
        self.arduino.get_spo2objtempF()
        self.status.set("Waiting for response.")
        self.status_msg.pack(side=BOTTOM,anchor=S)
        loop = asyncio.get_event_loop()
        threading.Thread(target=self._asyncio_thread, args=(loop,)).start()
        
        #self.timer_arduino.start()  # start timer for 5 seconds
        #self.update_spo2temp()
  
    def _asyncio_thread(self,loop):
        loop.run_until_complete(self.async_update_spo2temp())
        
    def show_accept_screen(self,temp,spo2):
        
        self.accept_w = Toplevel(self.master)
        self.accept_w.title("Accept Readings")
        w, h = 550,200
        x, y = 685,410 #(self.width/2 - w/2), (self.height/2 - h/2 - 30)
        screen_string = str(self.width)+" "+str(self.height)+" "+str(x)+" "+str(y)
        self.accept_w.geometry("%dx%d+%d+%d" % (w, h, x, y))
        #print("%dx%d+%d+%d" % (w, h, x, y))
        msg = "Do you accept the following readings: \nTemp: " +temp+ u"\N{DEGREE SIGN}" + "F\nSPO2: "+spo2 + "%\n"+ \
        "Normal temperature readings are between 97 to 99"+u"\N{DEGREE SIGN}" + "F"+\
        "\nNormal SPO2 readings are between 95 to 100%"
        self.accept = AcceptScreen(self.accept_w,msg)
        self.accept_w.wait_window(self.accept_w)
        if self.accept.result:
            self.respiration["text"] = " "+spo2 + "%"
            self.internal_temp["text"] = " "+temp + u"\N{DEGREE SIGN}" + "F"
            self.arduino.write_file(CURR_USER.id,spo2, temp)
            steps=CURR_USER.get_steps()
            heart_rate=CURR_USER.get_heart_rate()
            self.Firebase.push_data(CURR_USER.id,temp=temp, spo2=spo2,steps=steps,heart_rate=heart_rate)
            prediction=self.KNN_Model.predict(float(temp), int(spo2), int(heart_rate))
            self.update_rec(prediction)
            date = time.strftime('%m-%d-%y', time.localtime())
            curtime = time.strftime('%H:%M:%S', time.localtime())
            self.timestamp["text"] = "Last Updated: "+date+"_"+curtime
        
        self.status_msg.pack_forget()
        #self.status.set("")
     
        
    async def async_update_spo2temp(self):
        
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        task1 = asyncio.create_task(self.arduino.get_response(fut))
        await task1
        await fut
        #print(await fut)
        
        user_accept = False
        response = fut.result()
        temp = str(format(float(response[1]),".2f"))
        spo2 = str(int(response[0]))
#         temp = str(99 - random.randrange(30)/10)
#         spo2 = str(100 - random.randrange(5))
        self.show_accept_screen(temp,spo2)
        #user_accept = self.show_accept_screen(msg)
        

            
    def update_rec(self,prediction):
        msg = ""
        if (prediction == 0):
            msg = "You seem relaxed"
        elif (prediction == 1):
            msg = ("You seem physically stressed\n"
                   "We suggest that you:\n"
                   "- Stay hydrated\n"
                   "- Remember to stretch\n"
                   "- Take deep breaths")         
        elif(prediction == 2):
            msg = ("You seem emotionally stressed\n"
                   "We suggest that you:\n"
                   "- Read a book\n"
                   "- Take a walk or practice yoga\n"
                   "- Listen to some music\n"
                   "- Meditate")
        elif(prediction == 3):
            msg = ("You seem cognitively stressed\n"
                   "We suggest that you:\n"
                   "- Reduce your caffeine intake\n"
                   "- Chew gum\n"
                   "- Avoid procrastination\n"
                   "- Take frequent breaks and exercise")
        self.rec["text"] = msg
        
    def update_fitbit_files(self):      
        self.FileManager.update_fitbit_logs(CURR_USER)
        
                                                       
if __name__=="__main__":
    # set up window in fullscreen
    root = Tk()
#     root.wm_attributes("-fullscreen","true")
    
    Grid.rowconfigure(root, 0, weight=1)
    Grid.columnconfigure(root, 0, weight=1)

    app = Application(master=root)
    app.mainloop()
