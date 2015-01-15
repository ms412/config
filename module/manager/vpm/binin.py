
import json
import time

from library.libmsgbus import msgbus

#from module.manager.vdm import vdm

class binin(msgbus):
    '''
    Mandatory values
    vpmID contains unique ID of the VPM instance -> Port-Section-Name in Configuration
    hwHandle is the object instance performing operation on the hardware, started by the Virtual Device Manger(VDM)
    each port manager (VPM) started from a VDM Instance has the same hwHandle
    callback contains the notification interface of the concerning VDM instance

    _mode = contains the mode type of the VPM object

    ++ Mandatory Values ++
    _hwid = contains the hardware address of the concerning Pin (from configuration file)

    ++ Optional Values ++
    OFF_VALUE = contains parameter returned in case port has low potential at it's interface, if not configured in config file = 'OFF'
    ON_VALUE = contains parameter returned in case port has high potential at it's interface, if not configured in config file = 'ON'
    INTERVAL = update interval reports the current state of the pin after a pre-configured time interval, accuracy depending on the concerning VDM update interval on the,
                expected value is integer; default is 0 -> no update interval
    '''

    def __init__(self,vpmID,hwHandle,callback):
        '''
        Constructor
        portID = unique IF VPM listens to
        hwHandle = handle for the hardware
        notifyIF = interface to which the VPM sends notifications
        '''

        self._VPM_ID = vpmID
        self._hwHandle = hwHandle
        self._callback = callback

        '''
        System parameter
        '''
        self._mode = 'BINARY-IN'
        self._hwid = 0

        '''
        Class variables
        '''
        self._pin_save = 'Unknown'
        self._T0 = time.time()

       # self._update = False

        '''
        Maintenance Counter
        '''
        self._counter = 0

        self.setup()

    def __del__(self):
        print('kill myself',self._VPM_ID)
        self.msgbus_publish('LOG','%s VPM Module Mode: %s Destroying myself: %s '%('INFO', self._mode, self._VPM_ID))

    def setup(self):
        '''
        configure port as input port
        '''
        print('VPM Mode:', self._mode,'ID', self._VPM_ID,'hw handle',self._hwHandle)

      #  self._hwHandle.ConfigIO(self._hwid,1)

       # self.msgbus_publish('LOG','%s VPM Module BINARY IN Setup Configuration: %s '%('INFO', self._VPM_CFG))    def setup(self):


        return True

    def config(self,msg):
        '''
        :param msg: contains configuration as a tree object
        :return:
        '''
        IN = 1
        OUT = 0
        cfg = msg.select(self._VPM_ID)
        print('Config interface')
        self._off_value = str(cfg.getNode('OFF_VALUE','OFF'))
        self._on_value = str(cfg.getNode('ON_VALUE','ON'))
        self._interval = int(cfg.getNode('INTERVAL',0))
        self._hwid = int(cfg.getNode('HWID',None))

        if not self._hwid:
            print('VPM::ERROR no HWID in config')
        else:
            print('VPM:', self._hwid)
            self._hwHandle.ConfigIO(self._hwid,IN)
        return True

    def run(self):
        '''
        run is getting called on a regular base from VDM, frequency of calls defined by update value in VDM configuration section
        '''
        self._counter = self._counter +1

        result = self._hwHandle.ReadPin(self._hwid)

        if result == 0:
            pin_act = self._off_value
        else:
            pin_act = self._on_value

        if self._interval > 0:
            '''
            If interval got definded, send messeg after each completed interval
            '''
            if (self._T0 + self._interval) < time.time():
                print('Timeinterval', self._T0 + self._interval,'Actual',time.time())
                self._T0 = time.time()
                self.notify()

        print('PinSave',self._pin_save,'PinAct',pin_act)
        if not self._pin_save in pin_act:
            self._pin_save = pin_act
            print ('Mo0dification detected')

            '''
            Pin State changed during two runs
            now we have to send notification
            '''
            self.notify()

        return True

    def notify(self):
        '''
        in case potential of the pin changed, a notification will be emitted
        :return: dictionary
        PORT_ID = unique port name
        VALUE = current state of Pin
        STATE = whether value is true or false
        '''

        notify_msg= {}

        notify_msg['PORT_ID'] = self._VPM_ID
        notify_msg['VALUE'] = self._pin_save
        notify_msg['STATE'] = True
        print ('Sent Notification:,',notify_msg)
        self._callback(notify_msg)

        return True

    def request(self,msg):
        '''
        request interface
        :param msg: dictionary anny value expected; will call notify interface to send an update of the current pin state
        :return:
        '''

        msgtype = msg.get('TYPE',None)
        cmd = msg.get('COMMAND',None)
        print('Get Notification',msg,msgtype)

        if 'GET' in msgtype:
            if 'GET' in cmd:
                self.notify()
            else:
                print ('Command unknown')
        else:
            print('Messagetype unknown')

        return True