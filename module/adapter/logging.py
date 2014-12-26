
import logging
import time

from queue import Queue
from threading import Thread, Lock

from library.libmsgbus import msgbus
from library.libtree import tree
from module.adapter.config import configmodule


class log_adapter(Thread, msgbus):
    '''
    classdocs
    '''
    def __init__(self):
        Thread.__init__(self)
        print('init logging')

        self.cfg_queue = Queue()
        self.log_queue = Queue()

    def run(self):
        print ('run logging adapter')

        self.setup()

        threadRun = True

        while threadRun:
            time.sleep(5)
          #  print('logging loop')
            while not self.cfg_queue.empty():
                self.on_cfg(self.cfg_queue.get())

            while not self.log_queue.empty():
                self.on_log(self.log_queue.get())

        return

    def setup(self):
        self.msgbus_subscribe('LOG', self._on_log)
        self.msgbus_subscribe('CONF', self._on_cfg)

    def _on_log(self,log_msg):
        self.log_queue.put(log_msg)
        return

    def _on_cfg(self,cfg_msg):
        self.cfg_queue.put(cfg_msg)
        return

    def on_log(self, logmsg):
   #     print ('logmessage',logmsg)
        if logmsg.startswith('INFO'):
            msg = logmsg.replace('INFO','')
            self.info(msg.strip())
        elif logmsg.startswith('WARNING'):
            msg = logmsg.replace('WARNING','')
            self.warning(msg.strip())
        elif logmsg.startswith('ERROR'):
            msg = logmsg.replace('ERROR','')
            self.error(msg.strip())
        elif logmsg.startswith('CRITICAL'):
            msg = logmsg.replace('CRITICAL','')
            self.critical(msg.strip())
        elif logmsg.startswith('DEBUG'):
            msg = logmsg.replace('DEBUG','')
            self.debug(msg.strip())
        else:
            self.debug(logmsg.strip())

    def on_cfg(self,cfg_msg):
       # print('Config message',cfg_msg)
        general = cfg_msg.select('GENERAL')
        self.msgbus_publish('LOG','%s Logger Configuration %s '%('INFO', general.getTree()))

        logfile = general.getNode('LOGFILE','/var/log/mqtt2gpio.log')
        logmode = general.getNode('LOGMODE','INFO')
        self.open(logfile,logmode)


    def open(self, LOGFILE,LOGMODE):
        '''
        Constructor
        '''
 #       logging.__init__(self)
        LOGFORMAT = '%(asctime)-15s - %(levelname)s - %(message)s'
        LOGFORMAT_DEBUG = '%(asctime)-15s - %(message)s'


        if 'INFO' in LOGMODE:
            logging.basicConfig(filename=LOGFILE, level=logging.INFO, format=LOGFORMAT)
        elif 'WARNING' in LOGMODE:
            logging.basicConfig(filename=LOGFILE, level=logging.WARNING, format=LOGFORMAT)
        elif 'ERROR' in LOGMODE:
            logging.basicConfig(filename=LOGFILE, level=logging.ERROR, format=LOGFORMAT)
        elif 'CRITICAL' in LOGMODE:
            logging.basicConfig(filename=LOGFILE, level=logging.CRITICAL, format=LOGFORMAT)
        else:
            logging.basicConfig(filename=LOGFILE, level=logging.DEBUG, format=LOGFORMAT_DEBUG)

    def info(self,msg, *args, **kwargs):

        logging.info(msg, *args, **kwargs)

    def warning(self,msg, *args, **kwargs):
        logging.warning(msg, *args, **kwargs)

    def error(self,msg, *args, **kwargs):
        logging.error(msg,*args, **kwargs)

    def critical(self,msg, *args, **kwargs):
        logging.critical(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        logging.debug(msg, *args, **kwargs)

