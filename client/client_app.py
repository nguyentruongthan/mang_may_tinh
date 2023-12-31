from tkinter import *
from tkinter import filedialog as fd
import os
import time
from publish import *
from fetch import *

path = "data"

def show():
    list_box.delete(0,END)
    file_names = os.listdir(path)
    for file_name in file_names:
        list_box.insert(END, file_name)
        

def mfileopen():
    file_path = fd.askopenfilename()
    lname.set(file_path)
    
def publish():
    global state
    state.destroy()
    
    local_name = lname.get()
    file_name = fname.get()
    
    result = publish_func(local_name, file_name)
    state = Label(root, text = result)
    state.grid(row = 5, column=1)
    
    time.sleep(0.5)
    
    show()

def fetch():
    global state
    state.destroy()
    
    file_names = fname.get().split(" ")
    result = fetch_func(file_names)
    
    state = Label(root, text = result)
    state.grid(row = 5, column=1)
    
    time.sleep(0.5)
    show()

root = Tk()
root.title("Client")
root.minsize(height = 500, width = 500)
list_box = Listbox(root, width=80, height=20)
list_box.grid(row = 1, columnspan = 2)

show()

button_brower_lname = Frame(root)

lname = StringVar()

Button(button_brower_lname, text = "brower", command = mfileopen).pack(side = LEFT)

button_brower_lname.grid(row = 2, column = 2)
Label(root, text = "lname:").grid(row = 2, column=0)

Entry(root, width=40, textvariable = lname).grid(row = 2, column = 1)

state = Label(root, text = "")
state.grid(row = 5, column=1)

fname = StringVar()
Label(root, text = "fname:").grid(row = 3, column=0)
Entry(root, width=40, textvariable = fname).grid(row = 3, column = 1)

button = Frame(root)
Button(button, text = "publish", command = publish).pack(side=LEFT)
Button(button, text = "fetch", command = fetch).pack(side=LEFT)
button.grid(row = 4, column = 1)

root.mainloop()




