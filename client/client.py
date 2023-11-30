import socket
import threading
import sys
import os 

PORT_CLIENT = 7777
PORT_LOCAL = 8888
PORT_SERVER = 9999

class client:
    
    __ip_server: str
    #socket server
    __socket_server: socket.socket #socket use to connect to server
    __socket_client: socket.socket #socket use to listen from other client
    __socket_local: socket.socket  #socket use to listen from local socket
    
    def __init__(seft, ip_addr: str):
        
        seft.__ip_server = ip_addr     
        #connect to serfor for identify server exist
        seft.__socket_server = seft.connect((seft.__ip_server, PORT_SERVER))
        seft.__socket_server.close()
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
            #if finish handle request -> close connect 
            socket_local.close()
            
    def handle_cmd(seft, socket_local: socket.socket):
        
        message = socket_local.recv(1024)
        #if disconnect -> close socket_local
        if not message:
            return
        
        message = message.decode()

        #split message to <method> and <fname>
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
        elif method == "exit":
            #exit this client process
            pid = str(os.getpid())
            socket_local.send(pid.encode())
        else:
            socket_local.send("ERROR".encode())
    
    #thread always listen connect from client 
    def accepting(seft):
        while 1:
            s, addr = seft.__socket_client.accept()
            # print(f"Connected from {add}")
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
                socket_client.close()
        
            
    
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
        #messaeg (str): method:<method>\n......
        obj_request = seft.split_message(message)
        method = obj_request[0]
        
        if method == "fetch":
            fname = obj_request[1]
            seft.send_file(socket_client, fname)
        elif method == "ping":
            socket_client.send("OKE".encode())
        else:
            socket_client.send("ERROR".encode()) 
        
        
    
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
        #open file
        file = open("data\\" + file_name, "rb")
        
        #read file
        data = file.read()
        
        #send size of file to client
        size = str(len(data))
        socket_client.send(size.encode())
        
        #wait for recv "OKE" from another client
        signal = socket_client.recv(1024).decode()
    
        if signal == "OKE":
            #send data of file to server
            size = len(data)
            count:int = 0
            #we send many times with each time we send 4096 bytes
            #we decrease size by 4096 once we send and stop when size <= 0
            while size > 0:
                if size < 4096:
                    socket_client.send(data[4096*count:])
                else:
                    socket_client.send(data[4096*count: 4096*(count + 1)])
                count += 1
                size -= 4096        
        file.close()
    
    def recv_file(seft, socket_client:socket.socket, file_name:str):
        #recv size of file
        size = int(socket_client.recv(1024).decode())
        #send response to client who send file for synchronized
        socket_client.send("OKE".encode())
        #We recv data many time with each time we recv 4096 bytes
        #we decrease size by 4096 once we recv and stop when size <= 0
        file_bytes = b''
        while size > 0:
            if size >= 4096:
                data = socket_client.recv(4096)    
            else:
                data = socket_client.recv(size)    
            file_bytes += data
            size -= len(data)
            
                
        #open file name which received from client
        file = open("data\\" + file_name, "wb")
        file.write(file_bytes)  
        file.close()
          
        print(f"Recv file {file_name} completed")
        
        socket_client.close()
    
    def message_for_fetch(seft, fname) -> bytes:
        message = ""
        message += "METHOD:fetch" 
        message += "\nfname:"
        message += fname
        
        #METHOD:fetch
        #fname:<fname>
        return message
        
    def choose_client_for_fetch(seft, list_clients:list[str]) -> str:
        #we can choose client with another way
        #TODO
        return list_clients[0]
        

    def fetch(seft, socket_local:socket.socket, fname: str):
        #connect to server
        seft.__socket_server = seft.connect((seft.__ip_server, PORT_SERVER))
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
        #message = method:fetch\nfname:<fname>
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
        seft.__socket_server = seft.connect((seft.__ip_server, PORT_SERVER))
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
    