
import logging

from library.libmsgbus import msgbus
from module.adapter.config import configmodule

# Singleton/SingletonDecorator.py
class SingletonDecorator:
    def __init__(self,klass):
        self.klass = klass
        self.instance = None
    def __call__(self,*args,**kwds):
        if self.instance == None:
            self.instance = self.klass(*args,**kwds)
        return self.instance

class logwrapper(msgbus):
    '''
    classdocs
    '''
    def __init__(self):

        self.msgbus_subscribe('LOG', self._on_log)
        self.msgbus_subscribe('CONF', self._on_config)

    def _on_log(self, logmsg):
        if logmsg.startswith('INFO'):
            msg = logmsg.replace('INFO','')
            self.info(msg.strip())
        elif logmsg.startwith('WARNING'):
            msg = logmsg.replace('WARNING','')
            self.warning(msg.strip())
        elif logmsg.startwith('ERROR'):
            msg = logmsg.replace('ERROR','')
            self.error(msg.strip())
        elif logmsg.startwith('CRITICAL'):
            msg = logmsg.replace('CRITICAL','')
            self.critical(msg.strip())
        else:
            self.info(logmsg.strip)

    def _on_config(self,conf_msg):
        print('Config message',conf_msg)
        print(type(conf_msg))
        x = configmodule()
        general = x.loadDict(conf_msg.select('GENERAL'))
        print('test',conf_msg.select('GENERAL'))
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


class logwrapper_old(object):
    '''
    classdocs
    '''
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


loghandle = SingletonDecorator(logwrapper)