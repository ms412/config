from threading import Thread
from queue import Queue
import time

from library.libmsgbus import msgbus

from module.manager.vpm.binin import binin
from module.manager.vpm.binout import binout
from module.devices.mcp23017 import MCP23017


#from module.devices.raspberry import Raspberry

class vdm(Thread,msgbus):
    '''
    Number of started VDMs depends on numbers of configured Devices, each device has is own thread

    Channels Subscribe:
    CONFIG_VDM: receives the configuration message for all VDMs

    Channels Publish:
    LOG sends log messages to the logging interface

    Configuration IF:

    Mandatory Thread Parameters
        _DevName: contains name of the running VDM instance; name must be consistent with the configuration file, name can be freely chosen
        callback: contains the callback method of the VHM instance to which Notifications are to be published

    Mandatory Configuration Parameters:
        TYPE: Type of the Hardware Interface, default Raspberry
        SYSTEM: information of the board the gpio2mqtt adapter works on

    Mandatory Configuration Parameters for Rsaspberry Device:
        None

    Mandatory Configuration Parameters for 23017 Devices:
        I2C_ADDRESS: address of the i2c device at the first bus in Hex notification 0x1A


    Optional Configuration Parameters:
        UPDATE: time of the execution cycle of the thread expressed in seconds, default 1 sec

    '''

    def __init__(self,DevName,callback):
        Thread.__init__(self)

        self._DevName = DevName
     #   print('##VDM##',self._DevName)

        '''
        queues
        '''
        self.cfgQ = Queue()
        #self.notify_vdmQ = Queue()
        self.reqQ = Queue()
        self.notifyQ =Queue()

        '''
        mandatory VDM data
        '''
        self._UPDATE = 1
        self._DEVICE_TYPE = ''
       # self._DEVICE_NAME = ''

       # self._VPMInstance = {}

        '''
        contains all active VPM instances managed by thread
        '''
        self._VPMobj = {}

        '''
        Hardware handel stores the handle to the hardware
        only once available per VDM instance
        '''
        self._hwHandle = None

        '''
        callback
        '''
        self._callback = callback


        self.setup()

    def __del__(self):
        '''
        stop all concerning VPM objects before destroying myself
        '''

        for key, value in self._VPMobj:
            del value

        self.msgbus_publish('LOG','%s VDM Module Destroying myself: %s '%('INFO', self._DevName))


    def setup(self):

        self.msgbus_subscribe('CONFIG_VDM', self._on_config)
     #   self.msgbus_subscribe('REQ_VDM', self._on_req)
        #self.msgbus_subscribe(self._commNotifyVHMCh, self._on_vpm_notify)

        return True

    def _on_config(self,msg):
        self.cfgQ.put(msg)
        return True

    def _on_request(self,msg):
        self.reqQ.put(msg)
        return True

    def _on_notify(self,msg):
        self.notifyQ.put(msg)
        return True

    def run(self):

      #  self.msgbus_publish('LOG','%s VDM Virtual Device Manager %s Startup'%('INFO', self._DevName))
        threadRun = True

        while threadRun:
            time.sleep(self._UPDATE)
            print('VDM loop Device ',self._DevName, len(self._VPMobj))

            while not self.cfgQ.empty():
                self.on_config(self.cfgQ.get())

            while not self.reqQ.empty():
                self.on_request(self.reqQ.get())

            while not self.notifyQ.empty():
                self.on_notify(self.notifyQ.get())

            '''
            trigger VPM instances
            '''
            for key,value in self._VPMobj.items():
                value.run()

        return True

    def on_notify(self, msg):
        '''
        receives notification from VPM instance and forwards it to VHM by adding device message header with name of VDM instance
        :param msg: message from VPM instance as dictionary
        :return: True
        '''

        device_msg= {}
        device_msg[self._DevName]=msg
        self._callback(device_msg)

        return True

    def on_request(self,msg):
        device = msg.get(self._DevName,None)

        if not device:
            self.msgbus_publish('LOG','%s VDM Request not for Device: %s'%'INFO',self._DevName)
        else:
            for k in device.keys():
                port = self._VPMobj.get(k,None)
                if not port:
                    self.msgbus_publish('LOG','%s VDM Requested Port does not exist: %s in Device: %s'%'ERROR',k,self._DevName)
                else:
                    port.request(device.get(k))

        return True



    def on_cfg(self,cfg_msg):

        device = cfg_msg.select(self._DevName)
        self.msgbus_publish('LOG','%s VDM Configuration Update for Device: %s, Config: %s '%('INFO', self._DevName, device.getTree()))
        print('VDMgetNodes',device.getNodesKey())

        '''
        mandatory configurations
        '''
        self._DEVICE_TYPE = str(device.getNode('TYPE','RASPBERRY'))
        self._UPDATE = float(device.getNode('UPDATE',0.1))

        if 'MCP23017' in self._DEVICE_TYPE:
            self.msgbus_publish('LOG','%s VDM Start HW Manager for Device: %s, Type: %s'%('INFO', self._DevName, self._DEVICE_TYPE))
            self._SYSTEM_TYPE = str(device.getNode('SYSTEM','RASPBERRY_B1'))
            self._I2C_ADDRESS = int(device.getNode('I2C_ADDRESS'),16)
            self._hwHandle = MCP23017(self._SYSTEM_TYPE,self._I2C_ADDRESS)
       #     device.addNode('HW_HANDLE', self._hwHandle)
      #      device.addNode('DEVICE_ID', self._DevName)


        elif 'RASPBERRY' in self._DEVICE_TYPE:
            self.msgbus_publish('LOG','%s VDM Start HW Manager for Device: %s, Type %s'%('INFO', self._DevName, self._DEVICE_TYPE))
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
        print('VDM::VPM ports to confiure:', cfg_device,'run:',run_device)
        '''
        list devices of VPM to be started
        '''
        print('VDM::START VPM',list(cfg_device.difference(run_device)))
        self.start_vpm(list(cfg_device.difference(run_device)),device)
