import MySQLdb
import threading
import time
from datetime import datetime,timedelta
import random
import Socket_onoff
import os
import Get_Sensordata
import Errorlog_Insert
import Socket_switch_onff
import Control_IO
import matplotest
    
class Thread_water(threading.Thread): 
    def __init__(self,threadID,ip,name,port,sclass,status,line,ec_min,ec_max,do_min,do_max,ph_min,ph_max,temper_min,temper_max,address,place):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.ip = ip
        self.name = name
        self.port = port
        self.sclass = sclass
        self.status = status
        self.line = line
        self.ec_min=ec_min
        self.ec_max=ec_max
        self.do_min=do_min
        self.do_max=do_max
        self.ph_min=ph_min
        self.ph_max=ph_max
        self.temper_min=temper_min
        self.temper_max=temper_max
        self.address=address
        self.place=place
    def run(self):
     #time.sleep(random.randint(0,20))
       print(str(self.threadID)+","+str(self.ec_min)+","+str(self.ec_max)+","+str(self.do_min)+","+str(do_max)+","+str(ph_min)+","+str(ph_max)+","+str(temper_min)+","+str(temper_max)+","+str(self.address)+","+str(self.place))
       Socket_onoff.water_test(self.ip,self.port,self.line,self.ec_min,self.ec_max,self.do_min,self.do_max,self.ph_min,self.ph_max,self.temper_min,self.temper_max,self.address,self.place)

class Thread_watercheap(threading.Thread): 
    def __init__(self,threadID,ip,name,port,sclass,status,line,ec_min,ec_max,do_min,do_max,ph_min,ph_max,temper_min,temper_max,address,place):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.ip = ip
        self.name = name
        self.port = port
        self.sclass = sclass
        self.status = status
        self.line = line
        self.ec_min=ec_min
        self.ec_max=ec_max
        self.do_min=do_min
        self.do_max=do_max
        self.ph_min=ph_min
        self.ph_max=ph_max
        self.temper_min=temper_min
        self.temper_max=temper_max
        self.address=address
        self.place=place
    def run(self):
     #time.sleep(random.randint(0,20))
       print(str(self.threadID)+","+str(self.ec_min)+","+str(self.ec_max)+","+str(self.do_min)+","+str(do_max)+","+str(ph_min)+","+str(ph_max)+","+str(temper_min)+","+str(temper_max)+","+str(self.address)+","+str(self.place))
       for i in range(0,3):
         print("water_cheap: "+str(i))
         Socket_onoff.water_cheap(self.ip,self.port,self.line,self.ec_min,self.ec_max,self.do_min,self.do_max,self.ph_min,self.ph_max,self.temper_min,self.temper_max,self.address,self.place)

class Thread_envior(threading.Thread):
    def __init__(self,threadID,ip,name,port,sclass,status,line,address,place):
        threading.Thread.__init__(self)
        self.ip = ip
        self.name = name
        self.port = port
        self.sclass = sclass
        self.status = status
        self.line = line
        self.address = address
        self.place = str(place)
    def run(self):
        if str(self.place)=="1":
          Socket_onoff.enviro_modbus(self.ip,int(self.port),self.address,self.place)
        elif str(self.place)=="2":
          Socket_onoff.enviro(self.ip,int(self.port),self.address,self.place)
        print(str(self.ip)+","+str(self.port)+","+str(self.address)) 
         
class Thread_envior_temphum(threading.Thread):
    def __init__(self,threadID,ip,name,port,sclass,status,line,address,place):
        threading.Thread.__init__(self)
        self.ip = ip
        self.name = name
        self.port = port
        self.sclass = sclass
        self.status = status
        self.line = line
        self.address = address
        self.place = place
    def run(self):

        Socket_onoff.temhum_modbus(self.ip,int(self.port),self.address,self.place)
        #print(str(self.ip)+","+str(self.port)+","+str(self.address)+"you!!!!!") 
        #print("fuck you!!!!!!!!!!!!!")

class Thread_light(threading.Thread):
    def __init__(self,threadID,ip,name,port,sclass,status,line,address,place,light_max,light_min):
        threading.Thread.__init__(self)
        self.ip = ip
        self.name = name
        self.port = port
        self.sclass = sclass
        self.status = status
        self.line = line
        self.address = address
        self.place = place
        self.light_max = light_max
        self.light_min = light_min
    def run(self):
        print(str(self.ip)+","+str(self.port)+","+str(self.address)+str(self.light_max)+","+str(self.light_min)+",light!!!") 
        Socket_onoff.light_modbus(self.line,self.ip,int(self.port),str(self.address),self.place,light_max,light_min)

