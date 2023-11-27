import socket
import threading

PORT_CLIENT = 7777
PORT_LOCAL = 8888
PORT_SERVER = 9999

class server:
    #socket use to listen client
    __socket_listen: socket.socket
    #dict contain socket of client and its file name 
    #when client publish file name to server
    __socket_client_dict: dict[socket.socket, set[str]]
    
    __socket_local: socket.socket
    
    def __init__(seft):
    
        seft.__socket_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        seft.__socket_listen.bind(("", PORT_SERVER))
        seft.__socket_listen.listen(100)
        
        seft.__socket_local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        seft.__socket_local.bind(("", PORT_LOCAL))
        seft.__socket_local.listen(1)
        
        seft.__socket_client_dict = {}
        seft.__lock = threading.Lock()
        
        
    #thread always listen connect from client 
    def accepting(seft):
        while 1:
            s, add = seft.__socket_listen.accept()
            print(f"Connected from {add}")
            seft.__lock.acquire()
            seft.__socket_client_dict[s] = set()
            seft.__lock.release()
            thread_client = threading.Thread(target = seft.handle_client, args = (s,))
            thread_client.start()
    
    def cmd(seft):
        while 1:
            s, _ = seft.__socket_local.accept()
            thread_cmd = threading.Thread(target = seft.handle_cmd, args = (s,))
            thread_cmd.start()
            thread_cmd.join()
            
    def handle_cmd(seft, socket_local:socket.socket):
        message = socket_local.recv(1024).decode()
        obj_request = seft.split_message(message)
        method = obj_request[0]
        
        if method == "discover":
            #socket_client is socket local which is created from cmd
            #when we call discover from cmd
            host_name = obj_request[1]
            fnames = seft.discover(host_name)
            #send size of fnames
            socket_local.send(len(fnames).encode())
            #recv signal from local socket 
            signal = socket_local.recv(1024).decode()
            #send fnames to local socket
            if(signal == "OKE"):
                socket_local.send(fnames)
            else:
                seft.handle_request_error()
                socket_local.send("ERROR".encode()) 
        elif method == "list_clients":
            clients = seft.list_clients()
            socket_local.send(clients.encode())
                
    #create new thread when server accept new connect from new client
    def handle_client(seft, client:socket.socket):
        while 1:
            try:
                request = client.recv(1024)
                seft.handle_request(client, request)
            except ConnectionResetError:
                seft.remove_client(client)
                print(f"Disconnect from {client.getpeername()}")
                client.close()
                exit()
        
    
    def remove_client(seft, client:socket.socket):
        seft.__lock.acquire()
        seft.__socket_client_dict.pop(client)
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
            fname = obj_request[1]
            seft.publish(socket_client, fname)
            socket_client.send("OKE".encode())
        elif method == "fetch":
            fname = obj_request[1]
            seft.fetch(socket_client, fname)
        else:
            seft.handle_request_error()
            socket_client.send("ERROR".encode()) 
        
    def get_socket_client_set(seft) -> set[socket.socket]:
        return set(seft.__socket_client_dict.keys())
        
    #return set of file_name whose client have
    def get_socket_client_file(seft, s: socket.socket) -> set[str]:
        return seft.__socket_client_dict[s]
    
    def get_host_name(seft, s:socket.socket) -> str:
        ip = s.getpeername()[0]
        port = s.getpeername()[1]
        return ip + ":" + str(port)
    def list_clients(seft) -> str:
        socket_client_set = seft.get_socket_client_set()
        clients = ""
        for client in socket_client_set:
            ip = client.getpeername()[0]
            port = str(client.getpeername()[1])
            clients += (ip + port + "\n")
        return clients
    
    #return string contain file name of host_name
    def discover(seft, host_name: str):
        result_str = ""
        socket_client_set = seft.get_socket_client_set()
        socket_client = socket.socket
        for socket_client in socket_client_set:
            if host_name == seft.get_host_name(socket_client):
                result_str = "Host" + host_name + "\n"
                fname_set = seft.get_socket_client_file(socket_client)
                for fname in fname_set:
                    result_str += fname
                    result_str += "\n"
                return result_str
        return "Doesn't exist" + host_name
        
    #add fname to set of file_name of client
    def publish(seft, socket_client: socket.socket, fname: str):
        #get set of file_names of client
        file_names = seft.__socket_client_dict[socket_client]
        #add file_name into this set
        file_names.add(fname)
        
    #return set of addr (ip_addr, port_number) of sockets which have file fname
    def find_fname_in_socket_client_dict(seft, fname: str) -> set[str]:
        #set of socket client 
        socket_client_set = seft.get_socket_client_set()
        #set of addr of client which has fname
        set_addr_client_have_fname: set[str] = {}
        for socket_client in socket_client_set:
            socket_client_file = seft.get_socket_client_file(socket_client)
            if find_element_of_set(fname, socket_client_file):
                # addr inclue ip and port_number
                # it shoule be change to only ip 
                addr = socket_client.getpeername()[0] + ":" + str(socket_client.getpeername()[1])
                
                set_addr_client_have_fname.add(addr)
                
        return set_addr_client_have_fname
        
    #if not exist -> send "NO"
    #else -> send string
    def fetch(seft, socket_client: socket.socket, fname: str):
        set_addr_client_have_fname = seft.find_fname_in_socket_client_dict(fname)
        
        # if not exist any client has this file
        if len(set_addr_client_have_fname) == 0:
            socket_client.send("NO".encode())
            return
        
        #if exist client has this file
        result = ""
        
        for addr_client in set_addr_client_have_fname:
            result += addr_client 
            result += "\n"
        
        #result is: <client>\n<client>\n...<client>\n
        socket_client.send(result.encode())
    
    def get_socket_client_from_host_name(seft, addr: str) -> socket.socket:
        ip_port = addr.split(":")
        ip = ip_port[0]
        port = ip_port[1]
        
        for s in seft.__socket_client_dict:
            if s.getpeername() == (ip, port):
                return s
        return None
                
    
    def run(seft):
        thread_accept = threading.Thread(target = seft.accepting)
        thread_cmd = threading.Thread(target = seft.cmd)
        
        thread_accept.start()
        thread_cmd.start()
        
        thread_accept.join()
        thread_cmd.join()
        
    
    
    
def find_element_of_set(element, set: set) -> bool:
    for tem in set:
        if tem == element:
            return True
    return False
        
    
    
if __name__ == "__main__":
    
    obj_server = server()
    
    obj_server.run()
    
    
    