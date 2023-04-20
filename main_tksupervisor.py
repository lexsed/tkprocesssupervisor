"""
A simple process supervisor using tkinter.

This is a simple process supervisor that uses tkinter to display the status of
multiple processes.  The processes are defined in a json file.  The json file has two
top level keys, "config" and "processes". 

The "config" key contains a dictionary of configuration items.  (TBD)

The "processes" key contains a list of dictionaries.  Each dictionary contains the
configuration for a single process.  The dictionary contains the following keys:

    "name" - the name of the process
    "command" - the command to run
    "run" - True if the process should be started when the supervisor is started
    "initial_delay" - the number of seconds to wait before starting the process
    "backoff_on_restart" - the number of seconds to wait before restarting the process



"""


import time
from myicon import get_my_icon
from mypgroup import myprocess, MyPGroup
import argparse
import json


import tkinter as tk
#import tkinter.tix as tix
import tkinter.ttk as ttk

import json
import tkinter.font



parser = argparse.ArgumentParser(description='Display data from multiple sources according to time.')
parser.add_argument('config', default=["proc_supervisor.json"], nargs='*', type=str, help='source configuration file')

# initialize parser
args = parser.parse_args()
print(args.config)


with open(args.config[0]) as f:
    config_data = json.load(f)

config = config_data.get("config", {})
processes = config_data.get("processes", [])
        


