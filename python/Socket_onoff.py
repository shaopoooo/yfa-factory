import socket
import time
import struct
import Errorlog_Insert
import codecs
import binascii
import random
import MySQLdb
import Socket_switch_onff
import threading
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import logging
import Control_IO
import datetime

class Thread_alarm(threading.Thread):
    def __init__(self):
      threading.Thread.__init__(self)
    def run(self):
      #Errorlog_Insert.status_alarm("192.168.99.12","8080","Com2","on")
      time.sleep(2)
      Socket_switch_onff.open_alarm()


def enviro(ip,port,address,place):
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  try:
    s.connect(ipaddress)
    s.settimeout(10)
  
    time.sleep(2)
    data = s.recv(256) 
    data=binascii.hexlify(data).decode()
    s.close()
    #print(data)
    if(str(data[0:4])=="0200" and str(data[44:48])=="0d0a"):
      #print(data[28:36].decode('hex'))
     
      co2 = int(data[6:14].decode('hex'))
      temp = str(data[18:26].decode('hex'))
      hum =  str(data[28:36].decode('hex'))
      Errorlog_Insert.write_envior(str(co2),str(temp),str(hum),str(place))
      Errorlog_Insert.status_connection(ip,port,address,place)
      Errorlog_Insert.clean_errortime(ip,port,address,place)
  except:
    if(int(Errorlog_Insert.find_errortime(ip,port,address,place))<6):
      Errorlog_Insert.add_errortime(ip,port,address,place)
      s.close()
    else:
      s.close()
      Errorlog_Insert.status_disconnection(ip,port,address,place)
      Errorlog_Insert.write_envior('-','-','-',place)
    #print "fuck!!!!!!!!"
      

 