class Thread_wind(threading.Thread):
    def __init__(self,threadID,ip,name,port,sclass,status,line,address,place,wind_max,wind_min):
        threading.Thread.__init__(self)
        self.ip = ip
        self.name = name
        self.port = port
        self.sclass = sclass
        self.status = status
        self.line = line
        self.address = address
        self.place = place
        self.wind_max = wind_max
        self.wind_min = wind_min
    def run(self):
        Socket_onoff.big_wind_modbus(self.line,self.ip,int(self.port),self.address,self.place,wind_max,wind_min)
        print(str(self.ip)+","+str(self.port)+","+str(self.address)+","+str(self.wind_max)+","+str(self.wind_min)+",wind") 

class Thread_waterlengh(threading.Thread):
    def __init__(self,threadID,ip,name,port,sclass,status,line,address,place,water_max,water_min):
        threading.Thread.__init__(self)
        self.ip = ip
        self.name = name
        self.port = port
        self.sclass = sclass
        self.status = status
        self.line = line
        self.address = address
        self.place = place
        self.water_max = water_max
        self.water_min = water_min
    def run(self):
        Socket_onoff.waterlengh_modbus(self.line,self.ip,int(self.port),self.address,self.place,water_max,water_min)
        print(str(self.ip)+","+str(self.port)+","+str(self.address)+","+str(self.water_max)+","+str(self.water_min)+",water") 

class Thread_soil(threading.Thread):
    def __init__(self,threadID,ip,name,port,sclass,status,line,address,place,soil_temp_min,soil_temp_max,soil_hum_min,soil_hum_max,soil_ec_min,soil_ec_max,soil_ph_min,soil_ph_max):
        threading.Thread.__init__(self)
        self.ip = ip
        self.name = name
        self.port = port
        self.sclass = sclass
        self.status = status
        self.line = line
        self.address = address
        self.place = place
        self.soil_temp_min = soil_temp_min
        self.soil_temp_max = soil_temp_max
        self.soil_hum_min = soil_hum_min
        self.soil_hum_max = soil_hum_max
        self.soil_ec_min = soil_ec_min
        self.soil_ec_max = soil_ec_max
        self.soil_ph_min = soil_ph_min
        self.soil_ph_max = soil_ph_max

    def run(self):
        print("soil!!!!")
        print(str(self.line)+","+str(self.ip)+","+str(self.port)+","+str(self.address)+","+str(self.place)+","+str(soil_temp_min)+","+str(soil_temp_min)+","+str(self.soil_hum_min)+","+str(self.soil_hum_max)+","+str(soil_ec_min)+","+str(soil_ec_max)+","+str(soil_ph_min)+","+str(soil_ph_max))
        Socket_onoff.LCD_temhum_modbus(self.line,self.ip,int(self.port),self.address,self.place)


class ChangetoPort(threading.Thread):
   def __init__(self):
     threading.Thread.__init__(self)
   def run(self):
     #print ("fuck!!!")
     val1=os.system("node /home/pfs/html/jsmpeg-master/websocket-relay.js yfa 8081 8082")

class ChangetoPort2(threading.Thread):
   def __init__(self):
     threading.Thread.__init__(self)
   def run(self):
     #print ("fuck!!!")
     val1=os.system("node /home/pfs/html/jsmpeg-master/websocket-relay.js yfa 8083 8084")

class Runvideo(threading.Thread):
   def __init__(self):
     threading.Thread.__init__(self)
   def run(self):
     while(1):
       val2=os.system("ffmpeg -i 'rtsp://admin:admin@192.168.99.15' -q 0 -f mpegts -codec:v mpeg1video -s 1366x768 http://192.168.99.2:8081/yfa")

       #val2=os.system("ffmpeg -i 'rtsp://admin:yfa@192.168.99.11:88/live/video/profile2' -q 0 -f mpegts -codec:v mpeg1video -s 1366x768 http://192.168.99.2:8081/yfa")
       time.sleep(3)
     time.sleep(3)

class Runvideo2(threading.Thread):
   def __init__(self):
     threading.Thread.__init__(self)
   def run(self):
     while(1):
       #val2=os.system("ffmpeg -i 'rtsp://admin:admin@192.168.99.15' -q 0 -f mpegts -codec:v mpeg1video -s 1366x768 http://192.168.99.2:8083/yfa")
       val2=os.system("ffmpeg -i 'rtsp://admin:yfa@192.168.99.11:88/live/video/profile2' -q 0 -f mpegts -codec:v mpeg1video -s 1366x768 http://192.168.99.2:8083/yfa")
       time.sleep(3)
     time.sleep(3)

