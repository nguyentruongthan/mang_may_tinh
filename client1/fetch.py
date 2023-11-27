import socket
import sys

IP_ADDR: str = ""

#port use to connect with client process in this computer
PORT_LOCAL = 8888

#path to address of folder respontory
#TODO
PATH_RESPONTORY = "C:/Users/than/Desktop/client1/"

    

def connect(addr:tuple[str, int]):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(addr)
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
    fname = sys.argv[1]
    
    #connect to local host
    socket_process_client = connect((IP_ADDR, PORT_LOCAL))
    
    #send message to server

    #method:fetch\n
    #fname:<fname>
    message_str = get_message_fetch(fname)
    message_bytes = message_str.encode()
    #send to process client in local computer
    socket_process_client.send(message_bytes)
    socket_process_client.close()
    

    
    
    
    