class MySupervisorWindow(tk.Tk):
    def __init__(self, config, processes):
        super().__init__()
        self.title("Process Supervisor")
        self.geometry("600x480")
        img = tk.PhotoImage(data=get_my_icon())
        self.iconphoto(True,img)

        self.config = config
        self.processes = processes
        self.pgroup = MyPGroup(config, processes)
        
        self.create_widgets()
        self.configure_widgets()
        self.after(500, self.update)

    def pg_status(self):
        for i,proc in enumerate(self.pgroup.processses):
            state = ''
            if proc.running():
                pid = proc.pid
                pid_str = f'{pid:8.0f}' if pid else ' '*8
                if proc.run:
                    state = f'🏃 running {pid_str}'
                else:
                    state = f'⬇ stopping {pid_str}'
            else:
                if proc.run == False:
                    state = '🛑 stopped'
                else:
                    if proc.backoff>0:
                        state = f'⌛ backoff {proc.backoff:0.1f}s '
                    else:
                        state = '⚠️ not running '


            
            #yield f'{i:02d}: {state:25s} | {proc.name:30s} | {proc.command:80s}'
            yield (f'{i:02d}', state, proc.name, proc.command)
        
        
    def create_widgets(self):

        # frame with main controls
        self.control_frame = ttk.LabelFrame(self, text="Controls")
        self.control_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
      #  sep = ttk.Separator(self.control_frame, orient=tk.HORIZONTAL)
      #  sep.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=10, pady=5)


        self.button_start = ttk.Button(self.control_frame, text="Start", command=lambda: self.do_selected(self.start))
        self.button_start.pack(side=tk.LEFT, fill=tk.X, expand=False)
        
        self.button_start = ttk.Button(self.control_frame, text="Restart", command=lambda: self.do_selected(self.restart))
        self.button_start.pack(side=tk.LEFT, fill=tk.X, expand=False)

        self.button_stop = ttk.Button(self.control_frame, text="Stop", command= lambda: self.do_selected(self.stop))
        self.button_stop.pack(side=tk.LEFT, fill=tk.X, expand=False)

        sep = ttk.Separator(self.control_frame, orient=tk.HORIZONTAL)
        sep.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=30, pady=5)


        self.button_start = ttk.Button(self.control_frame, text="Start all", command=self.start)
        self.button_start.pack(side=tk.LEFT, fill=tk.X, expand=False)
        
        self.button_start = ttk.Button(self.control_frame, text="Restart all", command=self.start)
        self.button_start.pack(side=tk.LEFT, fill=tk.X, expand=False)

        self.button_stop = ttk.Button(self.control_frame, text="Stop all", command=self.stop)
        self.button_stop.pack(side=tk.LEFT, fill=tk.X, expand=False)

        ###
        # frame with process list and text widget for output

        self.left_frame = tk.PanedWindow(self,orient="vertical")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.process_list = ttk.Treeview(self.left_frame, columns=('number','state', 'name', 'command'), show='headings')
        self.process_list.heading('#1', text='#')
        self.process_list.heading('#2', text='State')
        self.process_list.heading('#3', text='Name')
        self.process_list.heading('#4', text='Command')

        self.process_list.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.process_list.column("# 1",anchor=tk.CENTER, stretch=tk.NO, width=20)
        self.process_list.column("# 2",anchor=tk.W, stretch=tk.YES, width=80)
        self.process_list.tag_configure('running', background='lightgreen')
        self.process_list.tag_configure('wait', background='lightgray')
        self.process_list.tag_configure('warning', background='yellow')
        self.process_list.tag_configure('error', background='pink')
        self.process_list.tag_configure('normal', background='white')

        # bind double click to listbox
        #self.process_list.bind('<Double-1>', self.on_double_click)
        self.process_list.bind('<Double-1>', self.on_double_click)
        self.process_list.bind('<Return>', self.on_double_click)
        self.process_list.bind('<<TreeviewSelect>>', self.on_listbox_select)

        
        self.notebook = ttk.Notebook(self.left_frame)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # a terminal-like text widget
        self.text = tk.Text(self.notebook, width=60, height=10)
        self.text.pack(side=tk.TOP, fill=tk.BOTH)
        self.text.configure(bg='lightgray')  # disable text widget
        
        self.item_font =tkinter.font.Font( family = "Courier New", 
                                 size = 10, 
                                 weight = "normal")
        
        # add a vertical scrollbar to the text widget
        self.scroll_yscroll = ttk.Scrollbar(self.text, orient=tk.VERTICAL, command=self.text.yview)
        self.scroll_yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text['yscrollcommand'] = self.scroll_yscroll.set
        
        #self.process_list.configure(font=self.item_font)
        

        self.notebook.add(self.text, text='Output')

        self.config = tk.Text(self.notebook, width=60, height=10)
        self.config.pack(side=tk.TOP, fill=tk.BOTH)
        self.config.configure(bg='lightgray')  # disable text widget
        self.notebook.add(self.config, text='Config')

        #self.process_list.bind("<<ListboxSelect>>", self.on_listbox_select)

    

        
        # add a vertical scrollbar to the text widget
        self.left_frame.add(self.process_list)
        self.left_frame.add(self.notebook)





    def on_listbox_select(self, event):
        try:
            selected = [int(self.process_list.focus())]
        except:
            selected = []
            
        if len(selected) == 1:
            index = selected[0]
            self.config.delete('1.0', tk.END)
            formatted =json.dumps(self.pgroup.iget_process(index).process_entry, indent=4)
            self.config.insert(tk.END, formatted)
            self.config.configure(bg='lightgray')
            


    def on_double_click(self, event):
        """Double click on a process to start it"""
        self.do_selected(self.start)
    
    def do_selected(self, func):
        """Do something to the selected processes"""
        for i in self._get_selected():
            func(i)

        

    def start(self, index=None):
        if index is None:
            self.pgroup.start_all()
        else:
            self.pgroup.istart(index)
        

    def stop(self, index=None):
        if index is None:
            self.pgroup.stop_all()
        else:
            self.pgroup.istop(index)

    def restart(self, index=None):
        if index is None:
            self.pgroup.restart_all()
        else:
            self.pgroup.irestart(index)



    def configure_widgets(self):
        
        #self.process_list.delete(0, tk.END) # clear the list
        # fill out the list

        for i, proc_text in enumerate(self.pg_status()):
            #self.process_list.insert(tk.END, proc_text)
            self.process_list.insert('', 'end', i, values=proc_text)


        

            
    def _get_selected(self):
        selected = self.process_list.focus()
        try:
            i = int(selected)
            return [i]
        except:
            return []
    
    def update(self):
        

        # save the selected items
        #selected = self.process_list.focus()

        for i, status in list(enumerate(self.pg_status())):

            #self.process_list.delete(i)
            #self.process_list.insert(i, status)
            #item = self.process_list.item(i)
            self.process_list.item(i, values=status)

            
            if 'running' in status[1]:
                #self.process_list.itemconfig(i, dict(bg='lightgreen'))
                self.process_list.item(i, tags=('running',))
                

            elif 'backoff' in status:
                #self.process_list.itemconfig(i, dict(bg='gray'))
                self.process_list.item(i, tags=('wait',))
            elif 'not running' or 'stopping' in status:
                self.process_list.item(i, tags=('warning',))

            elif 'stopped' in status:
                self.process_list.item(i, tags=('normal',))
                #self.process_list.itemconfig(i, dict(bg='yellow'))


        #if selected:
            # reselect the selected items
        #    self.process_list.selection_set(selected)

            
            #self.process_list.itemconfigure(i, element=status)

        selected = self._get_selected()
        if selected and len(selected) == 1 and self.notebook.index(self.notebook.select()) == 0:
            buffer = self.pgroup.processses[selected[0]].buffer
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, buffer)
            self.text.see(tk.END)




        self.after(500, self.update)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.pgroup.stop_all()
        self.pgroup.destroy()
        return False



def main():

    with MySupervisorWindow(config, processes) as root:
    
        root.mainloop()
        
        

	
	
	
if __name__ == "__main__":
    main()
    print('done')
