from tkinter import *
from tkinter import filedialog as fd
from data_base_server import *
import subprocess
import time
from discover import *
from ping import *

if not os.path.exists('data'):
    os.mkdir('data')

clients = read()
ip_discover: str = ""
def discover():
    global state_ping
    global ip_discover
    ip_discover = host_name.get()
    state_ping.destroy()
    discover_func(ip_discover)
    time.sleep(1)
    show()


def list_clients():
    global state_ping
    global ip_discover
    global clients
    state_ping.destroy()
    ip_discover = ""
    clients = read()
    Label(root, text = "").grid(row = 4, column=1)
    show()

def ping():
    global state_ping
    state_ping.destroy()
    ip_ping = host_name.get()
    result = ping_func(ip_ping)
    time.sleep(1)
    state_ping = Label(root, text = result)
    state_ping.grid(row = 4, column=1)

    show()

    
def show():
    global ip_discover
    list_box.delete(0, END)
    ip_clients = list(clients.keys())
    for ip_client in ip_clients:
        list_box.insert(END, ip_client[:-4])
        if ip_client[:-4] == ip_discover:
            file_names = list(clients[ip_client])
            for file_name in file_names:
                file_name = "              " + file_name
                list_box.insert(END, file_name)

root = Tk()
root.title("Server")
root.minsize(height = 500, width = 500)

list_box = Listbox(root, width=80, height=20)
list_box.grid(row = 1, columnspan = 2)

show()
state_ping = Label(root, text = "")
state_ping.grid(row = 4, column=1)

Label(root, text = "List of clients:").grid(row = 0, column=0)

host_name = StringVar()
host_name.set("0.0.0.0")
Label(root, text = "host name:").grid(row = 2, column=0)
Entry(root, width=40, textvariable = host_name).grid(row = 2, column = 1)



button = Frame(root)
Button(button, text = "Discover", command = discover).pack(side=LEFT)
Button(button, text = "Ping", command = ping).pack(side=LEFT)
Button(button, text = "List Clients", command = list_clients).pack(side=LEFT)

button.grid(row = 3, column = 1)



root.mainloop()




