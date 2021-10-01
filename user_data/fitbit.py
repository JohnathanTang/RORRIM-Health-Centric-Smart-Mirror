
import requests
import time
import json
import pandas as pd
from datetime import date
import csv
import os


#user specific access token and ID
USER_ID = '8WYYBH'
ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMkMyNVMiLCJzdWIiOiI4V1lZQkgiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcmFjdCBybG9jIHJ3ZWkgcmhyIHJudXQgcnBybyByc2xlIiwiZXhwIjoxNjM1ODc1MDAxLCJpYXQiOjE2MDQ1MTI0MzJ9.6CTS1yjhZVc2eqkKP70sRJE-ATmNo3QmTtGYR_JMPEk'


class Fitbit(object):
    def __init__(self, user_id, fitbit_id, access_token):
        self.user = user_id
        self.id = fitbit_id
        self.token = access_token

    #GET request for heart rate
    def get_heart_rate(self):
        data_type = 'heart'
        data_request = requests.get('https://api.fitbit.com/1/user/'+self.id+'/activities/'+data_type+'/date/today/1d/1sec.json', headers = {'Authorization': 'Bearer '+self.token})
        #print(data_request.json())
        data = data_request.json()['activities-heart-intraday']['dataset']
        time_list = []
        data_list = []
        for record in data:
            #print(record['time'],record['value'])
            data_list.append(record['value'])
            time_list.append(record['time'])
        #Store latest heart rate reading
        data_received = data_list[-1]
        #Return data
        #print(data_received)
        return data_received

    def get_heart_log(self):
        today = date.today()
        data_request = requests.get('https://api.fitbit.com/1/user/'+self.id+'/activities/heart/date/today/1d/1sec.json', headers = {'Authorization': 'Bearer '+self.token})
        data = data_request.json()['activities-heart-intraday']['dataset']
        path = 'user_data/user'+str(self.user)+'/Heart/'+str(today)+'.csv'
        heart_data = open(path, 'w+')
        csvwriter = csv.writer(heart_data)
        count = 0
        for i in data:
            if count == 0:
                    header = i.keys()
                    csvwriter.writerow(header)
                    count += 1
            csvwriter.writerow(i.values())
        heart_data.close()
        return str(today)+'.csv'


    def get_steps(self):
        data_type = 'steps'
        data_request = requests.get('https://api.fitbit.com/1/user/'+self.id+'/activities/'+data_type+'/date/today/today.json', headers = {'Authorization': 'Bearer '+self.token})
        data = data_request.json()['activities-steps']
        data_list = []
        for record in data:
            data_list.append(record['value'])
        data_received = data_list[-1]
        #print(data_received)
        return data_received

    def get_profile_picture(self):
        data_request = requests.get('https://api.fitbit.com/1/user/'+self.id+'/profile.json', headers = {'Authorization': 'Bearer '+self.token})
        # profile = data_request.json()
        # print(profile)
        #print(data_request.json())
        profile_picture = data_request.json()['user']['avatar640']

    def get_sleep_log(self):
        today = date.today()
        date_to_pull = '2020-10-21'
        #data_request = requests.get('https://api.fitbit.com/1.2/user/'+self.id+'/sleep/date/'+date_to_pull+'/'+str(today)+'.json', headers = {'Authorization': 'Bearer '+self.token})
        data_request = requests.get('https://api.fitbit.com/1.2/user/'+self.id+'/sleep/date/'+str(today)+'.json', headers = {'Authorization': 'Bearer '+self.token})
        data = data_request.json()['sleep']
        
        # open a file for writing
        path = 'user_data/user'+str(self.user)+'/Sleep/'+str(today) + '.csv'
        sleep_data = open('user_data/user'+str(self.user)+'/sleep_data.csv', 'w')
        # create the csv writer object
        csvwriter = csv.writer(sleep_data)
        count = 0

        for i in data:
            curr_level = i.pop('levels')
            if count == 0:
                header = i.keys()
                csvwriter.writerow(header)
                count += 1
            csvwriter.writerow(i.values())
            curr_date = str(i['dateOfSleep']).replace('/','_')
            level_data = open(path, 'w')
            csvwriter2 = csv.writer(level_data)
            count2 = 0
            for j in curr_level['data']:
                if count2 == 0:
                    header2 = j.keys()
                    csvwriter2.writerow(header2)
                    count2 += 1
                j['dateTime'] = str(j['dateTime']).split('T')[1]
                csvwriter2.writerow(j.values())
            level_data.close()
        sleep_data.close()
        
        return curr_date + '.csv'

    def append_kaggle(self):
        personal_folder = 'user_data/user'+ str(self.user)

        #make new personal folder with sleep and heart directory
        if not os.path.exists(personal_folder):
            os.makedirs(personal_folder)
            os.makedirs(personal_folder+'/Sleep')
            os.makedirs(personal_folder+'/Heart')

        #transfer kaggle.csv to user's directory
        #if not os.path.isfile(personal_folder +'/log.csv'):
        df = pd.read_csv('user_data/kaggle.csv')
        df.to_csv(personal_folder+'/log.csv', index = False)
        self.get_sleep_log()

        if os.path.isfile('user_data/user'+str(self.user)+'/sleep_data.csv'):

            sleep_data = open('user_data/user'+str(self.user)+'/sleep_data.csv', 'r')
            with open('user_data/user'+str(self.user)+'/log.csv', 'a+', newline = "") as fd:
                csvwriter = csv.writer(fd)
                read_sleep_data = csv.reader(sleep_data, delimiter = ',')
                for row in reversed(list(read_sleep_data)):
                    try:
                        date_of_sleep = row[0]
                        #milliseconds -> seconds
                        seconds = (int(row[1]) / 1000)
                        quality = row[2]

                        hour = int(seconds // 3600)
                        minutes = int((seconds % 3600) // 60)

                        time_string =  str("%d:%02d" % (hour, minutes))

                        tuple = [date_of_sleep ,"", str(quality)+"%", time_string, "", "","",""]
                        csvwriter.writerow(tuple)
                    except(ValueError):
                        pass
                fd.close()
            sleep_data.close()



