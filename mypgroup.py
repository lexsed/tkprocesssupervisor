
"""

Implementation of a process group manager using minexpect.py

The processes are defined in a list of dictionaries.  Each dictionary contains the
configuration for a single process.  The dictionary contains the following keys:

    "name" - the name of the process
    "command" - the command to run
    "run" - True if the process should be started when the supervisor is started
    "initial_delay" - the number of seconds to wait before starting the process
    "backoff_on_restart" - the number of seconds to wait before restarting the process

    
"""
import subprocess
import threading
import time
from minexpect import minExpect
import psutil


class myprocess():

    def __init__(self, process_entry):
        self.process_entry = process_entry
        self.name = process_entry["name"]
        self.command = process_entry["command"]
        
        
        self.buffer = ""
        self.buffer_size = process_entry.get("buffer_size", 1024*8)
        
        self.manage = True
        self.run = process_entry.get("run", True)
        self.process = None
        
        self.thread = threading.Thread(target=lambda : self._manager_thread())
        
        
        self.was_running = False
        self.backoff_on_restart = process_entry.get("backoff_on_restart", 2)
        

        self._backoff(process_entry.get("initial_delay", 0))

        self.last_return_code = None
        self.pid = None

        self.thread.start()
        
        
        

        
    def start(self):
        self.run = True
        

    def _start_process(self):

        try: 
            self.process = minExpect(self.process_entry["command"])
            self.was_running = True
            return True
        except Exception as e:
            print(f"error starting process: {e}")
            self.backoff = 2
            return False


    def restart(self):
        self._stop_process()
        self.run = True
        self._backoff(self.backoff_on_restart)

    def cpuusage(self):
        try:
            if self.process:
                return psutil.Process(self.process.child.pid).cpu_percent()
        except:
            pass
        return float("nan")



    def stop(self):
        
        self.run = False
        
        
    def _stop_process(self):
        if self.process:
            self.last_return_code = self.process.close()
        self.process = None



    def running(self):
        if self.process:
            return self.process.running()
        return False
    
    def _check_buffer(self):
            try: 
                for i in range(10): # read up to 10 times to get all the data
                    if self.process.child.poll() is not None:
                        break
                    data = self.process.readAllSoFar()
                    if data: 
                        self.buffer += data
                        if len(self.buffer) > self.buffer_size:
                            chomp = len(self.buffer) - self.buffer_size
                            if '\n' in self.buffer: # chomp to the at least a newline
                                chomp = max(self.buffer.find('\n'), chomp)
                            self.buffer = self.buffer[chomp:]
                    else:
                        break # no more data, no more reads
            except Exception as e:
                #print(f"error in _check_buffer {e}")
                pass


    def _backoff(self, backoff=None):
        if backoff is  None:
            self.backoff = self.backoff_on_restart
        else:
            self.backoff = backoff
            self.last_check_backoff = time.time()
        return self.backoff
    
    def _check_backoff(self):
        if self.backoff > 0:
                    self.backoff -= abs(time.time() - self.last_check_backoff)
                    if self.backoff < 0:
                        self.backoff = 0
                    self.last_check_backoff = time.time()
        return self.backoff

    
        
    def _manager_thread(self):
            try:
                while self.manage:
                    if self.run:
                        if not self.running():
                            if self.was_running:
                                # detercted a restart
                                self.was_running = False
                                try:
                                    self.last_return_code = self.process.child.poll()
                                    self.pid = None
                                except Exception as e:
                                    pass
                                self._backoff() # backoff on restart
                            
                            if self.backoff <= 0:
                                self._start_process()
                                self._backoff()
                                #self.buffer = ""
                        else:
                            if self.pid is None:
                                self.pid = self.process.child.pid
                                
                            self._check_buffer()
                    else:
                        if self.running():
                            self._stop_process()
                    time.sleep(0.1)
                    self._check_backoff()
            except Exception as e:
                pass
            self._stop_process()
            print(f"manager thread exit {self.name}")
                
                


    def lenbuffer(self):
        return len(self.buffer)
    
    def readbuffer(self):
        data = self.buffer
        self.buffer = ""
        return data
    
    def peekbuffer(self):
        return self.buffer
        

    def destroy(self):
        self.stop()
        self.manage = False
        self.thread.join()


    def __del__(self):
        self.destroy()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.destroy()
        return False
    
    def __enter__(self):
        return self
    

        


class MyPGroup:

    def __init__(self, config, process_list):
        self.config = config
        self.process_configs = process_list
        self.processses = []
        self.by_name = {}
    

        for process_entry in self.process_configs:
            name   = process_entry["name"]
            proc = myprocess(process_entry)
            self.processses.append(proc)
            self.by_name[name] = { "process": proc, "config": process_entry }
            
            
        
        
    def get_process(self, name):
        return self.by_name[name]["process"]
    
    
    
    def iget_process(self, idx):
        return self.processses[idx]
    
    def istart(self, idx):
        self.processses[idx].start()

    def istop(self, idx):
        print(f"stopping {idx}")
        self.processses[idx].stop()

    def irestart(self, idx):
        self.processses[idx].restart()
    
    def stop_all(self):
        for i,proc in enumerate(self.processses):
            self.istop(i)


    def destroy(self):
        for proc in self.processses:
            proc.destroy()

    def start_all(self):
        for proc in self.processses:
            proc.start()

    def restart_all(self):
        for proc in self.processses:
            proc.restart()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_all()

        return False
