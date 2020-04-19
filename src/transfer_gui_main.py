from tkinter import *
import tkinter as tk
import os 
import time
from client import retrieve_gui_data, search_gui_filename,get_qui_requested_file

class ParentWindow(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        
        self.master = master
        self.master.minsize(500, 230)
        self.master.title("P2P File Transfer")
        self.database = []
        self.server_files = None
        self.files = 0
        
    
    def start(self):
        greeting = tk.Label(text="Please provide at least one file to server.\n\r")
        greeting.pack()
        self.add_file()


    def add_file(self):
        custom_source = StringVar()
        custom_source.set('Provide a path to the file please.')
        text_source = tk.Entry(self.master, width=60, textvariable=custom_source)
        text_source.pack()

        def check():
            file_path = text_source.get()
            if os.path.isfile(file_path):
                add_button['state'] = 'disabled'
                self.files += 1
                self.get_info_about_file(file_path)
                return 
            else:
                text_source.delete(0, tk.END)
                text_source.insert(0,"Path is invalid. Provide another.")
            

        add_button = tk.Button(text = "Add", width = 3, height = 1, bg = "white",fg = "black", command = check)
        add_button.pack()


    def get_info_about_file(self, file_path):
        path = os.path.abspath(os.getcwd())
        name, ext  = os.path.splitext(file_path[2:])
        size = os.path.getsize(file_path)
        modified = os.path.getmtime(file_path)
        year,month,day,hour,minute,second=time.localtime(modified)[:-3]
        date = "%02d/%02d/%d"%(day,month,year)
        
        self.database.append([name,path,ext,size,date])
        self.loop()

        
    def loop(self):
        if self.files < 5:
            want_more = tk.Label(text = "Do you want to add another file?")
            want_more.pack()

            def yes_func():
                yes['state'] = 'disabled'
                no['state'] = 'disabled'
                self.add_file()
            
            def no_func():
                yes['state'] = 'disabled'
                no['state'] = 'disabled'
                self.send()

            
            yes = tk.Button(text = "Yes", width = 3, height = 1, bg = "white",fg = "black", command = yes_func)
            yes.pack()
            no = tk.Button(text = "No", width = 3, height = 1, bg = "white",fg = "black", command = no_func)
            no.pack()

        else:
            self.send()

    
    def send(self):
        retrieve_gui_data(self.database)
        self.search()
    
    
    def pass_search_output(self, files):
        self.server_files = files
    
    
    def search(self):
        custom_source = StringVar()
        custom_source.set('Which file do you want to download? Provide just a name.')
        text_source = tk.Entry(self.master, width=60, textvariable=custom_source)
        text_source.pack()

        def check():
            selected_file = text_source.get()
            search_gui_filename(selected_file)

            while self.server_files == None:
                time.sleep(5)
            
            if len(self.server_files) == 0:
                self.server_files = None
                text_source.delete(0, tk.END)
                text_source.insert(0,"This file does not exist. Provide another.")
            else:
                search_button['state'] = 'disabled'
                self.download_file()
                return            

        search_button = tk.Button(text = "Search", width = 5, height = 1, bg = "white",fg = "black", command = check)
        search_button.pack()


    def download_file(self):
        select_file = tk.Label(text = "Please, select the file you want to download.")
        select_file.pack()

        scrollbar = tk.Scrollbar(self.master)
        scrollbar.pack( side = RIGHT, fill = Y )

        mylist = Listbox(self.master, yscrollcommand = scrollbar.set )
        for i in range(len(self.server_files)):
            mylist.insert(END, self.server_files[i])

    
        scrollbar.config( command = mylist.yview )
        mylist.pack( fill = BOTH )

        def download():
            download_button['state'] = 'disabled'
            selected = list(mylist.get(mylist.curselection()))
            print(selected)
            get_qui_requested_file(selected)
            self.master.quit()
        download_button = tk.Button(text = "Download", width = 5, height = 1, bg = "white",fg = "black", command = download )
        download_button.pack()



if __name__ == "__main__":
    root = tk.Tk()
    App = ParentWindow(root)
    App.start()
    root.mainloop()