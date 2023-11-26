import socket
import os
import shutil
import sys

IP_ADDR: str = ""

#port use to connect with client process in this computer
SEFT_PORT = 9999

#path to address of folder respontory
PATH_RESPONTORY = "C:/Users/than/Desktop/client1/"
    
#connect to client for send request
def connect(addr:tuple[str, int]):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(addr)
        print(f"Connected to {addr}")
    except ConnectionRefusedError as cre:
        print("Host doesn't exist")
    except TypeError as Type:
        print("Syntax error")
    return s

#convert publish request to standard form   
def get_message_publish(fname:str) -> str:
    message = "method:publish\n"
    message += "fname:"
    message += fname
    
    #message:
    #method:publish\n
    #fname:<fname>
    
    return message

#check file lname is exist in file system
def check_lname(lname: str):
    #check for lname exist in folder of clinet
    is_lname_exist = os.path.exists(lname)
    #if file not exist
    if not is_lname_exist:
        print(f"File {lname} doesn't exist")
        exit()
    
if __name__ == "__main__":
    
    #init ip_addr 
    IP_ADDR = socket.gethostbyname(socket.gethostname())
    
    
    #using args for identify lname and fname
    #TODO
    if(len(sys.argv) > 3):
        print("Syntax error: more than 2 argument for publish funcion")
        exit()
    lname = sys.argv[1]
    fname = sys.argv[2]
    
    #check fname is exist
    check_lname()
    #copy lname to client's repository
    shutil.copyfile(lname, PATH_RESPONTORY + fname)
    
    #connect to local host
    socket_process_client = connect((IP_ADDR, SEFT_PORT))
    
    
    
    #send message to process client

    #method:publish\n
    #fname:<fname>
    message_str = get_message_publish(fname)
    message_bytes = message_str.encode()
    #send to process client in local computer
    socket_process_client.send(message_bytes)
    
    socket_process_client.close()
    

    
    
    
    