def water_test(ip,port,line,ec_min,ec_max,do_min,do_max,ph_min,ph_max,temper_min,temper_max,address,place):
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  
  try:
    s.connect(ipaddress)
    s.settimeout(10)
    
    s.send('\x00\x00\x00\x00\x00\x06\x01\x04\x00\x00\x00\x09')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    s.close()
    #print(data)
    if(len(str(data))==54):
      ph=float(int(str(data[18:22]),16))/100
      do=float(int(str(data[34:38]),16))/100
      ec=float(int(str(data[42:46]),16))/1000
      temper=float(int(str(data[50:54]),16))/10
      errors=[]
      print (str("%.2f"%do)+","+str("%.2f"%ec)+","+str("%.2f"%ph)+","+str("%.2f"%temper))
      db = MySQLdb.connect(host="localhost",user="root",passwd="yfa",db="plant_yfa")
      cursorline = db.cursor()
      cursorline.execute("SELECT * FROM sensor_data where line = '"+line+"'")
      result_address = cursorline.fetchall()
      ph_check="1"
      ec_check="1"
      do_check="1"
      temperature_check="1"
      for i in result_address:
        ph_check=i[3]
        ec_check=i[6]
        do_check=i[9]
        temperature_check=i[12]
        ph_dataset_status=i[2]
        ec_dataset_status=i[5]
        do_dataset_status=i[8]
        temperature_dataset_status=i[11]

      db.close()
      do_state=int(do_dataset_status)
      ec_state=int(ec_dataset_status)
      ph_state=int(ph_dataset_status)
      temper_state=int(temperature_dataset_status)

      if do_check is '1':
        if do<do_max and do>do_min:
          do_state=0
          #print("do is ok")
          #Control_IO.Hand_switch(str(i),0)

        elif do>do_max and do_dataset_status is '0':
          do_state=1 
          Errorlog_Insert.writeerror(str(line),"null","null",str(ip),"domax",str("%.2f"%do),str("%.3f"%ec),str("%.2f"%ph),str("%.1f"%temper))
          #Control_IO.Hand_switch(str(i),1)

        elif do<do_min and do_dataset_status is '0':
          do_state=1
          Errorlog_Insert.writeerror(str(line),"null","null",str(ip),"domin",str("%.2f"%do),str("%.3f"%ec),str("%.2f"%ph),str("%.1f"%temper))
          #Control_IO.Hand_switch(str(i),1)
      else:
        do_state=0  

      if do_check is '1':
        if ec<ec_max and ec>ec_min:
          ec_state=0
          #print("ec is ok")
          #Control_IO.Hand_switch(str(i),0)
      
        elif ec>ec_max and ec_dataset_status is '0':
          ec_state=1
          Errorlog_Insert.writeerror(str(line),"null","null",str(ip),"ecmax",str("%.2f"%do),str("%.3f"%ec),str("%.2f"%ph),str("%.1f"%temper))
          #Control_IO.Hand_switch(str(i),1)
      
        elif ec<ec_min and ec_dataset_status is '0':
          ec_state=1
          Errorlog_Insert.writeerror(str(line),"null","null",str(ip),"ecmin",str("%.2f"%do),str("%.3f"%ec),str("%.2f"%ph),str("%.1f"%temper))
          #Control_IO.Hand_switch(str(i),1)
      else:
        ec_state=0 
      
      if ph_check is '1':
        if ph<ph_max and ph>ph_min:
          ph_state=0
          #print("ph is ok")
          #Control_IO.Hand_switch(str(i),0)
      
        elif ph>ph_max and ph_dataset_status is '0':
          ph_state=1
          Errorlog_Insert.writeerror(str(line),"null","null",str(ip),"phmax",str("%.2f"%do),str("%.3f"%ec),str("%.2f"%ph),str("%.1f"%temper))
          #Control_IO.Hand_switch(str(i),1)
      
        elif ph<ph_min and ph_dataset_status is '0':
          ph_state=1
          Errorlog_Insert.writeerror(str(line),"null","null",str(ip),"phmin",str("%.2f"%do),str("%.3f"%ec),str("%.2f"%ph),str("%.1f"%temper))
          #Control_IO.Hand_switch(str(i),1)
      else:  
        ph_state=0

      if temperature_check is '1':
        if temper<temper_max and temper>temper_min:
          temper_state=0
          #print("temper is ok")
          #Control_IO.Hand_switch(str(i),0)

        elif temper>temper_max and temperature_dataset_status is '0':
          temper_state=1
          Errorlog_Insert.writeerror(str(line),"null","null",str(ip),"tempmax",str("%.2f"%do),str("%.3f"%ec),str("%.2f"%ph),str("%.1f"%temper))
          #Control_IO.Hand_switch(str(i),1)

        elif temper<temper_min and temperature_dataset_status is '0':
          temper_state=1
          Errorlog_Insert.writeerror(str(line),"null","null",str(ip),"tempmin",str("%.2f"%do),str("%.3f"%ec),str("%.2f"%ph),str("%.1f"%temper))
          #Control_IO.Hand_switch(str(i),1)
      else:            
        temper_state=0
      Errorlog_Insert.write_water(line,str("%.2f"%ph),str(ph_state),str("%.3f"%ec),str(ec_state),str("%.2f"%do),str(do_state),str("%.1f"%temper),str(temper_state))
      Errorlog_Insert.status_connection(ip,port,address,place)
      Errorlog_Insert.clean_errortime(ip,port,address,place)
  
  except:
    if(int(Errorlog_Insert.find_errortime(ip,port,address,place))<6):
      Errorlog_Insert.add_errortime(ip,port,address,place)
      s.close()
    else:
      Errorlog_Insert.write_water(line,'-','1','-','1','-','1','-','1')
      Errorlog_Insert.status_disconnection(ip,port,address,place)
      s.close()
    
    #print "fuck!!!!!!!!"

