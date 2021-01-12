import time
import webbrowser
import threading
import re

class MyThread(threading.Thread):
    def __init__(self, function_pointer):
        threading.Thread.__init__(self)
        self.function_pointer = function_pointer

    def run(self):
        self.function_pointer()
        # application.run()

def authenticate(function_pointer):
    thread = MyThread(function_pointer)
    thread.start()
    print("[+] Waiting for the Flask application to spin up...")
    time.sleep(3)
    webbrowser.open("http://127.0.0.1:5000")
