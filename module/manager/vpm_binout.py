
import json
from queue import Queue

from library.libmsgbus import msgbus



class vpm_binout(msgbus):
    '''
    classdocs
    '''
    def __init__(self,portName):

#        self._PortName

        self._portName = portName
        print('VPM binout init :', self._portName)

        '''
        queues
        '''
        self.cfgQ = Queue()
        self.req_vpmQ = Queue()

        '''
        Constructor
        '''
        self._hwId = 0
        self._name = ''
        self._mode = 'BINARY-OUT'

        self._log = 'LOG'


        self.setup()

    def setup(self):
        self.msgbus_publish('LOG','%s VPM Module BINARY OUT Setup Configuration: %s '%('INFO', self._portName))

    def run(self):
        print ('VPN BinOut')

    def _on_cfg(self,cfg_msg):
        '''
        Called from message bus and saves message into queue
        :param cfg_msg: configuration message
        :return: none
        '''
        self.cfgQ.put(cfg_msg)
        return

    def on_cfg(self,cfg_msg):
      #  print('VPM received configuration message:',cfg_msg.getTree())
        self._HW_HANDLE = cfg_msg.getNode('HW_HANDLE')
        self._port_cfg = cfg_msg.select(self._portName)
        print('VPM received configuration message:',self._portName,self._port_cfg.getTree())
        self.msgbus_publish(self._log,'%s VPM Module %s Config Update Port: %s, Message: %s'%('INFO',self._mode, self._portName, self._port_cfg.getTree()))