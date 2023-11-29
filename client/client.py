import socket
import threading
import sys
import os 

PORT_CLIENT = 7777
PORT_LOCAL = 8888
PORT_SERVER = 9999

class client:
    
    
    #socket server
    __socket_server: socket.socket
    __socket_client: socket.socket
    __socket_local: socket.socket
    
    def __init__(seft, ip_addr: str):
                
        #publish all file in local respostory to server
        list_files = os.listdir("data")
        for file in list_files:
            result = seft.publish(file)
            if result == 0:
                print("Error when publish file init")
                exit()
        #listen from other client to send file for fetch
        #or from local when we use publish and fetch method in cmd
        seft.__socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        seft.__socket_client.bind(("", PORT_CLIENT))
        seft.__socket_client.listen(100)
        
        #init socket_local for handle command from cmd
        seft.__socket_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        seft.__socket_local.bind(("", PORT_LOCAL))
        seft.__socket_local.listen(1)
        
        
        
    #handle request from cmd
    def cmd(seft):
        while 1:
            #accept connect from cmd
            socket_local, _ = seft.__socket_local.accept()
            seft.handle_cmd(socket_local)
            #if finish handle request
            #-> close connect 
            socket_local.close()
            
    def handle_cmd(seft, socket_local: socket.socket):
        while 1:
            message = socket_local.recv(1024)
            #if disconnect -> close socket_local
            if not message:
                break
            #if socket_local doesn't send request 
            #-> continue for socket_local send request
            if len(message) == 0: continue
            message = message.decode()

            obj_request = seft.split_message(message)
            method = obj_request[0]
            
            if method == "publish":
                fname = obj_request[1]
                result = seft.publish(fname)
                if result == 1:
                    socket_local.send("OKE".encode())
                else:
                    socket_local.send("ERROR".encode())
            elif method == "fetch":
                fname = obj_request[1]
                seft.fetch(socket_local, fname)
            else:
                socket_local.send("ERROR".encode())
    
    #thread always listen connect from client 
    def accepting(seft):
        while 1:
            s, add = seft.__socket_client.accept()
            print(f"Connected from {add}")
            #create new thread for handle new client
            thread_client = threading.Thread(target = seft.handle_client, args = (s, ))
            thread_client.start()
            
    #create new thread when client accept new connect from another client
    def handle_client(seft, socket_client:socket.socket):
            request = socket_client.recv(1024)
            if not request: 
                socket_client.close()
            else: 
                seft.handle_request(socket_client, request.decode())
        
            
    
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
                
    def handle_request(seft, socket_client:socket.socket, message:str):
        if len(message) == 0: return
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
    
        
    def send_file(seft, socket_client:socket.socket, file_name:str):
        print(f"Send {file_name} to {socket_client.getpeername()[0]}")
        #open file
        file = open("data\\" + file_name, "rb")
        
        #read file
        data = file.read()
        
        size = str(len(data))
        
        #send size of file to client
        socket_client.send(size.encode())
        #wait for recv "OKE" from another client
        signal = socket_client.recv(1024).decode()
        print(f"Recv signal: {signal}")
        if signal == "OKE":
            print("Start send file ...")
            #send data of file to server
            socket_client.sendall(data)
            print(f"Complete send {file_name} to {socket_client.getpeername()[0]}")
        
        file.close()
    
    def recv_file(seft, client:socket.socket, file_name:str):
        #we will recv and write to file continuous 
        #we stop until size of file less or equal to 0
        
        #recv size of file
        size = int(client.recv(1024).decode())
        print(f"Size of file {file_name} is {size}")
        client.send("OKE".encode())
        #open file name which received from client
        file = open("data\\" + file_name, "wb")
        print(f"Open file {file_name}")
        file_bytes = b''
        while size >= 0:
            data = client.recv(1024)    
            file_bytes += data
            size -= 1024
        
        file.write(file_bytes)    
        print(f"Recv file {file_name} completed")
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
        

    def fetch(seft, socket_local:socket.socket, fname: str):
        seft.__socket_server.connect((ip_server, PORT_SERVER))
        #send message to server and get list of clients who has file <fname>
        #message = method:fetch\nfname:<fname>
        message = seft.message_for_fetch(fname)
        #send message to server
        seft.__socket_server.send(message.encode())
        #recv message for addr of host who has file
        str_clients = seft.__socket_server.recv(1024).decode()
        if str_clients == "NO":
            socket_local.send(f"Network don't have file {fname}".encode())
            return 
        #convert str_clients to list_clients
        list_clients = str_clients.split("\n")        
        #choose client for fetch file from it
        client_ip = seft.choose_client_for_fetch(list_clients)
        
        #send message to client and recv file
        #connect to this client
        client_fetch = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_fetch.connect((client_ip, PORT_CLIENT))
        except ConnectionRefusedError:
            socket_local.send("Time out".encode())
            exit()
        
        #recv file from this client
        #send message to client
        client_fetch.send(message.encode())
        
        #receive file from client who has file <fname>
        seft.recv_file(client_fetch, fname)
        
        #send request publish 
        result_publish = seft.publish(fname)
        if result_publish == 1:
            socket_local.send("OKE".encode())
        else:
            socket_local.send("ERROR".encode())
        
        client_fetch.close()
        
        
        
    def run(seft):
        
        thread_accept = threading.Thread(target = seft.accepting)
        thread_cmd = threading.Thread(target = seft.cmd)
        
        thread_accept.start()
        thread_cmd.start()
        
        thread_accept.join()
        thread_cmd.join()
        
        
    
    
    def get_message_publish(seft, fname:str) -> str:
        message = "method:publish\n"
        message += "fname:"
        message += fname
        
        #message:
        #method:publish\n
        #fname:<fname>
        return message

    def publish(seft, fname:str) -> bool:
        #connect to server
        seft.__socket_server = seft.connect((ip_server, PORT_SERVER))
        #method:publish\nfname:<fname>
        message = seft.get_message_publish(fname)
        #send message to process server
        seft.__socket_server.send(message.encode())
        #wait for server send response
        #TODO
        try:
            seft.__socket_server.settimeout(5)
            result = seft.__socket_server.recv(1024).decode()
            if result == "OKE":
                seft.__socket_server.close()
                return 1
                
        except socket.timeout:
            print("Publish method didn't receive response from server!")
            seft.__socket_server.close()
            return 0
        seft.__socket_server.close()
        return 0

    
if __name__ == "__main__":
    ip_server = sys.argv[1]
    if not os.path.exists('data'):
        os.mkdir('data')
    obj_client = client(ip_server)
    obj_client.run()
    