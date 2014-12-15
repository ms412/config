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
        self.msgbus_subscribe('NOTIFY', self._on_vdm_notify)
        return True

    def _on_vdm_notify(self,msg):
        print('_VHM data received:',msg)
        self.msgbus_publish('DATA_TX',msg)
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
            threadObj = vdm(device)
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