class Everyhour(threading.Thread):
   def __init__(self):
     threading.Thread.__init__(self)
   def run(self):
     while(1):
       curtime = datetime.now()
       destime = curtime.replace(minute=0,second=0,microsecond=0)
       delta = curtime-destime
       sleeptime = 3600-delta.total_seconds()
       #print"Must sleep %d seconds"%sleeptime
       time.sleep(sleeptime)
       Get_Sensordata.getsensor_datatohistory()
       Socket_onoff.power_modbus("192.168.99.10",4001,"30","1")
       time.sleep(1)
       Socket_onoff.powernow_modbus("192.168.99.10",4001,"30","1")
       #
       Socket_onoff.power_modbus_2f("192.168.99.27",4001,"1","2")
       time.sleep(1)
       Socket_onoff.powernow_modbus_2f("192.168.99.27",4001,"1","2")

class Autocontrol(threading.Thread):
   def __init__(self):
     threading.Thread.__init__(self)
   def run(self):
     while(1):
       db = MySQLdb.connect(host="localhost", user="root", passwd="yfa", db="plant_yfa")
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
               Control_IO.Hand_switch(ip,address,1)
               cs='1'
             else:
               Control_IO.Hand_switch(ip,address,0)
               cs='0'
           else:
             if int(start_time[0:2])<= now_time or int(end_time[0:2])>now_time:
               Control_IO.Hand_switch(ip,address,1)
               cs='1'
             else:
               Control_IO.Hand_switch(ip,address,0)         
               cs='0'
           cursor.execute("UPDATE control_led SET control_status = '"+str(cs)+"' WHERE ip = '"+ip+"' AND address= "+address+";")
           db.commit()
         #Have two led time
         else:
           if int(start_time[0:2])<int(end_time[0:2]) and int(start_time2[0:2])<int(end_time2[0:2]):
             if int(start_time[0:2])<=now_time<int(end_time[0:2]) or int(start_time2[0:2])<=now_time<int(end_time2[0:2]):
               Control_IO.Hand_switch(ip,address,1)
               cs='1'
             else:
               Control_IO.Hand_switch(ip,address,0)
               cs='0'
           elif int(start_time[0:2])<int(end_time[0:2]) and int(start_time2[0:2])>int(end_time2[0:2]):
             if int(start_time2[0:2])<= now_time or int(end_time2[0:2])>now_time:
               Control_IO.Hand_switch(ip,address,1)
               cs='1'
             elif int(start_time[0:2])<=now_time<int(end_time[0:2]):
               Control_IO.Hand_switch(ip,address,1)
               cs='1'
             else:
               Control_IO.Hand_switch(ip,address,0)
               cs='0'
           else:
             if int(start_time[0:2])<= now_time or int(end_time[0:2])>now_time:
               Control_IO.Hand_switch(ip,address,1)
               cs='1'
             elif int(start_time2[0:2])<=now_time<int(end_time2[0:2]):
               Control_IO.Hand_switch(ip,address,1)
               cs='1'
             else:
               Control_IO.Hand_switch(ip,address,0)
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
       db = MySQLdb.connect(host="localhost", user="root", passwd="yfa", db="plant_yfa")
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
           Control_IO.Hand_switch(ip,address,0)
           #Control_IO.Test_DO('Mix0'+str(mix),'0')
           cursor.execute("UPDATE control_motor SET hour_timer = '"+str(hour_timer)+"' WHERE ip = '"+ip+"' AND address = "+address+";")
           #db.commit()
         else:
           if minute_timer>0:
             minute_timer=minute_timer-1
             cursor.execute("UPDATE control_motor SET minute_timer = '"+str(minute_timer)+"' WHERE ip = '"+ip+"' AND address = "+address+";")
             Control_IO.Hand_switch(ip,address,1)
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

class CheckIO(threading.Thread):
   def __init__(self):
     threading.Thread.__init__(self)
   def run(self):
     while(1):
       time.sleep(10)
       for i in range(0,16):
         Control_IO.Check_ConnectIO(str(i))

