from time import sleep 
#from firebase import Firebase
import time
import firebase_admin
from firebase_admin import auth, credentials, storage, db

CONFIG = {
  'apiKey': 'AIzaSyD-SCaJu_hye_hg95jur0w1DqfoU6svx5M',
  #"apiKey": "AAAA9rSNhpA:APA91bEf6pvQKLb0cyDXDA33sDuCqBWo4BLsZj2B065azB_RVXBNJqhu1-dzNwWfiCJHgfD-xtMEG4tPZP8n5Bp9pG05AxlX0LLi8kuqy6PE8aNC9RDcANxaj2yzHn6Nlf7oPUg5OF2N",
  "authDomain": "rorrim-fcb4c.firebaseapp.com",
  "databaseURL": "https://rorrim-fcb4c-default-rtdb.firebaseio.com/",
  "storageBucket": "rorrim-fcb4c.appspot.com"
}

#original_token = 'eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJSUzI1NiIsICJraWQiOiAiNTlkMzY3MzIxNzVkN2Q0NzRiYzIxNTdhMTIyNTk2Y2EyNWU0MjY2NSJ9.eyJpc3MiOiAiZmlyZWJhc2UtYWRtaW5zZGstOWFncjRAcm9ycmltLWZjYjRjLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwgInN1YiI6ICJmaXJlYmFzZS1hZG1pbnNkay05YWdyNEByb3JyaW0tZmNiNGMuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLCAiYXVkIjogImh0dHBzOi8vaWRlbnRpdHl0b29sa2l0Lmdvb2dsZWFwaXMuY29tL2dvb2dsZS5pZGVudGl0eS5pZGVudGl0eXRvb2xraXQudjEuSWRlbnRpdHlUb29sa2l0IiwgInVpZCI6ICJST1JSSU0iLCAiaWF0IjogMTYxMTYyNTA0NSwgImV4cCI6IDE2MTE2Mjg2NDV9.gt4w5vmxBcL_26NS05w6sgEB9_KAWh5o2zXu7iCe_Purk34ykEdiJSdD-OMQFJqPAKOu5tGV2jw6EOU4ZUePdyerOHoIMvKYhws4zqdf9d3QPGko2qFzE7IUh5TRNKosDGrCACB9g4h0xtEJ3HbOZ3--Cda9tiJGED0reTCtrQe_RYfQdqSwnewp_O89tzoZ2IChWziuY4dWJmTarQdnZm-fo3EvFV2hLc4VqBOOC9UopMxDeo2Zx3mxip0GjW-BcKLLruh-qDZFzxmkO4VejN3MBVuXutxwAQQj5zj_PVsk8JRx44ykv8-tPABhIZB0zpYd78jvjovzYyGA-OTkKg'

SLEEP = 'Sleep'
HEART = 'Heart'
SPO2_TEMP = None 

class Database():
    def __init__(self):
        self.config = CONFIG
#         self.db = self.firebase.database()
#         self.storage = self.firebase.storage()
#         self.auth = self.firebase.auth()
        
        cred = credentials.Certificate("user_data/rorrim-fcb4c-firebase-adminsdk-9agr4-59d3673217.json")
        firebase_admin.initialize_app(cred, CONFIG)
        
        #token = auth.create_custom_token(uid='RORRIM')
        #self.user = self.auth.sign_in_with_custom_token(original_token)
        
        
    def push_data(self, user_id, temp=None, spo2=None, steps=None, heart_rate = None): 
        
        date = time.strftime('%m-%d-%y', time.localtime())
        curtime = time.strftime('%H:%M:%S', time.localtime())
        
        if temp is not None: 
            #print("Temp=", temp)
            db.reference("/"+str(user_id)+"/"+str(date)+"/"+str(curtime)).update({'Temperature': temp})
            #print("Uploading...")
            #print("Done")
        if spo2 is not None:
            #print("SPO2=", spo2)
            db.reference("/"+str(user_id)+"/"+str(date)+"/"+str(curtime)).update({'SPO2': spo2})
            #print("Uploading...")
            #print("Done")
        if steps is not None:
            #print("Steps=", steps)
            db.reference("/"+str(user_id)+"/"+str(date)+"/"+str(curtime)).update({'Steps': steps})
            #print("Uploading...")
            #print("Done")
        if heart_rate is not None:
            #print("Steps=", steps)
            db.reference("/"+str(user_id)+"/"+str(date)+"/"+str(curtime)).update({'Heart Rate': heart_rate})
            #print("Uploading...")
            #print("Done")
                
    def push_file(self, user_id, health_type, file_name):
        bucket = storage.bucket()
        
        if health_type is not SPO2_TEMP:
            blob = bucket.blob(str(user_id)+'/'+health_type+'/'+file_name)
            blob.upload_from_filename('user_data/user'+str(user_id)+'/'+health_type+'/'+file_name)
        else:
            blob = bucket.blob(str(user_id)+'/'+file_name)
            blob.upload_from_filename('user_data/user'+str(user_id)+'/'+file_name)
#         
#         if health_type is not SPO2_TEMP:
#             self.storage.child(str(user_id)+'/'+health_type+'/'+file_name).put('user_data/user'+user_id+'/'+health_type+'/'+file_name,self.user['idToken'] )
#         else:
#             self.storage.child(str(user_id)+'/'+file_name).put('user_data/user'+str(user_id)+'/'+file_name, self.user['idToken'])
            
        #print("Pushed")
        
        
            
    def get_data(self,user_id,date=None):
        if date is None:
            date = time.strftime('%m-%d-%y', time.localtime())
            
        #print("Reading from Firebase...")
        #print("Last uploaded reading was: ")
        result = self.db.child(str(user_id)).child(str(date)).get() 
        #print(result.val()) 
        #print("Done")
        

        

        
        
        
    
        