def water_cheap(ip,port,i,line,ec_min,ec_max,do_min,do_max,ph_min,ph_max,temper_min,temper_max,address,place):
  address=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.connect(address)
  if i==0:
    s.send('\x00\x00\x00\x00\x00\x06\x01\x06\x00\x0c\x00\x00')
    time.sleep(1)
  if i==1:
    s.send('\x00\x00\x00\x00\x00\x06\x01\x06\x00\x0f\x00\x00')
    time.sleep(5)
  if i==2:
    s.send('\x00\x00\x00\x00\x00\x06\x01\x06\x00\x12\x00\x00')
    time.sleep(60)
  s.send('\x00\x00\x00\x00\x00\x06\x01\x03\x00\x00\x00\x03')
  time.sleep(1)
  data = s.recv(256)
  data=binascii.hexlify(data).decode()
  print(data)
  if i==0 and len(str(data))==50:
    ph=data[38:42]
    print ("ph="+str(float(ph)/100))
    temp=data[42:46]
    print ("Temp= "+str(float(temp)/10))
    Errorlog_Insert.write_water_phtemp("4",str(float(ph)/100),"0",str(float(temp)/10),"0")  
  elif i==1 and len(str(data))==50:
    ec=data[38:42]
    print ("ec= "+str(float(ec)/1000))
    Errorlog_Insert.write_water_ec("4",str(float(ec)/1000),"0")
  elif i==2 and len(str(data))==50:
    do=data[38:42]
    print ("do= "+str(float(do)/100))
    Errorlog_Insert.write_water_do("4",str(float(do)/1000),"0")
  print ("finish")
  
  time.sleep(1)
  s.close()

def enviro_modbus(ip,port,address,place):
   
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

  try: 
    s.connect(ipaddress) 
    s.settimeout(10) 
    s.send('\x00\x00\x00\x00\x00\x06\x05\x03\x00\x00\x00\x03')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    #print(data)
    s.close()
    if(len(str(data))==30):
      co2 = int(str(data[18:22]),16)
      temp = float(int(str(data[22:26]),16))/10
      hum =  float(int(str(data[26:30]),16))/10
      Errorlog_Insert.write_envior(str(co2),str(temp),str(hum),str(place))
      Errorlog_Insert.status_connection(ip,port,address,place)
      Errorlog_Insert.clean_errortime(ip,port,address,place)
  except:    
    if(int(Errorlog_Insert.find_errortime(ip,port,address,place))<6):
      Errorlog_Insert.add_errortime(ip,port,address,place)
      s.close()
    else:
      s.close()
      Errorlog_Insert.status_disconnection(ip,port,address,place)
      Errorlog_Insert.write_envior('-','-','-',place)
  
def wind_modbus(ip,port):
   
  address=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

  try:
    s.connect(address)
    s.settimeout(10)
    
    s.send('\x00\x00\x00\x00\x00\x06\x02\x03\x00\x06\x00\x02')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    print(data)
    s.close()
  except:
    s.close()
    #Errorlog_Insert.status_disconnection(ip,port)
    #Errorlog_Insert.write_envior('-','-','-')

def light_modbus(line,ip,port,address,place,light_max,light_min):
   
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  try:
    s.connect(ipaddress)
    s.settimeout(10)
    
    s.send('\x00\x00\x00\x00\x00\x06\x04\x03\x00\x00\x00\x02')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    s.close()
    
    #print(data[22:27])
    if(len(str(data))==26):
      light=float(int(str(data[22:26]),16))
      #print(light)
      db = MySQLdb.connect(host="localhost",user="root",passwd="yfa",db="plant_yfa")
      cursorline = db.cursor()
      cursorline.execute("SELECT * FROM sensor_data where line = '"+line+"'")
      result_address = cursorline.fetchall()
      light_check="1"
      for i in result_address:
        light_check=i[18]
        light_dataset_status=i[17]
      db.close()
      light_status=str(light_dataset_status)
      if light_check is '1':
        if(float(light)<float(light_max) and float(light)>float(light_min)):
          light_status='0'
          
        elif(float(light)>float(light_max) and light_check is '0'):
          light_status='1'
        
        elif(float(light)<float(light_min) and light_check is '0'):
          light_status='1'
      else:
        light_status='0'
        
      Errorlog_Insert.write_light(str(line),str("%.2f"%light),light_status)
      Errorlog_Insert.status_connection(ip,port,address,place)
      Errorlog_Insert.clean_errortime(ip,port,address,place)
  except:    
    if(int(Errorlog_Insert.find_errortime(ip,port,address,place))<6):
      Errorlog_Insert.add_errortime(ip,port,address,place)
      s.close()
    else:
      Errorlog_Insert.write_light(str(line),'-','1')
      Errorlog_Insert.status_disconnection(ip,port,address,place)
      s.close()
    #Errorlog_Insert.status_disconnection(ip,port)
    #Errorlog_Insert.write_envior('-','-','-')

