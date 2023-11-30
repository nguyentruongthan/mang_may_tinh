import socket
import threading
import os
import shutil
import time

PORT_CLIENT = 7777
PORT_LOCAL = 8888
PORT_SERVER = 9999

class server:
    #socket use to listen client
    __socket_listen: socket.socket
    #dict struct with key is ip_addr of client
    #and value is set of file name whom client has
    __ip_client_dict: dict[str, set[str]]
    
    __socket_local: socket.socket
    
    def __init__(seft):
        
        seft.__socket_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        seft.__socket_listen.bind(("", PORT_SERVER))
        seft.__socket_listen.listen(100)
        
        seft.__socket_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        seft.__socket_local.bind(("", PORT_LOCAL))
        seft.__socket_local.listen(1)
        
        seft.__ip_client_dict = {}
        seft.__lock = threading.Lock()
    
    #check client is live every 30s
    def check_clients_live(seft, is_one_time):
        while 1:
            ip_clients = list(seft.__ip_client_dict.keys())
            for ip_client in ip_clients:
                #we check three times
                for i in range(3):
                    socket_check_live = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socket_check_live.settimeout(3)
                    try: 
                        socket_check_live.connect((ip_client, PORT_CLIENT))
                        socket_check_live.gettimeout()
                        socket_check_live.close()
                        break
                    except socket.timeout:
                        os.remove("data\\" + ip_client + ".txt")
                        seft.remove_client(ip_client)
            if is_one_time == 1:
                return
            time.sleep(30)
            
    #thread always listen connect from client 
    def accepting(seft):
        while 1:
            s, _ = seft.__socket_listen.accept()
            ip_addr = s.getpeername()[0]
            # print(f"Connected from {ip_addr}")
            
            seft.__lock.acquire()
            #init new element for dict
            if seft.__ip_client_dict.get(ip_addr) is None:
                seft.__ip_client_dict[ip_addr] = set()
            #create file for client
            path = "data\\" + s.getpeername()[0] + ".txt"
            if not os.path.exists(path):
                file = open(path , 'x')
                file.close()
            seft.__lock.release()
            thread_client = threading.Thread(target = seft.handle_client, args = (s,))
            thread_client.start()
    
    def cmd(seft):  
        while 1:
            socket_local, _ = seft.__socket_local.accept()
            seft.handle_cmd(socket_local)
            
    def handle_cmd(seft, socket_local:socket.socket):
        message = socket_local.recv(1024).decode()
        obj_request = seft.split_message(message)
        method = obj_request[0]
        
        if method == "discover":
            host_name = obj_request[1]
            fnames = seft.discover(host_name)
            #send size of fnames
            length_fnames = len(fnames)
            socket_local.send(str(length_fnames).encode())
            if fnames != "":
                #recv signal from local socket 
                signal = socket_local.recv(1024).decode()
                #send fnames to local socket
                if(signal == "OKE"):
                    socket_local.send(fnames.encode())
                else:
                    seft.handle_request_error()
                    socket_local.send("ERROR".encode()) 
        elif method == "list_clients":
            clients = seft.list_clients()
            socket_local.send(clients.encode())
        elif method == "exit":
            pid = str(os.getpid())
            socket_local.send(pid.encode())
        else: 
            socket_local.send("ERROR".encode()) 
                
    #create new thread when server accept new connect from new client
    def handle_client(seft, client:socket.socket):
        request = client.recv(1024)
        if not request:
            client.close()
        else:
            
            # print(f"From {client.getpeername()[0]}:")
            # print(request.decode())
            # print("-----------------------")
            seft.handle_request(client, request.decode())
            
        
    
    def remove_client(seft, ip_client:str):
        print(f"Remove client {ip_client}")
        seft.__lock.acquire()
        if seft.__ip_client_dict.get(ip_client):
            seft.__ip_client_dict.pop(ip_client)
        seft.__lock.release()
                           
    
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
        elif method == "discover":
            host_name = seft.split_host_name(lines[1])
            result_list.append(host_name)
        return result_list

    def handle_request_error(seft):
        print("Request Error")
    
    def handle_request(seft, socket_client:socket.socket, message:str):
        #messaeg (str): method:<method>\n 
        #               ...............
        obj_request = seft.split_message(message)
        method = obj_request[0]
        
        if method == "publish":
            ip_client = socket_client.getpeername()[0]
            fname = obj_request[1]
            seft.publish(ip_client, fname)
            socket_client.send("OKE".encode())
        elif method == "fetch":
            fname = obj_request[1]
            seft.fetch(socket_client, fname)
        else:
            seft.handle_request_error()
            socket_client.send("ERROR".encode()) 
        
        socket_client.close()
        

    def list_clients(seft) -> str:
        ip_client_list = list(seft.__ip_client_dict.keys())
        ip_clients = ""
        for ip_client in ip_client_list:
            ip_clients += (ip_client + "\n")
        return ip_clients
    
    #return string contain file name of host_name
    def discover(seft, host_name: str) -> str:
        seft.check_clients_live(1)
        result_str = ""
        #get list of ip_addr of who connected to server
        fname_set = seft.__ip_client_dict.get(host_name)
        if fname_set != None:
            for fname in fname_set:
                result_str += fname
                result_str += "\n"
            if result_str == "":
                result_str = "Empty\n"
            return result_str
        return ""
        
    #add fname to set of file_name of client
    def publish(seft, ip_client: str, fname: str):
        #add file_name into this set
        seft.__ip_client_dict[ip_client].add(fname)
                
    #return set of addr (ip_addr, port_number) of sockets which have file fname
    def find_fname_in_socket_client_dict(seft, fname: str) -> list[str]:
        #set of socket client 
        ip_client_list = list(seft.__ip_client_dict.keys())
        #set of addr of client which has fname
        list_addr_client_have_fname = []
        for ip_client in ip_client_list:
            client_files = seft.__ip_client_dict[ip_client]
            if find_element_of_set(fname, client_files):
                # it shoule be change to only ip 
                list_addr_client_have_fname.append(ip_client)
                
        return list_addr_client_have_fname
    

            
    #if not exist any client has file <fname> -> send "NO"
    #else -> send string of client who has file <fname>
    def fetch(seft, socket_client: socket.socket, fname: str):
        seft.check_clients_live(is_one_time = 1)
        
        list_addr_client_have_fname = seft.find_fname_in_socket_client_dict(fname)
        
        # if not exist any client has this file
        if len(list_addr_client_have_fname) == 0:
            socket_client.send("NO".encode())
            return
        
        #if exist client has this file
        result = ""
        
        for addr_client in list_addr_client_have_fname:
            result += addr_client 
            result += "\n"
        
        #result is: <client>\n<client>\n...<client>\n
        socket_client.send(result.encode())           
    
    def run(seft):
        thread_accept = threading.Thread(target = seft.accepting)
        thread_cmd = threading.Thread(target = seft.cmd)
        thread_check_live = threading.Thread(target = seft.check_clients_live, args = (0, ))
        
        thread_accept.start()
        thread_cmd.start()
        thread_check_live.start()
        
        thread_accept.join()
        thread_cmd.join()
        thread_check_live.join()
    
    
    
def find_element_of_set(element, set: set) -> bool:
    for tem in set:
        if tem == element:
            return True
    return False
        
    
    
if __name__ == "__main__":
    if not os.path.exists('data'):
        os.mkdir('data')
    else:
        shutil.rmtree('data', ignore_errors=True)
        os.mkdir('data')

    obj_server = server()
    obj_server.run()
    
    
    