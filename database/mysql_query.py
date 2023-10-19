import pymysql.err
from database import connection
from math import ceil

cursor  = connection.get_connection.mysql.cursor()
def createUser(private_id,first_name,last_name,phone_number):
    try:
        sql = "INSERT INTO `users` (`private_id`, `first_name`,`last_name`,`phone_number`) VALUES (%s, %s,%s,%s)"
        cursor.execute(sql,(private_id,first_name,last_name,phone_number))
        return  (True,"User created","")
    except pymysql.err.IntegrityError as ex:
        print("INFO : ",ex)
        return (False,f"User with id '{private_id}' already registered","")
    except Exception as ex:
        print("ERROR: ",ex)
        return  (False,"Server problem","")

def saveEntryLog(form):
    #    {'personName': 'Adio Ihsan', 'temperature': 35.6, 'privateId': '812312321', 'qrCode': True, 'realFace': True, 'maxTemperature': 38.5, 'timestamp': '2023-10-07 13:31:34', 'status': True}

       user_id = form["privateId"]
       timestamp = form["timestamp"]
       temperature = form["temperature"]
       real_face = int(form["realFace"])
       registered = int(form["personName"] != "Unknown")
       enter_code = form["qrCode"]
       max_temperature = form["maxTemperature"]
       image_path = "/dino"
       status = int(form["status"])

       try:
            sql = "INSERT INTO `entry_logs` (`user_id`, `timestamp`,`temperature`,`real_face`,`registered`,`enter_code`,`max_temperature`,`image_path`,`status`) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql,(user_id,timestamp,temperature,real_face,registered,enter_code,max_temperature,image_path,status))
            if status == 1:
                return  (True,"Verification Succsess","")
            else :
                return (False,"Verification Failed","")
       except Exception as ex:
            print("ERROR: cant save log to DB cause:",ex)
            return  (False,"Server problem","")
       
def getEntryLog(pagination,status=1):
    limit = pagination["per_page"]
    offset = (pagination["current_page"] -1)*pagination["per_page"]
    try:
        # count total data
        sql_count = "SELECT COUNT(id)  as total_data from entry_logs where status=%s"
        cursor.execute(sql_count,(status))
        res_count = cursor.fetchone()
        pagination["total_data"] = res_count["total_data"]
        pagination["total_page"] = ceil(res_count["total_data"] / pagination["per_page"])
        
        #get the data 
        sql ="SELECT * FROM entry_logs LEFT JOIN users ON entry_logs.user_id = users.private_id WHERE status=%s GROUP BY timestamp ORDER BY timestamp DESC LIMIT %s OFFSET %s "
        cursor.execute(sql,(status,limit,offset))
        result = cursor.fetchall()
        if len(result) > 0:
            for item in result:
                timestamp =  item["timestamp"]
                item["timestamp"] = timestamp.strftime("%H:%M:%S - %d/%B/%Y")
                item["original_timestamp"] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return  (True,"success",{"record":result,"pagination":pagination})
    except Exception as ex:
        print("ERROR: cant get log from DB cause:",ex)
        return (False,"Server Problem",{"record":[],"pagination":pagination})

def getAllUsers(pagination):
    limit = pagination["per_page"]
    offset = (pagination["current_page"] -1)*pagination["per_page"]
    try:
        # count total data and pagination
        sql_count = "SELECT COUNT(id)  as total_data from users"
        cursor.execute(sql_count)
        res_count = cursor.fetchone()
        pagination["total_data"] = res_count["total_data"]
        pagination["total_page"] = ceil(res_count["total_data"] / pagination["per_page"])
        
        #get the data 
        sql =" SELECT *, (SELECT timestamp FROM entry_logs WHERE entry_logs.user_id = users.private_id ORDER BY timestamp DESC LIMIT 1) AS last_entry FROM users ORDER BY first_name ASC LIMIT %s OFFSET %s"
        cursor.execute(sql,(limit,offset))
        result = cursor.fetchall()
        if len(result) > 0:
            for item in result:
                timestamp =  item["last_entry"]
                if timestamp is not None:
                    item["last_entry"] = timestamp.strftime("%H:%M:%S - %d/%B/%Y")
        return  (True,"success",{"record":result,"pagination":pagination})
    except Exception as ex:
        print("ERROR: cant get all users from DB cause:",ex)
        return (False,"Server Problem",{"record":[],"pagination":pagination})

def getOneUser(user_id):
    try:
        sql =" SELECT *, (SELECT timestamp FROM entry_logs WHERE entry_logs.user_id = users.private_id ORDER BY timestamp DESC LIMIT 1) AS last_entry FROM users WHERE users.id = %s"
        cursor.execute(sql,(user_id))
        result = cursor.fetchone()
        if len(result) > 0:
                timestamp =  result["last_entry"]
                if timestamp is not None:
                    result["last_entry"] = timestamp.strftime("%H:%M:%S - %d/%B/%Y")
        else:
                return (False,f"User with not registered",{"record":[]})
        return (True,"succsess",{"record":result})
    except Exception as ex:
        print(f"ERROR: cant get a user with ID {user_id} from DB cause:",ex)
        return (False,"Server Problem",{"record":[]})

 
 
        
            
