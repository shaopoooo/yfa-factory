import json
import sys
import time
import os
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

import requests
import MySQLdb
from dotenv import load_dotenv

# Configure logging
logging.basicConfig()
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)

load_dotenv()
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
passwd = os.getenv("DB_PASSWD")
db_name = os.getenv("DB_NAME")

def get_db_connection():
  return MySQLdb.connect(host, user, passwd, db_name)

def Hand_switch(ip,address,doStatus):
  try:
    url = 'http://'+ip+'/api/slot/0/io/do/'+address+'/doStatus'
    headers = {'Content-type': 'application/json', 'Accept': 'vdn.dac.v1'}
  
    r = requests.get(url, headers=headers)
    r = json.loads(r.text)
    #print (r['io']['do'][address]['doStatus'])
    now_status=(r['io']['do'][address]['doStatus'])  
    
    if(now_status!=doStatus): 
      data={"slot":0,"io":{"do":{address:{"doStatus":doStatus}}}}
      aa=json.dumps(data,indent=4)
      # requests.put(url, aa, headers=headers) # Uncomment if this was intended to run
      k= requests.put(url, aa, headers=headers)
       
  except:
    print("Unexpected error:", sys.exc_info()[0])

def run_led_control():
  print("[%s] Running LED control task..." % time.strftime("%Y-%m-%d %H:%M:%S"))
  try:
      db = get_db_connection()
      cursor = db.cursor()
      cursor.execute("SELECT * FROM control_led where control = 'auto';")
      result = cursor.fetchall()
      for i in result:
        ip=str(i[1])
        start_time=str(i[6])
        end_time=str(i[7])
        now_time=int(time.strftime("%H", time.localtime()))
        mode=1
        address=str(i[2])
        if str(i[11])!='None' and str(i[12])!='None':
          if str(i[11])!='' and str(i[12])!='':
            mode=2
            start_time2=str(i[11])
            end_time2=str(i[12])
        #Only one Led
        if mode==1:
          cs='0'
          if int(start_time[0:2])<int(end_time[0:2]):
            if int(start_time[0:2])<=now_time<int(end_time[0:2]):
              Hand_switch(ip,address,1)
              cs='1'
            else:
              Hand_switch(ip,address,0)
              cs='0'
          else:
            if int(start_time[0:2])<= now_time or int(end_time[0:2])>now_time:
              Hand_switch(ip,address,1)
              cs='1'
            else:
              Hand_switch(ip,address,0)
              cs='0'
          cursor.execute("UPDATE control_led SET control_status = '"+str(cs)+"' WHERE ip = '"+ip+"' AND address= "+address+";")
          db.commit()
        #Have two led time
        else:
          if int(start_time[0:2])<int(end_time[0:2]) and int(start_time2[0:2])<int(end_time2[0:2]):
            if int(start_time[0:2])<=now_time<int(end_time[0:2]) or int(start_time2[0:2])<=now_time<int(end_time2[0:2]):
              Hand_switch(ip,address,1)
              cs='1'
            else:
              Hand_switch(ip,address,0)
              cs='0'
          elif int(start_time[0:2])<int(end_time[0:2]) and int(start_time2[0:2])>int(end_time2[0:2]):
            if int(start_time2[0:2])<= now_time or int(end_time2[0:2])>now_time:
              Hand_switch(ip,address,1)
              cs='1'
            elif int(start_time[0:2])<=now_time<int(end_time[0:2]):
              Hand_switch(ip,address,1)
              cs='1'
            else:
              Hand_switch(ip,address,0)
              cs='0'
          else:
            if int(start_time[0:2])<= now_time or int(end_time[0:2])>now_time:
              Hand_switch(ip,address,1)
              cs='1'
            elif int(start_time2[0:2])<=now_time<int(end_time2[0:2]):
              Hand_switch(ip,address,1)
              cs='1'
            else:
              Hand_switch(ip,address,0)
              cs='0'
          cursor.execute("UPDATE control_led SET control_status = '"+str(cs)+"' WHERE ip = '"+ip+"' AND address= "+address+";")
          db.commit()
      db.close()
      print("[%s] LED control task finished." % time.strftime("%Y-%m-%d %H:%M:%S"))
  except Exception as e:
      print("Error in LED control:", e)

def run_motor_control():
  print("[%s] Running Motor control task..." % time.strftime("%Y-%m-%d %H:%M:%S"))
  try:
      db = get_db_connection()
      cursor = db.cursor()
      cursor.execute("SELECT * FROM control_motor where control = 'auto';")
      result = cursor.fetchall()

      current_time = time.localtime()
      # Calculate total minutes from start of the day (00:00)
      current_total_minutes = current_time.tm_hour * 60 + current_time.tm_min

      for i in result:
        ip = str(i[1])
        address = str(i[2])
        hour_cycle = int(i[6])
        minute_cycle = int(i[7])
        
        cycle_minutes = hour_cycle * 60
        if cycle_minutes == 0:
            cycle_minutes = 24 * 60 # Default to 24 hours if 0 to avoid error

        # Determine position in the cycle
        position = current_total_minutes % cycle_minutes
        
        # Logic: First 'minute_cycle' minutes are ON, rest are OFF
        if position < minute_cycle:
          # ON Phase
          Hand_switch(ip, address, 1)
          minute_timer = minute_cycle - position
          hour_timer = 0
        else:
          # OFF Phase
          Hand_switch(ip, address, 0)
          minute_timer = 0
          hour_timer = cycle_minutes - position

        cursor.execute("UPDATE control_motor SET hour_timer = '"+str(hour_timer)+"', minute_timer = '"+str(minute_timer)+"' WHERE ip = '"+ip+"' AND address = "+address+";")

      db.commit()
      db.close()
      print("[%s] Motor control task finished." % time.strftime("%Y-%m-%d %H:%M:%S"))
  except Exception as e:
      print("Error in Motor control:", e)

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    
    # Schedule LED control to run every 10 seconds
    scheduler.add_job(run_led_control, 'cron', minute='*', second='*/10')
    
    # Schedule Motor control to run every 10 seconds
    scheduler.add_job(run_motor_control, 'cron', minute='*', second='*/10')
    
    print('Starting scheduler... Press Ctrl+C to exit')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
