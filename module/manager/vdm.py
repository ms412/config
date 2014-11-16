
from threading import Thread, Lock
from queue import Queue
import time

from library.libmsgbus import msgbus
from library.libtree import tree

from module.manager.vpm_binout import vpm_binout
#from module.manager.vpm_binin inport vpm_binin

from module.devices.mcp23017 import MCP23017
#from module.devices.raspberry import Raspberry

class vdm(Thread,msgbus):

    def __init__(self, DevName):
        Thread.__init__(self)

        self._DevName = DevName

        '''
        queues
        '''
        self.cfgQ = Queue()
        self.notify_vdmQ = Queue()
        self.req_vdmQ = Queue()

        '''
        mandatory VDM data
        '''
        self._THREAD_UPDATE = 0.1
        self._DEVICE_TYPE = ''
        self._DEVICE_NAME = ''

        self._VPMInstance = []

        '''
        contains all active VPM instances managed by thread
        '''
        self._VPMobj = {}


        self.setup()

    def setup(self):

        self.msgbus_subscribe('VDM_CONF', self._on_cfg)
        self.msgbus_subscribe('VPM_REQUEST', self._on_vdm_request)
        self.msgbus_subscribe('VHM_NOTIFY', self._on_vpm_notify)

    def run(self):

        """

        :type self: object
        """
        self.msgbus_publish('LOG','%s VDM Virtual Device Manager %s Startup'%('INFO', self._DevName))
        threadRun = True

        while threadRun:
            time.sleep(1)
            print('VDM loop Device ',self._DevName)

            while not self.cfgQ.empty():
                self.on_cfg(self.cfgQ.get())



    def on_cfg(self,cfg_msg):

        device = cfg_msg.select(self._DevName)
        self.msgbus_publish('LOG','%s VDM Configuration Update for Device: %s received %s '%('INFO', self._DevName, device.getTree()))
        print('getNodes',device.getNodesKey())

        '''
        mandatory configurations
        '''
        self._DEVICE_TYPE = str(device.getNode('TYPE','RASPBERRY'))
        self._THREAD_UPDATE = float(device.getNode('UPDATE',0.1))

        if 'MCP23017' in self._DEVICE_TYPE:
            self.msgbus_publish('LOG','%s VDM Start HW Manager for Device: %s'%('INFO', self._DEVICE_TYPE))
            self._SYSTEM_TYPE = str(device.getNode('SYSTEM','RASPBERRY_B1'))
            self._I2C_ADDRESS = int(device.getNode('I2C_ADDRESS'),16)
            self._hwHandle = MCP23017(self._SYSTEM_TYPE,self._I2C_ADDRESS)

        elif 'RASPBERRY' in self._DEVICE_TYPE:
            self.msgbus_publish('LOG','%s VDM Start HW Manager for Device: %s'%('INFO', self._DEVICE_TYPE))
            self._SYSTEM_TYPE = str(device.getNode('SYSTEM','RASPBERRY_B1'))
#            self._hwHandle = raspberry()


        '''
        compare running VPM devices with configured devices
        '''
        cfg_device = set(device.getNodesKey())
        run_device = set(self._VPMobj.keys())
        '''
        list devices of VPM to be started
        '''
        self.start_vpm(list(cfg_device.difference(run_device)),device)
        '''
        list devices of VPM to be stopped
        '''
        self.stop_vpm(list(run_device.difference(cfg_device)))
        '''
        VPM devices to be configured
        '''
        self.cfg_vpm(device)





    def _on_cfg(self,cfg_msg):
        '''
        Called from message bus and saves message into queue
        :param cfg_msg: configuration message
        :return: none
        '''
        self.cfgQ.put(cfg_msg)
        return

    def _on_vpm_notify(self,notify):
        self.notify_vdmQ.put(notify)
        return

    def _on_vdm_request(self,req):
        self.req_vdmQ.put(req)
        return

    def start_vpm(self,device,cfg_msg):
        self.msgbus_publish('LOG','%s VDM Start VPM devices: %s '%('INFO', device))
        for item in device:
            port_cfg = cfg_msg.select(item)
            self._SYSTEM_TYPE = str(port_cfg.getNode('MODE'))

            if 'BINARY-OUT' in self._SYSTEM_TYPE:
                self._VPMInstance[item](vpm_binout(port_cfg,self._hwHandle))

            elif 'BINARY-IN' in self._SYSTEM_TYPE:
                self._VPMInstance[item](vpm_binin(port_cfg,self._hwHandle))

        return

    def stop_vpm(self,device):
        self.msgbus_publish('LOG','%s VDM Stop VPM devices %s '%('INFO', device))
        return

    def cfg_vpm(self,device):
        self.msgbus_publish('LOG','%s VDM Configuration VPM devices: %s '%('INFO', device))
        return

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



