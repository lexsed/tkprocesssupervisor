
import time
from mypgroup import myprocess, MyPGroup
import argparse

import tkinter as tk
import tkinter.tix as tix
import tkinter.ttk as ttk

import json




parser = argparse.ArgumentParser(description='Display data from multiple sources according to time.')
parser.add_argument('config', default=["proc_supervisor.json"], nargs='*', type=str, help='source configuration file')

# initialize parser
args = parser.parse_args()
print(args.config)


with open(args.config[0]) as f:
    config_data = json.load(f)

config = config_data.get("config", {})
processes = config_data.get("processes", [])
        


class MySupervisorWindow(tix.Tk):
    def __init__(self, config, processes):
        super().__init__()
        self.title("Process Supervisor")
        self.geometry("600x480")
        self.config = config
        self.processes = processes
        self.pgroup = MyPGroup(config, processes)
        
        self.create_widgets()
        self.configure_widgets()
        self.after(500, self.update)

    def pg_status(self):
        for proc in self.pgroup.processses:
            state = ''
            if proc.running():
                state = 'running'
            else:
                if proc.run == False:
                    state = 'stopped'
                else:
                    if proc.backoff>0:
                        state = 'backoff {proc.backoff:0.1f}s}'
                    else:
                        state = 'not running'

            yield f'{proc.name} \t {state}'
        
        
    def create_widgets(self):
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.process_list = tk.Listbox(self.left_frame, width=60)
        self.process_list.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # bind double click to listbox
        self.process_list.bind('<Double-1>', self.on_double_click)
        

        # a terminal-like text widget
        self.text = tk.Text(self.left_frame, width=60, height=10)
        self.text.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        self.text.configure(bg='lightgray')  # disable text widget
        # add a vertical scrollbar to the text widget
        



        

        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=True)




        self.button_start = tk.Button(self.right_frame, text="Start", command=lambda: self.do_selected(self.start))
        self.button_start.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        self.button_start = tk.Button(self.right_frame, text="Restart", command=lambda: self.do_selected(self.restart))
        self.button_start.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.button_stop = tk.Button(self.right_frame, text="Stop", command= lambda: self.do_selected(self.stop))
        self.button_stop.pack(side=tk.TOP, fill=tk.X, expand=True)

        sep = ttk.Separator(self.right_frame, orient=tk.HORIZONTAL)
        sep.pack(side=tk.TOP, fill=tk.X, expand=True,)


        self.button_start = tk.Button(self.right_frame, text="Start all", command=self.start)
        self.button_start.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        self.button_start = tk.Button(self.right_frame, text="Restart all", command=self.start)
        self.button_start.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.button_stop = tk.Button(self.right_frame, text="Stop all", command=self.stop)
        self.button_stop.pack(side=tk.TOP, fill=tk.X, expand=True)

        sep = ttk.Separator(self.right_frame, orient=tk.HORIZONTAL)
        sep.pack(side=tk.TOP, fill=tk.BOTH, expand=True, )


    def on_double_click(self, event):
        self.do_selected(self.start)
    
    def do_selected(self, func):
        selected = self.process_list.curselection()
        for i in selected:
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
        
        self.process_list.delete(0, tk.END) # clear the list
        # fill out the list

        for proc_text in self.pg_status():
            self.process_list.insert(tk.END, proc_text)

        

            
    def update(self):
        sel = None

        selected = self.process_list.curselection()
        for i, status in list(enumerate(self.pg_status())):
            self.process_list.delete(i)
            self.process_list.insert(i, status)
            if 'running' in status:
                self.process_list.itemconfig(i, dict(bg='lightgreen'))
            elif 'backoff' in status:
                self.process_list.itemconfig(i, dict(bg='gray'))
            elif 'stopped' in status:
                self.process_list.itemconfig(i, dict(bg='yellow'))

        if selected:
            self.process_list.selection_set(selected)

            
            #self.process_list.itemconfigure(i, element=status)

        if selected:
            buffer = self.pgroup.processses[selected[0]].buffer
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, buffer)
            self.text.see(tk.END)




        self.after(500, self.update)


def main():

    root = MySupervisorWindow(config, processes)
    root.mainloop()
        
        

	
	
	
if __name__ == "__main__":
    main()
