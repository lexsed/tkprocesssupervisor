
import time
from mypgroup import myprocess, MyPGroup
pges = [{  
                'name': 'SimultaneousPlayAzElDmp',
             'command': "python endlessprint.py",
                 'run': False    }]
                

try:
    with MyPGroup({},pges) as pg:
        pg.start_all()


        process = pg.get_process("SimultaneousPlayAzElDmp")
        for i in range(20):
            print(f'Running: {process.running()}  backoff: {process.backoff}')
            if process.running():
                print(process.readbuffer())
            time.sleep(.5)

        pg.restart_all()
        while True:
            print(f'Running: {process.running()}  backoff: {process.backoff}')
            if process.running():
                print(process.readbuffer())
            time.sleep(.5)

except KeyboardInterrupt:
    pass


    
                

