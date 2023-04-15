# Description: This script will print a message every second until the process is killed.
# used to test the minexpect.py script

import time

try:
    while True:
        print(f"Process running, {time.time()}")
        time.sleep(1)

except SystemExit:
    print("SystemExit")
    pass