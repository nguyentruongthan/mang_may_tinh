import socket
import sys

#port use to connect with server process in this computer
PORT_LOCAL = 8888
    
#connect to server for send request
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

if __name__ == "__main__":
    
    #init ip_addr 
    IP_ADDR = socket.gethostbyname(socket.gethostname())
    
    
    #using args for identify lname and fname
    #TODO
    if(len(sys.argv) > 1):
        print("Syntax error: more than 1 argument for discover funcion")
        exit()
    
    #connect to local host
    socket_process_server = connect((IP_ADDR, PORT_LOCAL))
    
    #send message to process server

    #method:discover\n
    #hostname:<host_name>
    message_str = "method:list_clients\n"
    message_bytes = message_str.encode()
    #send to process client in local computer
    socket_process_server.send(message_bytes)
    
    clients = socket_process_server.recv(1024).decode()
    print(clients)
    
    socket_process_server.close()
    
    

    
    
    
    