def power_modbus(ip,port,address,place):
   
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

  try:
    s.connect(ipaddress)
    s.settimeout(10)
    
    s.send('\x00\x00\x00\x00\x00\x06\x1E\x03\x00\x0C\x00\x02')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    print(data)
    s.close()
    
    if(len(str(data))==26):
      power = float(int(str(data[18:26]),16))/10
      Errorlog_Insert.write_power(str(power))
      #print(str(power))
      Errorlog_Insert.status_connection(ip,port,address,place)
      Errorlog_Insert.clean_errortime(ip,port,address,place)
  except:    
    Errorlog_Insert.write_power("0.0")
    Errorlog_Insert.status_disconnection(ip,port,address,place)
    s.close()

def power_modbus_2f(ip,port,address,place):
   
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

  try:
    s.connect(ipaddress)
    s.settimeout(10)
    
    s.send('\x00\x00\x00\x00\x00\x06\x01\x03\x00\x0C\x00\x02')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    print(data)
    s.close()
    
    if(len(str(data))==26):
      power = (float(int(str(data[18:26]),16))/10)*4
      Errorlog_Insert.write_power_2f(str(power))
      #print(str(power))
      Errorlog_Insert.status_connection(ip,port,address,place)
      Errorlog_Insert.clean_errortime(ip,port,address,place)
  except:    
    Errorlog_Insert.write_power_2f("0.0")
    Errorlog_Insert.status_disconnection(ip,port,address,place)
    s.close()

def powernow_modbus(ip,port,address,place):
   
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

  try:
    s.connect(ipaddress)
    s.settimeout(10)
    
    s.send('\x00\x00\x00\x00\x00\x06\x1E\x03\x00\x09\x00\x02')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    print(data)
    s.close()
    
    if(len(str(data))==26):
      powernow = float(int(str(data[18:26]),16))/100
      print(powernow)
      Errorlog_Insert.write_powernow(str(powernow))
      Errorlog_Insert.status_connection(ip,port,address,place)
      Errorlog_Insert.clean_errortime(ip,port,address,place)
  except:    
    Errorlog_Insert.write_powernow("0.0")
    Errorlog_Insert.status_disconnection(ip,port,address,place)
    s.close()

def powernow_modbus_2f(ip,port,address,place):
   
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

  try:
    s.connect(ipaddress)
    s.settimeout(10)
    
    s.send('\x00\x00\x00\x00\x00\x06\x01\x03\x00\x09\x00\x02')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    print(data)
    s.close()
    
    if(len(str(data))==26):
      powernow = (float(int(str(data[18:26]),16))/100)*4
      print(powernow)
      Errorlog_Insert.write_powernow_2f(str(powernow))
      Errorlog_Insert.status_connection(ip,port,address,place)
      Errorlog_Insert.clean_errortime(ip,port,address,place)
  except: 
    Errorlog_Insert.write_powernow_2f("0.0")
    Errorlog_Insert.status_disconnection(ip,port,address,place)
    s.close()

def temhum_modbus(ip,port,address,place):
   
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

  try:
    s.connect(ipaddress)
    s.settimeout(10)
    
    s.send('\x00\x00\x00\x00\x00\x06\x07\x03\x00\x00\x00\x02')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    print(data)
    s.close()
    if(len(str(data))==26):
      tem=float(int(str(data[18:22]),16))/10
      hum=float(int(str(data[22:26]),16))/10
      print("tem: "+str(tem)+", hum: "+str(hum))
      Errorlog_Insert.write_envior('-',str(tem),str(hum),str(place))
      Errorlog_Insert.status_connection(ip,port,address,place)
      Errorlog_Insert.clean_errortime(ip,port,address,place)
  except:    
    if(int(Errorlog_Insert.find_errortime(ip,port,address,place))<6):
      Errorlog_Insert.add_errortime(ip,port,address,place)
      s.close()
    else:
      Errorlog_Insert.status_disconnection(ip,port,address,place)
      s.close()
    #Errorlog_Insert.status_disconnection(ip,port)
    #Errorlog_Insert.write_envior('-','-','-')

