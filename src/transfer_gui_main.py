from tkinter import *
import tkinter as tk
import os
import time

class ParentWindow(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)

        # define max and min size of frame
        self.master = master
        self.master.minsize(500, 230)
        self.master.maxsize(500, 230)
        # give the master frame a name
        self.master.title("P2P File Transfer")
        self.database = []
        self.files = 0
        
        
    def start(self):
        greeting = tk.Label(text="Please provide at least one file to server.\n\r")
        greeting.pack()
        self.work()
        #file_xfer_gui.load_gui(self)

    def work(self):

        self.add_file()
        
    
    def loop(self):
        if self.files < 5:
            want_more = tk.Label("Do you want to add another file?")
            want_more.pack()
            yes = tk.Button(text = "Yes", width = 3, height = 1, bg = "white",fg = "black", command = work)
            add_button.pack()
            add_button = tk.Button(text = "No", width = 3, height = 1, bg = "white",fg = "black", command = check)
            add_button.pack()


    def send(self):
        return 
    def get_info_about_file(self, file_path):
        path = os.path.abspath(os.getcwd())
        name, ext  = os.path.splitext(file_path[2:])
        size = os.path.getsize(file_path)
        modified = os.path.getmtime(file_path)
        year,month,day,hour,minute,second=time.localtime(modified)[:-3]
        date = "%02d/%02d/%d"%(day,month,year)
        
        self.database.append([name,path,ext,size,date])
        self.loop()

        
 


    # returns file name 
    def add_file(self):
        custom_source = StringVar()
        custom_source.set('Provide a path to the file please.')
        text_source = tk.Entry(self.master, width=60, textvariable=custom_source)
        text_source.pack()

        def check():
            file_path = text_source.get()
            if os.path.isfile(file_path):
                add_button['state'] = 'disabled'
                self.get_info_about_file(file_path)
                self.files += 1
                return 
            else:
                text_source.delete(0, tk.END)
                text_source.insert(0,"Path is invalid. Provide another.")
            

        add_button = tk.Button(text = "Add", width = 3, height = 1, bg = "white",fg = "black", command = check)
        add_button.pack()

        





if __name__ == "__main__":
    root = tk.Tk()
    App = ParentWindow(root)
    App.start()
    root.mainloop()