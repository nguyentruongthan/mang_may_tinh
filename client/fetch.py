import socket
import sys
import os
    

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
   
def get_message_fetch(fname:str) -> str:
    message = "method:fetch\n"
    message += "fname:"
    message += fname
    
    #message:
    #method:fetch\n
    #fname:<fname>
    
    return message
def fetch_func(file_names) -> str:
    IP_ADDR = socket.gethostbyname(socket.gethostname())
    PORT_LOCAL = 8888
    
    if len(file_names) < 1:
        result = "Syntax Error: Less than one argument"
        print(result)
        return result
    
    result_total = ""
    for fname in file_names:
        #check file fname is exist in file system
        if os.path.exists("data\\" + fname):
            print(f"File {fname} is existing")
            result_total += f"File {fname} is existing\n" 
            continue
        #connect to local host
        socket_process_client = connect((IP_ADDR, PORT_LOCAL))
        
        #send message to process client

        #method:fetch\n
        #fname:<fname>
        message = get_message_fetch(fname)
        #send to process client in local computer
        socket_process_client.send(message.encode())
        socket_process_client.settimeout(None)
        result = socket_process_client.recv(1024).decode()
        print(result)
        result_total += f"{result}\n"
        socket_process_client.close()
    return result_total

if __name__ == "__main__":
    
    #init ip_addr 
    IP_ADDR = socket.gethostbyname(socket.gethostname())
    
    
    #using args for identify lname and fname
    #TODO
    file_names = sys.argv[1:]
    fetch_func(file_names)
    
    
    

    
    
    
    