def envco2_modbus(ip,port):
   
  address=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

  try:
    s.connect(address)
    s.settimeout(10)
    
    s.send('\x00\x00\x00\x00\x00\x06\x08\x03\x00\x14\x00\x01')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    print(data)
    s.close()
  except:
    s.close()

def LCD_temhum_modbus(line,ip,port,address,place):
   
  print(line+","+ip+","+str(port)+","+str(address)+","+place)
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  try:
    s.connect(ipaddress)
    s.settimeout(10)
    
    s.send('\x00\x00\x00\x00\x00\x06\x06\x03\x00\x00\x00\x02')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    print(data)
    s.close()
    if(len(str(data))==26):
      tem=float(int(str(data[18:22]),16))/10
      hum=float(int(str(data[22:26]),16))/10
      print("tem: "+str(tem)+", hum: "+str(hum))
      Errorlog_Insert.write_soil(str(line),"-",'0',"-","0",str("%.1f"%hum),"0",str("%.1f"%tem),"0")
      Errorlog_Insert.status_connection(ip,port,address,place)
      Errorlog_Insert.clean_errortime(ip,port,address,place)
  except:
    if(int(Errorlog_Insert.find_errortime(ip,port,address,place))<6):
      Errorlog_Insert.add_errortime(ip,port,address,place)
      s.close()
    else:
      Errorlog_Insert.write_soil(str(line),'-','1','-','1','-','1','-','1')
      Errorlog_Insert.status_disconnection(ip,port,address,place)
      s.close()

def big_wind_modbus(line,ip,port,address,place,wind_max,wind_min):
   
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

  try:
    s.connect(ipaddress)
    s.settimeout(10)
    
    s.send('\x00\x00\x00\x00\x00\x06\x09\x03\x00\x00\x00\x01')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    print(data)
    s.close()
    if(len(str(data))==22):
      wind=float(int(str(data[18:22]),16))/10
      db = MySQLdb.connect(host="localhost",user="root",passwd="yfa",db="plant_yfa")
      cursorline = db.cursor()
      cursorline.execute("SELECT * FROM sensor_data where line = '"+line+"'")
      result_address = cursorline.fetchall()
      wind_check="1"
      for i in result_address:
        wind_check=i[15]
        wind_dataset_status=i[14]
      db.close()
      wind_status=str(wind_dataset_status)
      if wind_check is '1':
        if(float(wind)<float(wind_max) and float(wind)>float(wind_min)):
          wind_status='0'
          
        elif(float(wind)>float(wind_max) and wind_check is '0'):
          wind_status='1'
        
        elif(float(wind)<float(wind_min) and wind_check is '0'):
          wind_status='1'
      else:
        wind_status='0'  
      Errorlog_Insert.write_wind(line,str(wind),str(wind_status))
      Errorlog_Insert.status_connection(ip,port,address,place)
      Errorlog_Insert.clean_errortime(ip,port,address,place)
  except:    
    if(int(Errorlog_Insert.find_errortime(ip,port,address,place))<6):
      Errorlog_Insert.add_errortime(ip,port,address,place)
      s.close()
    else:
      Errorlog_Insert.write_wind(str(line),'-','1')
      Errorlog_Insert.status_disconnection(ip,port,address,place)
      s.close()

def waterlengh_modbus(line,ip,port,address,place,water_max,water_min):
   
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

  try:
    s.connect(ipaddress)
    s.settimeout(10)
    
    s.send('\x00\x00\x00\x00\x00\x06\x0a\x03\x01\x03\x00\x01')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    print(data)
    s.close()
    if(len(str(data))==22):
      waterlengh=float(int(str(data[18:22]),16))/1021*30
      print(waterlengh)
      print(str("%.1f"%waterlengh))
      db = MySQLdb.connect(host="localhost",user="root",passwd="yfa",db="plant_yfa")
      cursorline = db.cursor()
      cursorline.execute("SELECT * FROM sensor_data where line = '"+line+"'")
      result_address = cursorline.fetchall()
      waterlengh_check="1"
      for i in result_address:
        waterlengh_check=i[21]
        waterlengh_dataset_status=i[20]
      db.close()
      waterlengh_status=str(waterlengh_dataset_status)
      if light_check is '1':
        if(float(waterlengh)<float(water_max) and float(waterlengh)>float(water_min)):
          waterlengh_status='0'
          
        elif(float(waterlengh)>float(water_max) and waterlengh_check is '0'):
          waterlengh_status='1'
        
        elif(float(waterlengh)<float(water_min) and waterlengh_check is '0'):
          waterlengh_status='1'
        
      Errorlog_Insert.write_waterilenght(line,str("%.1f"%waterlengh),waterlengh_status)
      Errorlog_Insert.status_connection(ip,port,address,place)
      Errorlog_Insert.clean_errortime(ip,port,address,place)
  except:    
    if(int(Errorlog_Insert.find_errortime(ip,port,address,place))<6):
      Errorlog_Insert.add_errortime(ip,port,address,place)
      s.close()
    else:
      Errorlog_Insert.write_waterilenght(str(line),'-','1')
      Errorlog_Insert.status_disconnection(ip,port,address,place)
      s.close()

