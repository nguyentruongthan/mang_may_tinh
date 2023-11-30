import socket
import sys

PORT_CLIENT = 7777

#convert ping request to standard form   
def get_message_ping(host_name:str) -> str:
    message = "method:ping"
    
    #message:
    #method:ping
    
    return message

def ping_func(host_name) -> str:
    result = ""
    for i in range(3):
        try:
            #connect to host name
            #host_name is host name of client we want to ping
            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.settimeout(2)
            socket_client.connect((host_name, PORT_CLIENT))
            socket_client.gettimeout()
            #Get message for ping
            message = get_message_ping(host_name)
            socket_client.send(message.encode())
            data = socket_client.recv(1024).decode()
            if data == "OKE":
                print(f"{host_name} is existing")
                socket_client.close()
                result += f"{i}. {host_name} is existing\n"
            else: 
                result += f"{i}. Loss data response"
                print("Loss data response")
                socket_client.close()
        except socket.timeout:
            print("Time out")
            result += f"{i}. Time out\n"
        except:
            result += f"{i}. Error\n"
    return result

if __name__ == "__main__":
    if(len(sys.argv) > 2):
        print("Syntax error: more than 1 argument for discover funcion")
        exit()
    host_name = sys.argv[1]
    
    ping_func(host_name)

    
    
    
    
    

    
    
    
    