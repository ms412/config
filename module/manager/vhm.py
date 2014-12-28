import time
from queue import Queue

from library.libmsgbus import msgbus
from module.manager.vdm import vdm


class vhm(msgbus):
    '''
    VHM is started only once and manges all lower VDM threads

    Channels Subscribe:
    CONFIG channel receives configuration messages from configuration adapter, calls method "on_config"
    REQUEST channel receives request messages via messagebroker from mqtt broker, calls method "on_request"

    Channels Publish:
    CONFIG_VDM sends configuration messages to all VDM threads
    NOTIFY sends messages to the messagebroker to send messages to the mqtt broker
    LOG sends log messages to the logging interface
    '''

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
        '''
        subscribe to channels
        '''
        self.msgbus_subscribe('CONFIG', self.on_config)
        self.msgbus_subscribe('REQUEST', self.on_request)
        return True

    def on_notify(self,msg):
        '''
        callback method used be VDMs to send notifications to VHM
        Method adds DEVICES haeder to the message and publish it to message broker DATA_TX channel
        :param msg: message as dictionary from VDM
        :return: True
        '''
        print('VHM data received:',msg)
        add_header = {}
        add_header['DEVICES'] = msg
        self.msgbus_publish('DATA_TX',add_header)
        return True

    def on_request(self,msg):
        '''
        method receives notifications from message broker
        selects DEVICES Section from message and forwards the message to the concerning device
        :param msg: message as dictionary from Message broker
        :return: True
        '''

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


    def on_config(self,cfg_msg):
        '''
        message sink for configuration messages
        Selects section DEVICES in configfile

        :param cfg_msg: expects configuration message as tree type
        :return:
        '''
        '''

        '''

        dev_cfg = cfg_msg.select('DEVICES')
        print('#####',devices)
        self.msgbus_publish('LOG','%s VHM Configuration Update received %s '%('INFO', dev_cfg.getTree()))
        print('getNodes',dev_cfg.getNodesKey())

        '''
        compare running devices with configured devices

        configuration message must be either
        - forwarded to the VDM if the VDM is already exist
        - VDM deleted if it exist in the _threadDict as running thread
        - or created in case VDM does not exist but in configuration message
        '''

        new_devices = set(dev_cfg.getNodesKey())
        run_devices = set(self._threadDict.keys())

        print('new_devices',new_devices,'run_devices',run_devices)
        '''
        list devices to be started
        '''
        self.start_vdm(list(new_devices.difference(run_devices)))
        '''
        list devices to be stopped
        '''
        self.stop_vdm(list(run_devices.difference(new_devices)))
        '''
        devices to be configured
        '''
        self.cfg_vdm(dev_cfg)

        return True


    def start_vdm(self,devices):
        '''
        Starts VDM object
        :param devices: list of devices to be started
        :return: True
        '''

        print('VHM::start devices',devices)

        for device in devices:
            '''
            hands over device name and callback interface for notifications
            and starts thread
            '''
            threadObj = vdm(device,self.on_notify)
            threadObj.start()
            '''
            save object in threadDictionary with device name as key
            '''
            self._threadDict[device]=threadObj

        return True

    def stop_vdm(self,devices):
        '''
        Stop VDM object
        :param devices: list of devices to be stopped
        :return: True
        '''

        print('VHM::stop devices',devices)

        for device in devices:
            '''
            stops each device in device list and stops each VDM device listed
            '''
            threadObj = self._threadList[device]
            threadObj.stop()
            '''
            deletes device from threadDictionary
            '''
            del self._threadList[device]

        return True

    def cfg_vdm(self,dev_cfg):
        '''
        :param dev_cfg: contains the configuration of the devices in a tree object
        :return: True
        sends configuration to all devices listening to the CONFIG_VDM channel
        '''
        print('VHM::devices list',dev_cfg.getTree())

        self.msgbus_publish('CONFIG_VDM',dev_cfg)
        return True

