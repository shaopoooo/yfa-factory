import socket
import time
import MySQLdb

def open_alarm(): 
  address=("192.168.99.12",8080)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.connect(address)
  times=0
  st='off1'
  byt=st.encode()
  s.send(byt)
  time.sleep(1)

  while(1):
    #data = s.recv(512)
    #print ('the data reiveed is',data)
     
    #switch = input ("1 is open / 2 is close: ")   
    #if switch is '1':
      #print('open')
      #st='on1:00'
    #else:
      #print('close')
      #st='off1'
    if times%2==0:
      st='on2:00'
      byt=st.encode()
      s.send(byt)
      #print("fuck 1")

      time.sleep(0.5)
   
    else:
      st='off2'
      byt=st.encode()
      s.send(byt)
      #print("fuck 2")
      time.sleep(0.5)

      db = MySQLdb.connect(host="localhost",user="root",passwd="yfa",db="plant_yfa")
      cursor = db.cursor()
      cursor.execute("SELECT * FROM alarm_data where ip = '192.168.99.12' and port = '8080' and class = 'Com1'")
      result = cursor.fetchall()
      for i in result:
        status = i[4] 
      if status=="on" and times>6:
        print(status+"fuck!!!!!!!!!!!!!!!!!!!!!!!")
        break
      db.close()
    times=times+1
  st='on1:00'
  byt=st.encode()
  s.send(byt)
  time.sleep(1)
  s.close()

def close_alarm(): 
  address=("192.168.99.12",8080)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.connect(address)
  data = s.recv(512)
  print ('the data reiveed is',data)
  st='off2'
  byt=st.encode()
  s.send(byt)
  time.sleep(0.5)
  #print("fuck 2")
  s.close()

  #print("Nothing")


def is_safe(): 
  address=("192.168.99.12",8080)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.connect(address)
  data = s.recv(512)
  print ('the data reiveed is',data)
  st='on1:00'
  byt=st.encode()
  s.send(byt)
  time.sleep(1)
  #print("fuck 2")
  s.close()

  #print("Nothing")


def not_safe(): 
  address=("192.168.99.12",8080)
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.connect(address)
  data = s.recv(512)
  print ('the data reiveed is',data)
  st='off1'
  byt=st.encode()
  s.send(byt)
  time.sleep(1)
  #print("fuck 2")
  s.close() 
