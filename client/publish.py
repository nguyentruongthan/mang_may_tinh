import socket
import os
import shutil
import sys
import ntpath

#connect to client for send request
def connect(addr:tuple[str, int]):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.settimeout(3)
            s.connect(addr)
            s.gettimeout()
            print(f"Connected to {addr}")
        except ConnectionRefusedError:
            print(f"Don't exist host {addr}")
            exit()
        except socket.timeout:
            print("Time Out")
            exit()
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
def check_lname(lname: str) -> bool:
    #check for lname exist in folder of clinet
    is_lname_exist = os.path.exists(lname)
    #if file not exist
    return is_lname_exist
        
def publish_func(lname, fname) -> str:
    IP_ADDR = socket.gethostbyname(socket.gethostname())
    PORT_LOCAL = 8888
    
    lname = lname.replace(os.sep, ntpath.sep)
    #check fname is exist
    if not check_lname(lname):
        result = f"File {lname} doesn't exist"
        print(result)
        return result
    
    #connect to local host
    socket_process_client = connect((IP_ADDR, PORT_LOCAL))

    #send message to process client

    #method:publish\n
    #fname:<fname>
    message_str = get_message_publish(fname)
    #send to process client in local computer
    socket_process_client.send(message_str.encode())
    socket_process_client.settimeout(3)
    result = socket_process_client.recv(1024).decode()
    socket_process_client.gettimeout()
    print(result)
    if result == "OKE":
        #copy lname to client's repository   
        shutil.copyfile(lname, "data/" + fname)
    socket_process_client.close()
    return result
    
if __name__ == "__main__":
    
    #using args for identify lname and fname
    #TODO
    if(len(sys.argv) != 3):
        print("Syntax error: <lname> <fname>")
        exit()
    lname = sys.argv[1]
    fname = sys.argv[2]
    
    
    
    publish_func(lname, fname)
    

    
    
    
    