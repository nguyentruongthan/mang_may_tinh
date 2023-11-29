import socket
import os

IP_ADDR: str = ""

#port use to connect with client process in this computer
PORT_LOCAL = 8888

    
#connect to client for send request
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

#convert publish request to standard form   
def get_message_exit() -> str:
    message = "method:exit"
    
    #message:
    #method:exit
    return message
        
    
if __name__ == "__main__":
    #init ip_addr 
    IP_ADDR = socket.gethostbyname(socket.gethostname())
    
    #connect to local host
    socket_process_client = connect((IP_ADDR, PORT_LOCAL))

    #send message to process client

    #method:exit
    message_str = get_message_exit()
    #send to process client in local computer
    socket_process_client.send(message_str.encode())
    pid = socket_process_client.recv(1024).decode()

    
    socket_process_client.close()
    
    os.system(f'taskkill /pid {pid} /f')
    

    
    
    
    