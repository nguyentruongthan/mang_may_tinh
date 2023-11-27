import socket
import sys

PORT_CLIENT = 7777

#convert ping request to standard form   
def get_message_ping(host_name:str) -> str:
    message = "method:ping\n"
    message += "hostname:"
    message += host_name
    
    #message:
    #method:ping\n
    #hostname:<host_name>
    
    return message

if __name__ == "__main__":
    
    #using args for identify host_name
    #TODO
    if(len(sys.argv) > 2):
        print("Syntax error: more than 1 argument for discover funcion")
        exit()
    host_name = sys.argv[1]
    
    
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #connect to host name
    #host_name is host name of client we want to ping
    try:
        socket_client.connect((host_name, PORT_CLIENT))
        message = get_message_ping(host_name)
        socket_client.send(message.encode())
        data = socket_client.recv(1024).decode()
        if data == "OKE":
            print(f"{host_name} is existing")
    except ConnectionRefusedError as cre:
        print("Time out")
    
    
    
    
    
    

    
    
    
    