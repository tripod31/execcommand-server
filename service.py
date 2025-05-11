import win32service
import win32serviceutil
import win32event
import subprocess
import os
import signal
from win32evtlog import EVENTLOG_INFORMATION_TYPE, EVENTLOG_WARNING_TYPE, EVENTLOG_ERROR_TYPE
import sys
import psutil
import logging

PROG    =os.path.join(os.path.dirname(__file__),"app.py")  #サービス化する常駐プログラム
LOGFILE =os.path.join(os.path.dirname(__file__),r"log\service.txt"),

logging.basicConfig(
    filename = LOGFILE,
    level = logging.DEBUG, 
    format="%(asctime)s:LINE[%(lineno)s] %(levelname)s %(message)s"
)

def kill_child_proc(ppid):
    """
    親プロセスのpidを指定してそのプロセスの子プロセスをkill
    """
    for process in psutil.process_iter():
        _ppid = process.ppid()
        if _ppid == ppid:
            _pid = process.pid
            if sys.platform == 'win32':
                process.terminate()
            else:
                os.system('kill -9 {0}'.format(_pid))

class MyService(win32serviceutil.ServiceFramework):
    _svc_name_          = 'execcommand-server'
    _svc_display_name_  = 'execcommand-server'
    _svc_description_   = 'execcommand-server'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        command = "python " + PROG
        self.proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        logging.info(f"Started {PROG} pid={self.proc.pid}")
        ret = win32event.WaitForSingleObject(self.hWaitStop,win32event.INFINITE)

        kill_child_proc(self.proc.pid)
        os.kill(self.proc.pid, signal.SIGTERM)       
        logging.info(f"Killed {PROG} pid={self.proc.pid}")

if __name__=='__main__':
    win32serviceutil.HandleCommandLine(MyService)