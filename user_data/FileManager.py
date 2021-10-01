from user_data import Firebase, User
import os
import csv
#FOR FITBIT DATA 
#get sleep log ->push to Firebase -> make sure theres  a weeks worth on the Pi -> delete if > MAX 

class FileManager():
    def __init__(self,database):
        self.database = database
        
    def create_fitbit_logs(self, user):
        if user.fbit is None:
            return
        
        heart_log = user.fbit.get_heart_log()
        sleep_log = user.fbit.get_sleep_log()
        user.fbit.append_kaggle()
        
        self.database.push_file(user.id,Firebase.HEART,heart_log)
        self.database.push_file(user.id,Firebase.SLEEP,sleep_log)
        
        
    def delete_files(self,user_id):
        list_of_files = os.listdir('user_data/user'+str(user_id)+'/Heart')
        full_path = ['user_data/user'+str(user_id)+'/Heart/{0}'.format(x) for x in list_of_files]

        if len(list_of_files) > 7:
            oldest_file = min(full_path, key=os.path.getctime)
            #print(oldest_file)
            os.remove(oldest_file)
        
        list_of_files = os.listdir('user_data/user'+str(user_id)+'/Sleep')
        full_path = ['user_data/user'+str(user_id)+'/Sleep/{0}'.format(x) for x in list_of_files]

        if len(list_of_files) > 7:
            oldest_file = min(full_path, key=os.path.getctime)
            #print(oldest_file)
            os.remove(oldest_file)
            
    def update_fitbit_logs(self,user):
        
        self.create_fitbit_logs(user)
        self.delete_files(user.id)
        
    def get_last_readings(self,user_id):
        
        file = "user_data/user"+str(user_id)+"/spo2_temp.csv"
        with open(file,'r') as f:
            last_line=f.readlines()[-1].strip()
            return last_line.split(',')
        
        
        