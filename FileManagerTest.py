from user_data import FileManager, Firebase, User

db = Firebase.Database()
fm = FileManager.FileManager(db)
user = User.get_user(1)

fm.get_last_readings(1)