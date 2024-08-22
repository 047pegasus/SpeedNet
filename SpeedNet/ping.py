# program to ping a given IP address and check whether it is reachable or not, that returns True or False and also keeps a system log in a separate file called system_log.txt with the result of the ping. Before writing the result to the file, it should check if the file exists or not. If it does not exist, it should create the file and also check if the file is being used by any other program to write, then it must wait until it acquires the lock and then it shall start to write.
import os
import time
import platform
import threading

def ping(ip):
    if platform.system().lower() == "windows":
        ping_str = "-n 1"
    else:
        ping_str = "-c 1"

    response = os.system("ping " + ping_str + " " + ip)
    r = os.popen("ping " + ping_str + " " + ip).read()

    # get the std out of the command and write it to the log file while maintaing asynchronous writing and also first acquire then write and then release the lock
    thread = threading.Thread(target=write_to_file, args=("system_log.txt", str(r)))
    thread.start()
    thread.join()

    if response == 0:
        return True
    else:
        return False

def write_to_file(file_name, data):
    while os.path.exists(file_name):
        try:
            with open(file_name, "a") as file:
                file.write(data)
                file.write("\n")
                break
        except:
            time.sleep(1)
    else:
        with open(file_name, "w") as file:
            file.write(data)
            file.write("\n")

ping("google.com")