class Plot_3d(threading.Thread):
   def __init__(self):
     threading.Thread.__init__(self)
   def run(self):
     while(1):
       db = MySQLdb.connect(host="localhost", user="root", passwd="yfa", db="plant_yfa")
       cursor = db.cursor()
       cursor_threshold = db.cursor()
       cursor.execute("SELECT * FROM lidar_setting")
       result = cursor.fetchall()
       for i in result:
         if (str(i[4])=='true'):
           matplotest.plot_3d()
           Errorlog_Insert.write_3d_plot('false')
           time.sleep(60)
       else:
           time.sleep(60)

class Check_Water(threading.Thread):
   def __init__(self):
     threading.Thread.__init__(self)
   def run(self):
     while(1):
       db = MySQLdb.connect(host="localhost", user="root", passwd="yfa", db="plant_yfa")
       cursor = db.cursor()
       cursor.execute("SELECT * FROM control_water where control = 'manual';")
       result = cursor.fetchall()
       for i in result:
         ip=str(i[1])
         address=str(i[2])
         secondtime=int(i[6])
         name=str(i[10])
         constatus=str(i[8])
         #cursor.execute("UPDATE control_water SET control_status = '"+Control_IO.Check_Web_DO(name)+"' WHERE address = "+address+";")

         if constatus=='1':
           if secondtime>0:
             secondtime=secondtime-3
           else:
             secondtime=1800
             Control_IO.Web_DO(name,'0')
             cursor.execute("UPDATE control_water SET control_status='0' WHERE address = "+address+";")
           cursor.execute("UPDATE control_water SET time = '"+str(secondtime)+"' WHERE address = "+address+";")
           db.commit()
         else:
           if(secondtime!=1800):
             secondtime=1800
             cursor.execute("UPDATE control_water SET time = '"+str(secondtime)+"' WHERE address = "+address+";")
             db.commit()
       db.close()
       time.sleep(3)


thread2=ChangetoPort()
thread2.setDaemon(True)
thread2.start()
time.sleep(2)
thread3=Runvideo()
thread3.setDaemon(True)
thread3.start()
time.sleep(1)

thread4=Everyhour()
thread4.setDaemon(True)
thread4.start()
time.sleep(1)
thread5=Autocontrol()
thread5.setDaemon(True)
thread5.start()
time.sleep(1)
thread8=Autocontrol_Motor()
thread8.setDaemon(True)
thread8.start()
time.sleep(1)

#thread9=CheckIO()
#thread9.setDaemon(True)
#thread9.start()
#time.sleep(1)
thread10=Check_Water()
thread10.setDaemon(True)
thread10.start()
time.sleep(1)

thread6=ChangetoPort2()
thread6.setDaemon(True)
thread6.start()
time.sleep(1)
thread7=Runvideo2()
thread7.setDaemon(True)
thread7.start()
time.sleep(1)

thread11=Plot_3d()
thread11.setDaemon(True)
thread11.start()
time.sleep(1)

