import socket
import threading


PORT_CLIENT = 7777
PORT_LOCAL = 8888
PORT_SERVER = 9999

class client:
    
    # path for respontory
    __path_dir: str
    
    #socket server
    __socket_server: socket.socket
    __socket_client: socket.socket
    __socket_local: socket.socket
    
    def __init__(seft, ip_addr: str, path_dir: str):
        

        seft.__path_dir = path_dir
        #create socket for IPv4
        seft.__socket_server = seft.connect((ip_addr, PORT_SERVER))
        
        #listen from other client to send file for fetch
        #or from local when we use publish and fetch method in cmd
        seft.__socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        seft.__socket_client.bind(("", PORT_CLIENT))
        seft.__socket_client.listen(100)
        
        seft.__socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_ip = socket.gethostbyname(socket.gethostname())
        seft.__socket_client.bind((local_ip, PORT_LOCAL))
        seft.__socket_client.listen(1)
        
        seft.run()
        
    
    def cmd(seft):
        while 1:
            s, _ = seft.__socket_local.accept()
            thread_cmd = threading.Thread(target = seft.handle_cmd, args = (s))
            thread_cmd.start()
            thread_cmd.join()
            
    def handle_cmd(seft, socket_local:socket.socket):
        message = socket_local.recv(1024).decode()
        obj_request = seft.split_message(message)
        method = obj_request[0]
        
        if method == "publish":
            fname = obj_request[1]
            if seft.publish(socket_local, fname) == 1:
                socket_local.send("OKE".encode())
            else:
                socket_local.send("ERROR".encode())
        elif method == "fetch":
            fname = obj_request[1]
            seft.fetch(socket_local, fname)
        socket_local.close()
    #thread always listen connect from client 
    def accepting(seft):
        while 1:
            s, add = seft.__socket_client.accept()
            print(f"Connected from {add}")
            thread_client = threading.Thread(target = seft.handle_client, args = (s))
            thread_client.start()
    #create new thread when server accept new connect from another client
    def handle_client(seft, client):
        while 1:
            request = client.recv(1024)
            if not request:
                print(f"Disconnect from {client.getpeername()}")
                client.close()
                exit()
                
            seft.handle_request(client, request.decode())
            
    
    def split_method(seft, message:str) -> str:
        #message:   method:<method>
        obj_of_line = message.split(":")
        if len(obj_of_line) == 2:
            #return <method>
            return obj_of_line[1]
        return ""
    
    def split_fname(seft, message:str) -> str:
        #message:   fname:<fname>
        obj_of_line = message.split(":")
        if len(obj_of_line) == 2:
            #return <fname>
            return obj_of_line[1]
        return ""
    def split_host_name(seft, message:str) -> str:
        #message:   hostname:<hostname>
        obj_of_line = message.split(":")
        if len(obj_of_line) == 2:
            #return <hostname>
            return obj_of_line[1]
        return ""
    
    def split_message(seft, message:str) -> list[str]:
        #message:   method:<method>\n 
        #           ............
        result_list = []
        lines = message.split('\n')
        method = seft.split_method(lines[0])
        if method == "":
            return []
        
        result_list.append(method)
        if ((method == "publish") | (method == "fetch")):
            fname = seft.split_fname(lines[1])
            result_list.append(fname)
        return result_list

    def handle_request_error(seft):
        print("Request Error")
                
    def handle_request(seft, socket_client:socket.socket, message:str):
        #messaeg (str): method:<method>\n 
        #               ...............
        obj_request = seft.split_message(message)
        method = obj_request[0]
        
        if method == "fetch":
            fname = obj_request[1]
            seft.send_file(socket_client, fname)
        elif method == "ping":
            socket_client.send("OKE".encode())
        else:
            seft.handle_request_error()
            socket_client.send("ERROR".encode()) 
        socket_client.close()
        
    
    def check_ip_syntax(seft, ip:str) -> bool:
        obj_ip = ip.split(".")
        if len(obj_ip) != 4:
            print(f"Length is {len(obj_ip)}")
            return False
        for i in obj_ip:
            try: 
                i = int(i)
            except ValueError:
                print(f'{i} is not number')
                exit()
            if type(i) != int:
                print("Type error")
                return False
            if i < 0 | i > 255:
                print("Range error")
                return False
        return True       

    def connect(seft, addr:tuple[str, int]):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        ip = addr[0]
        if not seft.check_ip_syntax(ip):
            print("IP syntax error")
            exit()
        try:
            s.connect(addr)
            print(f"Connected to {addr}")
        except ConnectionRefusedError:
            print(f"Don't exist host {addr}")
            exit()
        return s
    
        
    def send_file(seft, client:socket.socket, file_name:str):
        #open file
        file = open(file_name, "rb")
        
        #read file
        data = file.read()
        
        size = len(data)
        
        #send size of file to client
        client.send(size)
        #wait for recv "OKE" from another client
        signal = client.recv(1024).decode()
        if signal == "OKE":
            #send data of file to server
            client.sendall(data)
        file.close()
    
    def recv_file(seft, client:socket.socket, file_name:str):
        #we will recv and write to file continuous 
        #we stop until size of file less or equal to 0
        
        #recv size of file
        size = client.recv(1024).decode()
        client.send("OKE".encode())
        #open file name which received from client
        file = open(seft.__path_dir + file_name, "wb")
        file_bytes = b''
        while size >= 0:
            data = client.recv(1024)    
            file_bytes += data
        
        file.write(file_bytes)    
            
        file.close()
        client.close()
    
    def message_for_fetch(seft, fname) -> bytes:
        message = ""
        message += "METHOD:fetch" 
        message += "\nfname:"
        message += fname
        
        #METHOD:fetch
        #fname:<fname>
        return message
    
    #return list of client which has file
    def recv_list_clients_for_fetch(seft) -> list[str]:
        
        message = seft.__socket_server.recv(1024).decode()
        
        if message == "NO":
            return []
        
        return message.split("\n")
        
    def choose_client_for_fetch(seft, list_clients:list[str]) -> str:
        #we can choose client with another way
        #TODO
        
        return list_clients[0]
        
    def fetch_to_client(seft, socket_client_fetch:socket.socket, fname:str):
        message = seft.message_for_fetch(fname)
        #message = 
        #METHOD:fetch
        #fname:<fname>
        socket_client_fetch.send(message.encode())
        
        #receive file from client who has file <fname>
        seft.recv_file(socket_client_fetch, fname)
        
    
    def fetch_to_server(seft, fname:str) -> list[str]:
        #send fname to server for recv list of client who has fname
        message = seft.message_for_fetch(fname)

        seft.__socket_server.send(message.encode())
        
        
        #recv list of client who has fname
        list_clients = seft.recv_list_clients_for_fetch()
        
        return list_clients
        

    def fetch(seft, fname: str):
        #send message to server and get list of clients who has file <fname>
        list_clients = seft.fetch_to_server(fname)
        
        #if no exist any other client has file
        if len(list_clients) == 0:
            return
        
        #choose client for fetch file from it
        client_ip = seft.choose_client_for_fetch(list_clients)
        
        #connect to this client
        client_fetch = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_fetch.connect((client_ip, 7777))
        
        #recv file from this client
        seft.fetch_to_client(client_fetch, fname)
        
        client_fetch.close()
        
        
    def run(seft):
        seft.accepting()
        
        
    
    
    def get_message_publish(fname:str) -> str:
        message = "method:publish\n"
        message += "fname:"
        message += fname
        
        #message:
        #method:publish\n
        #fname:<fname>
        
        return message

    def publish(seft, fname:str) -> int:
        message = seft.get_message_publish(fname)
        seft.__socket_server.send(message.encode())
        #wait for server send response
        #TODO
        try:
            seft.__socket_server.settimeout(5)
            signal = seft.__socket_server.recv(1024).decode()
            if signal == "OKE":
                return 1
        except socket.timeout:
            print("Publish method didn't receive response from server!")
            
        return 0

    
if __name__ == "__main__":
    ip_server = socket.gethostbyname(socket.gethostname())
    path_dir = "C:/Users/than/Desktop/client1/"
    
    obj_client = client(ip_server, path_dir)
    
    
    
        
        
    
        
        
        
    
    
    
    
    
    
    