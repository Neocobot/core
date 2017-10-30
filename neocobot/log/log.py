'''
@Project: Neocobot

@Created: 06-June-2017 by Chen Zhuo
'''
import threading
import datetime
import time
import os
import inspect
dir_path = None
file = [None, None, None]
mutex = threading.RLock()

class Log:
    INFO = '[INFO]'
    ERROR = '[ERROR]'
    WARNING = '[WARNING]'
    log_file = "log.txt"
    index = 0

    def log(self, log_type, message, display):
        global file, mutex, dir_path
        folder_path = os.path.abspath(os.path.dirname(inspect.stack()[0][1]))
        if dir_path is None:
            current_time = time.strftime("%Y%m%d_%H%M%S")
            dir = 'data/' + current_time
            dir_path = os.path.normpath(os.path.join(folder_path, dir))
            if not os._exists(dir_path):
                os.mkdir(dir_path)

        mutex.acquire()
        if file[self.index] is None:
            try:
                log_path = os.path.normpath(os.path.join(dir_path, self.log_file))
                file[self.index] = open(log_path, "w")
            except Exception as e:
                Log.write(Log.WARNING, str(e))

        current_time = str(datetime.datetime.now())
        complete_message = log_type + "["+current_time+"] "+message
        try:
            file[self.index].write(complete_message+"\n")
            file[self.index].flush()
            mutex.release()
            if display:
                print(complete_message)
        except Exception as e:
            Log.write(Log.WARNING, str(e))

    def close(self):
        global file
        if file[self.index] is not None:
            file[self.index].close()

    @staticmethod
    def write(log_type, message, display=True):
        threading.Thread(target=Log().log, args=(log_type,  message, display)).start()


class PoseLog(Log):
    log_file = 'pose.txt'
    index = 1

    @staticmethod
    def write(log_type, message, display=False):
        threading.Thread(target=PoseLog().log, args=(log_type,  message, display)).start()


class DatabaseLog(Log):
    log_file = 'database.txt'
    index = 2

    @staticmethod
    def write(log_type, message, display=False):
        threading.Thread(target=DatabaseLog().log, args=(log_type,  message, display)).start()
