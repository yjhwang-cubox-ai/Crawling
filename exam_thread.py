import threading
import time

class Worker(threading.Thread):
    def __init__(self,name):
        super().__init__()
        self.name = name
        
    def run(self):
        print("sub thread start ", threading.current_thread().getName())
        time.sleep(3)
        print("sub thread end", threading.current_thread().getName())

print("Main thread start")

for i in range(5):
    name = "thread {}".format(i)
    t = Worker(name)
    t.start()
    
print("main thread end")