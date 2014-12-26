import time
from queue import Queue

from library.libmsgbus import msgbus
from module.manager.vdm import vdm


class vhm(msgbus):

    def __init__(self):

        self.cfg_queue = Queue()

        self.req_vhm_queue = Queue()
        self.notify_vdm_queue = Queue()
        '''
        contains all running VDM threads
        '''
        self._threadDict = {}

        self.msgObj = 0

        print ('###InitVHM###')
        self.setup()

    def setup(self):
        self.msgbus_subscribe('CONFIG', self.config)
       # self.msgbus_subscribe('REQ_MSG', self._on_vhm_request)
      #  self.msgbus_subscribe('NOTIFY', self.on_notify)
        self.msgbus_subscribe('REQ_MSG', self.on_request)
        return True

    def on_notify(self,msg):
        print('VHM data received:',msg)
        add_header = {}
        add_header['DEVICES'] = msg
        self.msgbus_publish('DATA_TX',add_header)
        return True

    def on_request(self,msg):
        devices = msg.get('DEVICES',None)

        if not devices:
            self.msgbus_publish('LOG','%s VHM Request with invalid data arrive: %s'%'WARNING',msg)
        else:
            for k in devices.keys():
                device = self._threadDict.get(k,None)
                if not device:
                    self.msgbus_publish('LOG','%s VHM Requested Device does not exist: %s'%'ERROR',k)
                else:
                    device.on_request(devices.get(k))

        return True


    def config(self,cfg_msg):

        devices = cfg_msg.select('DEVICES')
        print('#####',devices)
        self.msgbus_publish('LOG','%s VHM Configuration Update received %s '%('INFO', devices.getTree()))
        print('getNodes',devices.getNodesKey())

        '''
        compare running devices with configured devices
        '''
        cfg_devices = set(devices.getNodesKey())
        run_devices = set(self._threadDict.keys())

        print('cfg_devices',cfg_devices,'run_devices',run_devices)
        '''
        list devices to be started
        '''
        self.start_vdm(list(cfg_devices.difference(run_devices)))
        '''
        list devices to be stopped
        '''
        self.stop_vdm(list(run_devices.difference(cfg_devices)))
        '''
        devices to be configured
        '''
        self.cfg_vdm(devices)

        return True


    def start_vdm(self,devices):

        print('VHM::start devices',devices)

        for device in devices:
            threadObj = vdm(device,self.on_notify)
            threadObj.start()
            self._threadDict[device]=threadObj

        return True

    def stop_vdm(self,devices):

        print('VHM::stop devices',devices)

        for device in devices:
            threadObj = self._threadList[device]
            threadObj.stop()
            del self._threadList[device]

        return True

    def cfg_vdm(self,devices):
        print('VHM::devices list',devices.getTree())

        self.msgbus_publish('CONFIG_VDM',devices)
        return True

