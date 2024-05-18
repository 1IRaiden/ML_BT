import concurrent.futures
import threading
import time


# first examples:
def func(i):
    print(f"Hello World{i}" +'\n')
    time.sleep(2)
    print(time.time())
    return 5

with concurrent.futures.ThreadPoolExecutor( max_workers=5) as executor:
    futures = [executor.submit(func, i) for i in range(5)]
    #for future in concurrent.futures.as_completed(futures):
     #   print(future.result())