#self.start_vdm(list(cfg_devices.difference(run_devices)))
        '''
        list devices of VPM to be stopped
        '''
        self.stop_vpm(list(run_device.difference(cfg_device)))
        '''
        VPM devices to be configured
        '''
        print ('VDM::Configure existing VPMs:',device.getNodesKey())
        self.cfg_vpm(device)


    def start_vpm(self,device,cfg_msg):
      #  self.msgbus_publish('LOG','%s VDM %s, Start VPM devices: %s, Config: %s '%('INFO', self._DevName,device,cfg_msg))
        for portID in device:
            port_cfg = cfg_msg.select(portID)
            self._SYSTEM_TYPE = str(port_cfg.getNode('MODE'))
            print ('start vpm mode',port_cfg.getNode('MODE'),portID,self._hwHandle,port_cfg)

            '''
            Start virtual port manager according configuration
            HW handle, notify channel
            '''
            if 'BINARY-OUT' in self._SYSTEM_TYPE:
                self._VPMobj[portID]=binout(portID,self._hwHandle,self._on_notify_VDM)

            elif 'BINARY-IN' in self._SYSTEM_TYPE:
                self._VPMobj[portID]=binin(portID,self._hwHandle,self._on_notify_VDM)

            else:
                self.msgbus_publish('LOG','%s VPM mode of Port %s not fond %s '%('ERROR', portID,port_cfg.getNode('MODE')))

        return

    def stop_vpm(self,device):
       # self.msgbus_publish('LOG','%s Stop VPM Devices: %s , Port: %s '%('INFO', self._DevName, device))
        print('VDM stop VPM instanced', device)
        if len(device)> 0:
            for port in device.getNodesKey():
                self.msgbus_publish('LOG','%s Stop VPM Devices: %s , Port: %s '%('INFO', self._DevName, port))
                del self._VPMobj[port]
        return

    def cfg_vpm(self,device):
        self.msgbus_publish('LOG','%s VDM Configuration VPM devices: %s '%('INFO', device))
        print ('DEVICES to configure',device.getNodesKey())
        for port in device.getNodesKey():
            print('Device:', self._DevName,'Port:',port)
            self._VPMobj[port].on_cfg(device)
#        self.msgbus_publish(self._commConf_Handle, self._on_cfg)

        return