#Default
'''
Errorlog_Insert.status_alarm("192.168.99.12","8080","Com1","on")
Socket_switch_onff.is_safe()
time.sleep(2)
Errorlog_Insert.status_alarm("192.168.99.12","8080","Com2","off")
Socket_switch_onff.close_alarm()
time.sleep(2)
'''
while (1):
  
  for n in range(1,14):
    db = MySQLdb.connect(host="localhost", user="root", passwd="yfa", db="plant_yfa")
    cursor = db.cursor()
    cursor_threshold = db.cursor()

    cursor.execute("SELECT * FROM sensor_setting where line ='"+str(n)+"'")
    result = cursor.fetchall()

    cursor_threshold.execute("SELECT * FROM crop_schedule where line ='"+str(n)+"'")
    result_threshold = cursor_threshold.fetchall()

    #print("n: "+str(n))

    ec_min=0.0
    ec_max=20.0
    do_min=0.0
    do_max=20.0
    ph_min=0.0
    ph_max=14.0
    temper_min=0.0
    temper_max=99.9
    wind_min=0.0
    wind_max=70.0
    light_min=0.0
    light_max=1700.0
    water_min=0.0
    water_max=100.0
    soil_temp_min=0.0
    soil_temp_max=99.9
    soil_hum_min=0.0
    soil_hum_max=99.9
    soil_ph_min=0.0
    soil_ph_max=14.0
    soil_ec_min=0.0
    soil_ec_max=20.0

  
    for i in result_threshold:
      print(str(i[8])+","+str(i[9])+","+str(i[10])+","+str(i[11])+","+str(i[12]))
      if float(i[8])>ec_min:
        ec_min=float(i[8])
      if float(i[9])<ec_max:
        ec_max=float(i[9])
    
      if float(i[10])>do_min:
        do_min=float(i[10])
      if float(i[11])<do_max:
        do_max=float(i[11])

      if float(i[12])>ph_min:
        ph_min=float(i[12])
      if float(i[13])<ph_max:
        ph_max=float(i[13])
   
      if float(i[14])>temper_min:
        temper_min=float(i[14])
      if float(i[15])<temper_max:
        temper_max=float(i[15])

      if float(i[16])>wind_min:
        wind_min=float(i[16])
      if float(i[17])<wind_max:
        wind_max=float(i[17])
      
      if float(i[18])>light_min:
        light_min=float(i[18])
      if float(i[19])<light_max:
        light_max=float(i[19])
      
      if float(i[20])>water_min:
        water_min=float(i[20])
      if float(i[21])<water_max:
        water_max=float(i[21])
      
      if float(i[22])>soil_temp_min:
        soil_temp_min=float(i[22])
      if float(i[23])<soil_temp_max:
        soil_temp_max=float(i[23])

      if float(i[24])>soil_hum_min:
        soil_hum_min=float(i[24])
      if float(i[25])<soil_hum_max:
        soil_hum_max=float(i[25])
      
      if float(i[26])>soil_ph_min:
        soil_ph_min=float(i[26])
      if float(i[27])<soil_ph_max:
        soil_ph_max=float(i[27])
      
      if float(i[28])>soil_ec_min:
        soil_ec_min=float(i[28])
      if float(i[29])<soil_ec_max:
        soil_ec_max=float(i[29])
    
    threads=[] 

    for record in result:
      Sid = record[0]
      Sip = record[1]
      Sdevice_name = record[2]
      Sport = record[3]
      Sclass = record[4]
      Sstatus = record[5]
      Sline = record[6]
      Saddress = record[7]
      Splace = record[9]
    
      if Sclass == "water":
        thread1 = Thread_water(Sid,Sip,Sdevice_name,Sport,Sclass,Sstatus,Sline,ec_min,ec_max,do_min,do_max,ph_min,ph_max,temper_min,temper_max,Saddress,Splace)
        thread1.setDaemon(True)
        thread1.start()
        threads.append(thread1)
      elif Sclass == "envior":
        thread1 = Thread_envior(Sid,Sip,Sdevice_name,Sport,Sclass,Sstatus,Sline,Saddress,Splace)
        thread1.setDaemon(True)
        thread1.start()
        threads.append(thread1)
      elif Sclass == "envior_temphum": 
        thread1 = Thread_envior_temphum(Sid,Sip,Sdevice_name,Sport,Sclass,Sstatus,Sline,Saddress,Splace)
        thread1.setDaemon(True)
        thread1.start()
        threads.append(thread1)
      elif Sclass == "light": 
        thread1 = Thread_light(Sid,Sip,Sdevice_name,Sport,Sclass,Sstatus,Sline,Saddress,Splace,light_min,light_max)
        thread1.setDaemon(True)
        thread1.start()
        threads.append(thread1)
      elif Sclass == "wind": 
        thread1 = Thread_wind(Sid,Sip,Sdevice_name,Sport,Sclass,Sstatus,Sline,Saddress,Splace,wind_min,wind_max)
        thread1.setDaemon(True)
        thread1.start()
        threads.append(thread1)
      elif Sclass == "waterlengh": 
        thread1 = Thread_waterlengh(Sid,Sip,Sdevice_name,Sport,Sclass,Sstatus,Sline,Saddress,Splace,water_min,water_max)
        thread1.setDaemon(True)
        thread1.start()
        threads.append(thread1)
      elif Sclass == "soil": 
        thread1 = Thread_soil(Sid,Sip,Sdevice_name,Sport,Sclass,Sstatus,Sline,Saddress,Splace,soil_temp_min,soil_temp_max,soil_hum_min,soil_hum_max,soil_ec_min,soil_ec_max,soil_ph_min,soil_ph_max)
        thread1.setDaemon(True)
        thread1.start()
        threads.append(thread1)
      elif Sclass == "water_cheap":
        thread1 = Thread_watercheap(Sid,Sip,Sdevice_name,Sport,Sclass,Sstatus,Sline,ec_min,ec_max,do_min,do_max,ph_min,ph_max,temper_min,temper_max,Saddress,Splace)
      time.sleep(1)
    for t in threads:
      t.join()
    db.close()
    print ("Exiting Main Thread")
    time.sleep(1)
#db.close()
