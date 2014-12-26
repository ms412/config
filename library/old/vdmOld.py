from threading import Thread
from queue import Queue
import time

from library.libmsgbus import msgbus

from module.manager.vpm import binin, binout
from module.devices.mcp23017 import MCP23017


#from module.devices.raspberry import Raspberry

class vdm(Thread,msgbus):

    def __init__(self, DevName):
        Thread.__init__(self)

        self._DevName = DevName
        print('##VDM##',self._DevName)

        '''
        queues
        '''
        self.cfgQ = Queue()
        self.notify_vdmQ = Queue()
        self.req_vdmQ = Queue()

        '''
        mandatory VDM data
        '''
        self._UPDATE = 0.1
        self._DEVICE_TYPE = ''
        self._DEVICE_NAME = ''

       # self._VPMInstance = {}

        '''
        contains all active VPM instances managed by thread
        '''
        self._VPMobj = {}

        '''
        subscribe channels
        '''
        self._commConfVDMCh = 'CFG'
        self._commReqVDMCh = 'REQ_VDM'
        '''
        publish channels
        '''
        self._logCh = 'LOG'
        self._commNotifyVHMCh = 'NOTIFY_VHM'


        self.setup()

    def setup(self):

        self.msgbus_subscribe(self._commConfVDMCh, self._on_cfg)
        self.msgbus_subscribe(self._commReqVDMCh, self._on_vdm_request)
        self.msgbus_subscribe(self._commNotifyVHMCh, self._on_vpm_notify)

    def run(self):

        self.msgbus_publish(self._logCh,'%s VDM Virtual Device Manager %s Startup'%('INFO', self._DevName))
        threadRun = True

        while threadRun:
            time.sleep(self._UPDATE)
            print('VDM loop Device ',self._DevName, len(self._VPMobj))

            while not self.cfgQ.empty():
                self.on_cfg(self.cfgQ.get())

          #  if len(self._VPMobj) > 0:
            for key,value in self._VPMobj.items():
                value.run()




    def on_cfg(self,cfg_msg):

        device = cfg_msg.select(self._DevName)
        self.msgbus_publish(self._logCh,'%s VDM Configuration Update for Device: %s, Config: %s '%('INFO', self._DevName, device.getTree()))
        print('VDMgetNodes',device.getNodesKey())

        '''
        mandatory configurations
        '''
        self._DEVICE_TYPE = str(device.getNode('TYPE','RASPBERRY'))
        self._UPDATE = float(device.getNode('UPDATE',0.1))

        if 'MCP23017' in self._DEVICE_TYPE:
            self.msgbus_publish(self._logCh,'%s VDM Start HW Manager for Device: %s, Type: %s'%('INFO', self._DevName, self._DEVICE_TYPE))
            self._SYSTEM_TYPE = str(device.getNode('SYSTEM','RASPBERRY_B1'))
            self._I2C_ADDRESS = int(device.getNode('I2C_ADDRESS'),16)
            self._hwHandle = MCP23017(self._SYSTEM_TYPE,self._I2C_ADDRESS)
            device.addNode('HW_HANDLE', self._hwHandle)
      #      device.addNode('DEVICE_ID', self._DevName)

        elif 'RASPBERRY' in self._DEVICE_TYPE:
            self.msgbus_publish(self._logCh,'%s VDM Start HW Manager for Device: %s, Type %s'%('INFO', self._DevName, self._DEVICE_TYPE))
            self._SYSTEM_TYPE = str(device.getNode('SYSTEM','RASPBERRY_B1'))
            device.addNode('HW_HANDLE', self._hwHandle)
           # device.addNode('HW_HANDELE', self._hwHandle)
           # device.addNode('DEVICE_ID', self._DevName)
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
        self.msgbus_publish(self._logCh,'%s VDM %s, Start VPM devices: %s, Config: %s '%('INFO', self._DevName,device,cfg_msg))
        for port in device:
            port_cfg = cfg_msg.select(port)
            self._SYSTEM_TYPE = str(port_cfg.getNode('MODE'))
            print ('start vpm mode',port_cfg.getNode('MODE'),port,self._hwHandle,port_cfg)

            '''
            Start virtual port manager according configuration
            HW handle, notify channel
            '''
            if 'BINARY-OUT' in self._SYSTEM_TYPE:
                self._VPMobj[port]=binout(port)

            elif 'BINARY-IN' in self._SYSTEM_TYPE:
                self._VPMobj[port]=binin(port)

            else:
                self.msgbus_publish('LOG','%s VPM mode of Port %s not fond %s '%('ERROR', item,port_cfg.getNode('MODE')))

        return

    def stop_vpm(self,device):
        self.msgbus_publish('LOG','%s VDM Stop VPM devices %s '%('INFO', device))
        return

    def cfg_vpm(self,device):
        self.msgbus_publish('LOG','%s VDM Configuration VPM devices: %s '%('INFO', device))
        for port in device.getNodesKey():
            self._VPMobj[port].on_cfg(device)
#        self.msgbus_publish(self._commConf_Handle, self._on_cfg)

        return
