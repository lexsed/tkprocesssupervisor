"""
Minimalistic expect class for subprocess.Popen
works on Linux, and Windows

Opens a subprocess.Popen object, and provides a minimalistic expect function.

Inline implementation of the pipe_no_wait function, which is used to make the pipe non-blocking,
on both Linux and Windows.


"""

#%%
import re
import subprocess
import time
import os

def isWindows():
    """ Returns True if the current platform is Windows. """
    
    return os.name == 'nt'

if not isWindows():
    """ If not Windows, use the fctl module. """
    import fcntl
    
    def pipe_no_wait(fd):
        flag = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)
        flag = fcntl.fcntl(fd, fcntl.F_GETFL)
        return True
else:
    """ If Windows, use the ctypes module. """
    import msvcrt
    

    from ctypes import windll, byref, wintypes, GetLastError, WinError
    from ctypes.wintypes import HANDLE, DWORD,  BOOL, LPDWORD


    PIPE_NOWAIT = wintypes.DWORD(0x00000001)

    ERROR_NO_DATA = 232

    def pipe_no_wait(pipefd):

        SetNamedPipeHandleState = windll.kernel32.SetNamedPipeHandleState
        SetNamedPipeHandleState.argtypes = [HANDLE, LPDWORD, LPDWORD, LPDWORD]
        SetNamedPipeHandleState.restype = BOOL

        h = msvcrt.get_osfhandle(pipefd)

        res = windll.kernel32.SetNamedPipeHandleState(h, LPDWORD(PIPE_NOWAIT), None, None)
        
        if res == 0:
            print(WinError())
            return False
        return True
    

    import os
                

    def stop_pid(pid, force=False):
        if pid is not None and pid:
            # ensure that the pid is valid
            #return os.system(f"taskkill /PID {pid} /T{ ' /F' if force else '' }")
            # run the command using subprocess
            return subprocess.call(f"taskkill /PID {pid} /T{ ' /F' if force else '' }", shell=True)
        
        return 0



class minExpect:
    """Minimalistic expect class for subprocess.Popen
    works on Linux, and Windows

    :param command: the command to run
    :type command: str
    """

    def __init__(self, command, shell=True):
        
        # create the process with the command
        self.child = subprocess.Popen(
            command, bufsize=8192, 
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, # merge stderr into stdout
            shell=shell,
        )
        
        
        # fix for blocking reads on Linux
        for fd in [
                        self.child.stdout.fileno(),
                        #self.child.stderr.fileno(),
                        self.child.stdin.fileno(),
                        ]:
            pipe_no_wait(fd)


    #%%
    def running(self):
        """check that the process is still running

        :return: running
        :rtype: bool
        """
        return self.child.poll() is None

    def readAllSoFar(self, retVal=None):
        """read all the output so far

        :param retVal: the return value, append to it
        :type retVal: str
        :return: output
        :rtype: str
        """
        # start with empty string if none given
        if retVal is None:
            retVal = ""

        # read the output
        #buf = self.child.stdout.read1(1024)
        
        try:
            buf = self.child.stdout.read1(1024)
            
            if buf:
                # append the output to the return value
                retVal += buf.decode("utf-8", errors="replace")
        except Exception as e:
            # normal for the pipe to return an error when there is no data
            pass


        return retVal

    def expectto(self, pattern=None, timeout=None):
        """expect to a pattern on the stdout

        :param pattern: the pattern to expect (regex)
        :type pattern: str
        :param timeout: the timeout
        :type timeout: int
        :return: the pattern
        :rtype: str
        """

        if timeout is None:
            timeout = 10

        start = time.time()
        return_str = ""
        while time.time() - start < timeout:
            return_str = self.readAllSoFar(return_str)
            if pattern and re.search(pattern, return_str):
                return return_str
            time.sleep(0.05)
        return_str

    def send(self, string):
        """send a string to the process

        :param string: string to send
        :type string: str
        :return: self
        :rtype: class minExpect
        """
        self.child.stdin.write(string.encode("utf-8"))
        self.child.stdin.flush()
        return self

    def close(self):
        """close the process streams and wait for the process to exit

        :return: self
        :rtype: class minExpect
        """
        # close all the standard streams
        try:
            self.child.stdin.close()
            self.child.stdout.close()
            if self.child.stderr is not None:
                self.child.stderr.close()
        except:
            print("error closing streams")
            pass
        if isWindows():
            stop_pid(self.child.pid)
        
            
        
        try:
            # wait for the process to exit
            self.child.wait(timeout=.5)  # wait for the process to exit
        except subprocess.TimeoutExpired:
            pass
        
        try:
            # wait for the process to exit
            if self.child.poll() is  None:
                self.child.terminate()
                self.child.wait(timeout=4)  # wait for the process to exit
        except subprocess.TimeoutExpired:
            print("timeout on close")
            if isWindows():
                    stop_pid(self.child.pid, force=True)

            if self.child.poll() is  None:
                self.child.kill()  # kill the process if it doesn't exit

            pass
        return self.child.poll()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False


if __name__ == "__main__":
    # test the class
    with minExpect("cmd.exe") as child:
        time.sleep(1)
        ## read the output from the child process
        # (this is a blocking call)
        child.expectto(">")

        child.send("dir\n")
        out = child.expectto(">")

        print(out)
