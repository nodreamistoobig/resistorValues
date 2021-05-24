from serial.tools import list_ports
import serial
from pymongo import MongoClient
import time
from serial import SerialException
from datetime import datetime

t = time.time()
existed = True
timestamps = []
values = []

client = MongoClient("roboforge.ru", username="admin", password="pinboard123", authSource="admin", serverSelectionTimeoutMS=5000, socketTimeoutMS=2000)
print(client.list_database_names())
db = client['pushmina']
collection = db['photoresistor']


def checkPort():
    for port in list_ports.comports():
        try:
            s = serial.Serial(port.device, baudrate = 9600)
            s.timeout = 1
            
            s.write(b'K')
          
            recieved = s.readline().strip()
            if (recieved==b"Q17"):
                return port.device
        except (KeyboardInterrupt, SerialException) as e:
            print(e)
            existed = False
            break
        except (SerialException) as e:
            print(e)
            break
        s.close()
    return None

def send(ts, v):
    try:
        if (timestamps):
            for i in range(len(timestamps)):
                collection.insert_one({'datetime':timestamps[i], 'value':values[i]}) 
            timestamps.clear()
            values.clear()
        collection.insert_one({'datetime':ts, 'value':v})   
    except Exception as e:
        print(e)
        timestamps.append(ts)
        values.append(v)
           

while (existed):
    #print("looking for port...")
    port = checkPort() 
    if (port):
        s = serial.Serial(port, baudrate = 9600)
        s.timeout = 1
        send_minutes = datetime.now().minute
        while(True):
            try:
                minutes = datetime.now().minute
                if (send_minutes != minutes):
                    s.write(b'P')
                    photores = s.readline().decode().strip()
                    timestamp = datetime.now()
                    print(photores)
                    print(timestamp)
                    send(timestamp, photores)
                    send_minutes = minutes 
            except(KeyboardInterrupt) as e:
                print(e)
                s.close()
                existed = False
                break
            except (SerialException) as e:
                print(e)
                s.close()
                break

        
