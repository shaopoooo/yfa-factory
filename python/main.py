import json
import sys
import threading
import time
import os

import requests
import MySQLdb
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
passwd = os.getenv("DB_PASSWD")
db_name = os.getenv("DB_NAME")

def Hand_switch(ip,address,doStatus):
  try:
    url = 'http://'+ip+'/api/slot/0/io/do/'+address+'/doStatus'
    headers = {'Content-type': 'application/json', 'Accept': 'vdn.dac.v1'}
  
    r = requests.get(url, headers=headers)
    r = json.loads(r.text)
    #print (r['io']['do'][address]['doStatus'])
    now_status=(r['io']['do'][address]['doStatus'])  
    ''' 
    if address=='2':
      Errorlog_Insert.status_connection_motor('2')
      Errorlog_Insert.status_connection_motor('3')
      Errorlog_Insert.status_connection_motor('4')
      Errorlog_Insert.status_connection_motor('5')
    else:  
      Errorlog_Insert.status_connection_led(address)
    '''
    if(now_status!=doStatus): 
      data={"slot":0,"io":{"do":{address:{"doStatus":doStatus}}}}
      aa=json.dumps(data,indent=4)
      k= requests.put(url, aa, headers=headers)
       
  except:
    print("Unexpected error:", sys.exc_info()[0])

class AutoControlLed(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
  def run(self):
    while(1):
      db = MySQLdb.connect(host, user, passwd, db_name)
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
      time.sleep(3)

class Autocontrol_Motor(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
  def run(self):
    while(1):
      time.sleep(60)
      db = MySQLdb.connect(host, user, passwd, db_name)
      cursor = db.cursor()
      cursor.execute("SELECT * FROM control_motor where control = 'auto';")
      result = cursor.fetchall()

      for i in result:
        ip=str(i[1])
        hour_cycle=int(i[6])
        minute_cycle=int(i[7])
        #now_time=int(time.strftime("%H", time.localtime()))
        address=str(i[2])
        #print (address)
        hour_timer=int(i[9])
        minute_timer=int(i[10])
        mix=int(i[3])-13
        if hour_timer>0:
          hour_timer=hour_timer-1
          #print (hour_timer)
          Hand_switch(ip,address,0)
          #Control_IO.Test_DO('Mix0'+str(mix),'0')
          cursor.execute("UPDATE control_motor SET hour_timer = '"+str(hour_timer)+"' WHERE ip = '"+ip+"' AND address = "+address+";")
          #db.commit()
        else:
          if minute_timer>0:
            minute_timer=minute_timer-1
            cursor.execute("UPDATE control_motor SET minute_timer = '"+str(minute_timer)+"' WHERE ip = '"+ip+"' AND address = "+address+";")
            Hand_switch(ip,address,1)
            #Control_IO.Test_DO('Mix0'+str(mix),'1')
            #print (minute_timer)
            #db.commit()
          else:
            hour_timer=hour_cycle*60
            minute_timer=minute_cycle
            cursor.execute("UPDATE control_motor SET hour_timer = '"+str(hour_timer)+"', minute_timer = '"+str(minute_timer)+"' WHERE ip = '"+ip+"' AND address = "+address+";")
            #db.commit()

      db.commit()
      db.close()

thread1=AutoControlLed()
thread1.setDaemon(True)
thread1.start()

while (1):
  print ("Exiting Main Thread")
  time.sleep(1)