from threading import Thread
from queue import Queue
import time

from library.libmsgbus import msgbus

'''
import device interface drivers
'''
from module.devices.raspberry import raspberry
from module.devices.mcp23017 import MCP23017

'''
import port manager
'''
from module.manager.vpm.binin import binin
from module.manager.vpm.binout import binout
from module.manager.vpm.trigger import trigger
#from module.manager.vpm.pulse import pulse
#from module.manager.vpm.pwm import pwm
#from module.manager.vpm.timerin import timerin

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
            print('VDM loop Device ',self._DevName, len(self._VPMobj), self._UPDATE)

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
        '''
        called by main thread in case request queue contains requests
        :param msg: message from VHM instance as dictionary
        :return: if message could be deliverd to VPM instance True else False
        '''
        result = False

        '''
        Selects only concerning information from Dictionary, in case it's not concerning this task we return
        '''

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
                    result = True

        return result

    def on_config(self,cfg_msg):
        '''
        configures the VDM thread
        :param cfg_msg: configuration message as Tree object
        :return:in case HW interface started True else False
        '''

        result = False

        '''
        selects the concerning branch of the Tree object
        '''
        device = cfg_msg.select(self._DevName)
        self.msgbus_publish('LOG','%s VDM Configuration Update for Device: %s, Config: %s '%('INFO', self._DevName, device.getTree()))
        print('VDMgetNodes',device.getNodesKey())

        '''
        reads mandatory configurations from tree object
        '''
        self._DEVICE_TYPE = str(device.getNode('TYPE','RASPBERRY'))
        self._UPDATE = float(device.getNode('UPDATE',0.1))

        '''
        starts the concerning HW interface which will be managed be the Virtual Device Manager
        '''

        '''
        manage the MCP23017 GPIO interface connected via i2c interface, reads all configuration parameter from configuration tree object
        handle to the hardware drive object stored in self._hwHandle
        '''

        if 'MCP23017' in self._DEVICE_TYPE:
            self.msgbus_publish('LOG','%s VDM Start HW Manager for Device: %s, Type: %s'%('INFO', self._DevName, self._DEVICE_TYPE))
            self._SYSTEM_TYPE = str(device.getNode('SYSTEM','RASPBERRY_B1'))
            self._I2C_ADDRESS = int(device.getNode('I2C_ADDRESS'),16)
            if 'RASPBERRY_B1' in self._SYSTEM_TYPE:
                self._hwHandle = MCP23017(1,self._I2C_ADDRESS)
            elif 'RASPBERRY_A1' in self._SYSTEM_TYPE:
                self._hwHandle = MCP23017(0,self._I2C_ADRESS)
            else:
                print('ERROR unknown device type', self._SYSTEM_TYPE)

            result = True

            '''
            manage the Raspberry GPIOs
            '''
        elif 'RASPBERRY' in self._DEVICE_TYPE:
            self.msgbus_publish('LOG','%s VDM Start HW Manager for Device: %s, Type %s'%('INFO', self._DevName, self._DEVICE_TYPE))
            self._SYSTEM_TYPE = str(device.getNode('SYSTEM','RASPBERRY_B1'))
            self._hwHandle = raspberry()
            #device.addNode('HW_HANDLE', self._hwHandle)
            result = True

            '''
            add more HW interface driver in the future
            '''
        else:
            self.msgbus_publish('LOG','%s VDM Start HW Manager for Device: %s, UNKNOWN'%('INFO', self._DevName))
            result = False
            print('VDM:: unknown device',self._DEVICE_TYPE)

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
        '''
        list devices of VPM to be stopped
        '''
        self.stop_vpm(list(run_device.difference(cfg_device)))
        '''
        VPM devices to be configured
        '''
        print ('VDM::Configure existing VPMs:',device.getNodesKey())
        self.cfg_vpm(device)

        return result


    def start_vpm(self,device,cfg_msg):
        '''
        starts the VPM de device
        :param device: contains the list of devices to be started
        :param cfg_msg: configuration for all Virtual Port Managers managed by this VDM instance, as tree type object
        :return: True in case VDM could be started else False
        '''

        result = False

        for portID in device:
            port_cfg = cfg_msg.select(portID)
            self._PIN_MODE = str(port_cfg.getNode('MODE'))
            print ('start vpm mode',port_cfg.getNode('MODE'),portID,self._hwHandle,port_cfg)

            '''
            Start virtual port manager according configuration
            HW handle, notify channel and saved in _VPMobj dictionary
            '''
            if 'BINARY-OUT' in self._PIN_MODE:
                self._VPMobj[portID]=binout(portID,self._hwHandle,self._on_notify)
                result = True

            elif 'BINARY-IN' in self._PIN_MODE:
                self._VPMobj[portID]=binin(portID,self._hwHandle,self._on_notify)
                result = True

            elif 'TRIGGER' in self._PIN_MODE:
                self._VPMobj[portID]=trigger(portID,self._hwHandle,self._on_notify)
                result = True

            else:
                self.msgbus_publish('LOG','%s VPM mode of Port %s not fond %s '%('ERROR', portID,port_cfg.getNode('MODE')))
                result = False

        return result

    def stop_vpm(self,device):
        '''
        stops all VPM devices listed in device list
        :param device: name of device
        :return: true in case deletion was successful else False
        '''

        result = False

        print('VDM stop VPM instanced', device)
        if len(device)> 0:
            for port in device.getNodesKey():
                self.msgbus_publish('LOG','%s Stop VPM Devices: %s , Port: %s '%('INFO', self._DevName, port))
                del self._VPMobj[port]
                result = True
        return result

    def cfg_vpm(self,device):
        '''
        sends configuration message to all VPMs managed by this VDM instance
        :param device: configuration as device tree object
        :return: True
        '''

        self.msgbus_publish('LOG','%s VDM Configuration VPM devices: %s '%('INFO', device))
        print ('DEVICES to configure',device.getNodesKey())
        for port in device.getNodesKey():
            print('Device:', self._DevName,'Port:',port)
            self._VPMobj[port].config(device)
#        self.msgbus_publish(self._commConf_Handle, self._on_cfg)

        return True