def water_test_2f(ip,port,line,ec_min,ec_max,ph_min,ph_max):
  ipaddress=(ip,port)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  ec_med=(float(ec_min)+float(ec_max))/2
  ph_med=(float(ph_min)+float(ph_max))/2
  print ec_med
  print ph_med
  Allline=str(int(line)+13)
  Error=0
  timewait=1
  ec_runtime=1
  ph_runtime=1
  if (int(line)%2==0):
    timewait=1.42
  else:
    timewait=1
  print ('mode: '+str(timewait))
  print (line)
  try:
    s.connect(ipaddress)
    s.settimeout(10)
    if int(line)>4: 
      s.send('\x00\x00\x00\x00\x00\x06\x01\x04\x00\x00\x00\x09')
    else:
      s.send('\x00\x00\x00\x00\x00\x06\x02\x04\x00\x00\x00\x09')
    time.sleep(2)
    data = s.recv(256)
    data=binascii.hexlify(data).decode()
    s.close()
    #print(data)
    if(len(str(data))==54):
      ph=float(int(str(data[18:22]),16))/100
      do=float(int(str(data[34:38]),16))/100
      ec=float(int(str(data[42:46]),16))/100
      temper=float(int(str(data[50:54]),16))/10
      print ('DO: '+str("%.2f"%do)+","+' EC: '+str("%.2f"%ec)+","+' PH: '+str("%.2f"%ph)+","+' Temp: '+str("%.2f"%temper))
      Errorlog_Insert.write_water(Allline,str("%.2f"%ph),"0",str("%.2f"%ec),"0",str("%.2f"%do),"0",str("%.2f"%temper),"0")
      #if int(time.strftime("%H", time.localtime()))>=8 and int(time.strftime("%H", time.localtime()))<17 and datetime.date.today().weekday()+1<6:
      if datetime.date.today().weekday()+1<6:
        if float("%.2f"%ec)<float(ec_min) and float("%.2f"%ec)>0.0:          
          Errorlog_Insert.writeerror(Allline,"null","null","Water","ecmin",do,ec,ph,temper)          
          #'''
          Control_IO.Test_DO('A_0'+line,'1')
          Control_IO.Test_DO('B_0'+line,'1')
          Control_IO.Test_DO('Mix0'+line,'1')
          Control_IO.Test_DO('A_Ma','1')
          Control_IO.Test_DO('B_Ma','1')
          #'''
          Control_IO.Switch_onoff('A_0'+line,"1","0")#
          Control_IO.Switch_onoff('B_0'+line,"1","0")#
          Control_IO.Switch_onoff('Mix0'+line,"1","0")#
          Control_IO.Switch_onoff('A_Ma',"1","0")#
          Control_IO.Switch_onoff('B_Ma',"1","0")#
          Control_IO.Update_status('Nothing',0,'ec',Allline)#
          #
          if (ec_med-float("%.2f"%ec))>=0.2:
            ec_runtime=120*2*timewait
          else:
            ec_runtime=120*(ec_med-float("%.2f"%ec))*10*timewait
          print ('ec: '+str(ec_runtime))
          Error=Error+1
        elif float("%.2f"%ec)>float(ec_max) and float("%.2f"%ec)>0.0:
          Errorlog_Insert.writeerror(Allline,"null","null","Water","ecmax",do,ec,ph,temper)          
        else:
          #'''
          Control_IO.Test_DO('A_Ma','0')
          Control_IO.Test_DO('B_Ma','0')
          Control_IO.Test_DO('A_0'+line,'0')
          Control_IO.Test_DO('B_0'+line,'0')
          #'''
          Control_IO.Switch_onoff('A_0'+line,"0","0")#
          Control_IO.Switch_onoff('B_0'+line,"0","0")#
          Control_IO.Switch_onoff('A_Ma',"0","0")#
          Control_IO.Switch_onoff('B_Ma',"0","0")#
          Control_IO.Update_status('Nothing',0,'stop',Allline)#
          print 'ec is ok'
        if float("%.2f"%ph)>float(ph_max) and float("%.2f"%ph)>0.0:
          Errorlog_Insert.writeerror(Allline,"null","null","Water","phmax",do,ec,ph,temper)          
          #'''
          Control_IO.Test_DO('Ac_0'+line,'1')
          Control_IO.Test_DO('Mix0'+line,'1')
          Control_IO.Test_DO('Ac_Ma','1')
          #'''
          Control_IO.Switch_onoff('Ac_0'+line,"1","0")#
          Control_IO.Switch_onoff('Mix0'+line,"1","0")#
          Control_IO.Switch_onoff('Ac_Ma',"1","0")#
          Control_IO.Update_status('Nothing',0,'ph',Allline)#
          #'''
          if (float("%.2f"%ph)-ph_med)>=0.2:
            ph_runtime=12*2*timewait
          else:
            ph_runtime=12*(float("%.2f"%ph)-ph_med)*10*timewait
          print ('ph: '+str(ph_runtime))
          Error=Error+1
        elif float("%.2f"%ph)<float(ph_min) and float("%.2f"%ph)>0.0: 
          Errorlog_Insert.writeerror(Allline,"null","null","Water","phmin",do,ec,ph,temper)          
          #'''  
          Control_IO.Test_DO('Ba_0'+line,'1')
          Control_IO.Test_DO('Mix0'+line,'1')
          Control_IO.Test_DO('Ba_Ma','1')
          #'''
          Control_IO.Switch_onoff('Ba_0'+line,"1","0")
          Control_IO.Switch_onoff('Mix0'+line,"1","0")
          Control_IO.Switch_onoff('Ba_Ma',"1","0")
          Control_IO.Update_status('Nothing',0,'ph',Allline)#
          #
          if (ph_med-float("%.2f"%ph))>=0.2:
            ph_runtime=12*2*timewait
          else:
            ph_runtime=12*(ph_med-float("%.2f"%ph))*10*timewait
          print ('ph: '+str(ph_runtime))
          Error=Error+1
        else:
          print ('ph is ok')
          #'''
          Control_IO.Test_DO('Ac_Ma','0')
          Control_IO.Test_DO('Ac_0'+line,'0')
          Control_IO.Test_DO('Ba_Ma','0')
          Control_IO.Test_DO('Ba_0'+line,'0')
          #'''
          Control_IO.Switch_onoff('Ac_0'+line,"0","0")#
          Control_IO.Switch_onoff('Ac_Ma',"0","0")#
          Control_IO.Switch_onoff('Ba_0'+line,"0","0")#
          Control_IO.Switch_onoff('Ba_Ma',"0","0")#
          Control_IO.Update_status('Nothing',0,'stop',Allline)#      
        if float("%.2f"%ec)<=0.0:
          Errorlog_Insert.writeerror(Allline,"null","null","Water","eczero",do,ec,ph,temper)          
        if Error>=1:
          if Error>1:
            Control_IO.Update_status('Nothing',0,'both',Allline)#      
          if ec_runtime>ph_runtime:
            time.sleep(ph_runtime)
            #'''
            Control_IO.Test_DO('Ac_Ma','0')
            Control_IO.Test_DO('Ac_0'+line,'0')
            Control_IO.Test_DO('Ba_Ma','0')
            Control_IO.Test_DO('Ba_0'+line,'0')
            #'''
            Control_IO.Switch_onoff('Ac_0'+line,"0","0")#
            Control_IO.Switch_onoff('Ac_Ma',"0","0")#
            Control_IO.Switch_onoff('Ba_0'+line,"0","0")#
            Control_IO.Switch_onoff('Ba_Ma',"0","0")#
            time.sleep(ec_runtime-ph_runtime)
            #'''
            Control_IO.Test_DO('A_Ma','0')
            Control_IO.Test_DO('B_Ma','0')
            Control_IO.Test_DO('A_0'+line,'0')
            Control_IO.Test_DO('B_0'+line,'0')
            #'''
            Control_IO.Switch_onoff('A_0'+line,"0","0")#
            Control_IO.Switch_onoff('B_0'+line,"0","0")#
            Control_IO.Switch_onoff('A_Ma',"0","0")#
            Control_IO.Switch_onoff('B_Ma',"0","0")#
            Control_IO.Update_status('Nothing',0,'mix',Allline)#      
            time.sleep((ec_runtime*1.5)-ec_runtime)
            Control_IO.Test_DO('Mix0'+line,'0')
            Control_IO.Switch_onoff('Mix0'+line,"0","0")#
            Control_IO.Update_status('Nothing',0,'stop',Allline)#      
          else:
            time.sleep(ec_runtime)
            #'''
            Control_IO.Test_DO('A_Ma','0')
            Control_IO.Test_DO('A_0'+line,'0')
            Control_IO.Test_DO('B_Ma','0')
            Control_IO.Test_DO('B_0'+line,'0')
            #'''
            Control_IO.Switch_onoff('A_0'+line,"0","0")#
            Control_IO.Switch_onoff('B_0'+line,"0","0")#
            Control_IO.Switch_onoff('A_Ma',"0","0")#
            Control_IO.Switch_onoff('B_Ma',"0","0")#
            time.sleep(ph_runtime-ec_runtime)
            #'''
            Control_IO.Test_DO('Ac_Ma','0')
            Control_IO.Test_DO('Ba_Ma','0')
            Control_IO.Test_DO('Ac_0'+line,'0')
            Control_IO.Test_DO('Ba_0'+line,'0')
            #'''
            Control_IO.Switch_onoff('Ac_0'+line,"0","0")#
            Control_IO.Switch_onoff('Ba_0'+line,"0","0")#
            Control_IO.Switch_onoff('Ac_Ma',"0","0")#
            Control_IO.Switch_onoff('Ba_Ma',"0","0")#
            Control_IO.Update_status('Nothing',0,'mix',Allline)#      
            time.sleep((ph_runtime*1.5)-ph_runtime)
            Control_IO.Test_DO('Mix0'+line,'0')
            Control_IO.Switch_onoff('Mix0'+line,"0","0")#
            Control_IO.Update_status('Nothing',0,'stop',Allline)#      
        else:
            print('Every thing is ok')
            Control_IO.Update_status('Nothing',0,'stop',Allline)#      
      else:
        print('Not yet time')
  except Exception as e:
    print(e)
    print("Error")
    #'''
    Control_IO.Test_DO('Ac_Ma','0')
    Control_IO.Test_DO('Ac_0'+line,'0')
    Control_IO.Test_DO('Ba_Ma','0')
    Control_IO.Test_DO('Ba_0'+line,'0')
    Control_IO.Test_DO('A_Ma','0')
    Control_IO.Test_DO('B_Ma','0')
    Control_IO.Test_DO('A_0'+line,'0')
    Control_IO.Test_DO('B_0'+line,'0')
    Control_IO.Test_DO('Mix0'+line,'0')
    #'''
    Control_IO.Switch_onoff('A_0'+line,"0","0")#
    Control_IO.Switch_onoff('B_0'+line,"0","0")#
    Control_IO.Switch_onoff('A_Ma',"0","0")#
    Control_IO.Switch_onoff('B_Ma',"0","0")#
    Control_IO.Switch_onoff('Ac_0'+line,"0","0")#
    Control_IO.Switch_onoff('Ba_0'+line,"0","0")#
    Control_IO.Switch_onoff('Ac_Ma',"0","0")#
    Control_IO.Switch_onoff('Ba_Ma',"0","0")#
    Control_IO.Switch_onoff('Mix0'+line,"0","0")#
    Control_IO.Update_status('Nothing',0,'stop',Allline)#      
