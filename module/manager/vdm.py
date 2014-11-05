
from threading import Thread, Lock
from queue import Queue
import time

from module.general.msgbus import MsgBus
from module.general.dicttree import DictionaryTree

from module.interface.vpm.binary_out import VPM_BinaryOut

from module.hardware.mcp23017 import MCP23017
from module.hardware.raspberry import Raspberry

class VDM(Thread,MsgBus):

    def __init__(self, ThreadName):
        Thread.__init__(self)

        self.ThreadName = ThreadName
        self.cfgQ = Queue()
        self.reqQ = Queue()
        self.nofyQ = Queue()

        self._THREAD_UPDATE = 0.1
        self._DEVICE_TYPE = ''
        self._DEVICE_NAME = ''

        self.VDMcfg = ''
        self._VPMInstance = []

        print ('VDM init', self.ThreadName)

        self.Setup()

    def run(self):
        time.sleep(2)
        while(True):
            time.sleep(1)
            print('#',self.ThreadName)
            '''
            are configurations pending in the queue
            '''
            if not self.cfgQ.empty():
                '''
                configurations are concerning this thread
                '''
                print('cfgQ is not empty')
                dataQ = self.cfgQ.get()
                print('DataQ',dataQ)
                threadCfg = dataQ.get(self.ThreadName,None)
                print('thread config available',self.ThreadName,threadCfg)
                if threadCfg:
                    '''
                    configuration is concerning this thread
                    make local config
                    and distribut config to Virtual Port Manager
                    '''
                    VDMcfg = DictionaryTree(threadCfg)
                    self._VDMConfig(VDMcfg.GetLeafs())
                    self._VPMcfg(VDMcfg.GetNodes())

            '''
            are request pending in the queue
            '''
            if not self.reqQ.empty():
                '''
                request is concerning this thread
                '''
                threadReq = self.reqQ.get(self.ThreadName,None)
                if threadReq:
                    '''
                    request is concerning this thread
                    send forward to Virtual Port Manager
                    '''
                    VPMreq = DictionaryTree(threadReq())
                    self._VPMreq(VPMreq.GetNodes())







    def Setup(self):
        '''
        Subscribe to Notification Channels
        '''
        self.subscribe('VDM_CFG', self.ConfigIF)
        self.subscribe('VDM_REQ', self.RequestIF)
    #    self.subscribe('VDM_NOFY', self.NotifyIF)

        print('VDM Setup Completed')

    def ConfigIF(self,msg):
        '''
        Configuration Interface
        '''
        self.cfgQ.put(msg)
        print('VDM received message store in Queue', self.ThreadName,msg)

    def RequestIF(self,msg):
        '''
        Request Interface
        '''
        self.reqQ.put(msg.get('VDM_REQ',None))


    def _VDMConfig(self, cfgMsg):
        print('VDM configuration message',self.ThreadName,cfgMsg)
        self._DEVICE_TYPE = cfgMsg.get('TYPE')
        self._DEVICE_NAME = cfgMsg.get('NAME')
        self._THREAD_UPDATE = float(cfgMsg.get('UPDATE',0.1))

    def _VPMcfg(self,cfgMsg):
        print ('VPM configuration messages',self.ThreadName,cfgMsg)
        VPMcfg = DictionaryTree(cfgMsg)

        if 'MCP23017' in self._DEVICE_TYPE:
            self._RASPBERRY_REV = int(self.VDMcfgMsg.get('RASPBERRY_REV',1))
            self._I2C_ADDRESS = int(self.VDMcfgMsg.get('I2C_ADDRESS'),16)
            self._hwHandle = MCP23017(self._RASPBERRY_REV,self._I2C_ADDRESS)

            for cfgItem in VPMcfg:
                VPMName = cfgItem.get('NAME')

                if 'BINARY-OUT' in cfgItem.get('MODE'):
                    self._VPMInstance[VPMName](VPM_BinaryOut(self._hwHandle, self._DEVICE_TYPE, cfgItem))
                elif 'BINARY-IN' in cfgItem.get('MODE'):
#                    self._VPMInstance[VPMName](VPM_BinaryIn(self._hwHandle, self._DEVICE_TYPE, cfgItem))
                    print('')

        elif 'RASPBERRY' in self._DEVICE_TYPE:
            self._RASPBERRY_REV = int(self.VDMcfgMsg.get('RASPBERRY_REV',1))
            self._I2C_ADDRESS = int(self.VDMcfgMsg.get('I2C_ADDRESS'),16)
            self._hwHandle = Raspberry()
            print('')



