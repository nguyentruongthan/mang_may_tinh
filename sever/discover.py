import socket
import sys

IP_ADDR: str = ""

#port use to connect with server process in this computer
PORT_LOCAL = 8888
    
#connect to server for send request
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

#convert discover request to standard form   
def get_message_discover(host_name:str) -> str:
    message = "method:discover\n"
    message += "hostname:"
    message += host_name
    
    #message:
    #method:discover\n
    #hostname:<host_name>
    
    return message
def discover_func(host_name:str):
    #init ip_addr 
    IP_ADDR = socket.gethostbyname(socket.gethostname())
    #connect to local host
    socket_process_server = connect((IP_ADDR, PORT_LOCAL))
    #message = method:discover\nhostname:<host_name>
    message = get_message_discover(host_name)
    #send to process client in local computer
    socket_process_server.send(message.encode())
    #recv size of filenames from server process
    size = socket_process_server.recv(1024).decode()
    size = int(size)
    #send signal to server
    socket_process_server.send("OKE".encode())
    #recv fnames from server
    fnames = ""
    while size > 0:
        fnames += socket_process_server.recv(1024).decode()
        size -= 1024
    if fnames == "":
        fnames = "Empty"
   
    print(fnames)
    
    file = open("data\\" + host_name + ".txt", 'w')
    file.write(fnames)
    file.close()
    
    socket_process_server.close()
    

if __name__ == "__main__":
    
    
    
    #using args for identify lname and fname
    #TODO
    if(len(sys.argv) > 2):
        print("Syntax error: more than 1 argument for discover funcion")
        exit()
    host_name = sys.argv[1]
    
    discover_func(host_name)
   
    

    
    
    
    