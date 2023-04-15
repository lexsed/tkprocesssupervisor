import time

try:
    while True:
        print(f"Process running, {time.time()}")
        time.sleep(1)

except SystemExit:
    print("SystemExit")
    pass