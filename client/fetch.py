import socket
import sys
import os

IP_ADDR: str = ""

#port use to connect with client process in this computer
PORT_LOCAL = 8888

#path to address of folder respontory
#TODO

    

def connect(addr:tuple[str, int]):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(3)
        s.connect(addr)
        s.gettimeout()
        # print(f"Connected to {addr}")
    except ConnectionRefusedError as cre:
        print("Host doesn't exist")
    except TypeError as Type:
        print("Syntax error")
    return s
   
def get_message_fetch(fname:str) -> str:
    message = "method:fetch\n"
    message += "fname:"
    message += fname
    
    #message:
    #method:fetch\n
    #fname:<fname>
    
    return message

if __name__ == "__main__":
    
    #init ip_addr 
    IP_ADDR = socket.gethostbyname(socket.gethostname())
    
    
    #using args for identify lname and fname
    #TODO
    number_of_fname = len(sys.argv) - 1
    if number_of_fname < 1:
        print("Syntax Error: Less than one argument") 
    fnames = sys.argv[1:]
    for fname in fnames:
        #check file fname is exist in file system
        if os.path.exists("data\\" + fname):
            print(f"File {fname} is existing")
            exit()
        #connect to local host
        socket_process_client = connect((IP_ADDR, PORT_LOCAL))
        
        #send message to process client

        #method:fetch\n
        #fname:<fname>
        message = get_message_fetch(fname)
        #send to process client in local computer
        socket_process_client.send(message.encode())

        result = socket_process_client.recv(1024).decode()
        print(result)
        socket_process_client.close()
    
    

    
    
    
    