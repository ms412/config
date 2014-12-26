
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
        self._pinstatesave = 0
        self._T0 = time.time()

        self._update = False

        self._counter = 0

        self.setup()

    def setup(self):
       # self.msgbus_publish('LOG','%s VPM Module BINARY IN Setup Configuration: %s '%('INFO', self._VPM_CFG))    def setup(self):

        print('VPM Mode:', self._mode,'ID', self._VPM_ID)



    def config(self,msg):
        print('Config interface')
        self._off_value = str(msg.getNode('OFF_VALUE','OFF'))
        self._on_value = str(msg.getNode('ON_VALUE','ON'))
        self._interval = int(msg.getNode('INTERVAL',0))
        self._hwid = int(msg.getNode('HWID',None))

        if not self._hwid:
            print('VPM::ERROR no HWID in config')

        '''
        configure port as input port
        '''
        self._hwHandle.ConfigIO(self._hwid,1)


    def run(self):
        test ={}
        self._counter = self._counter+1
        print ('VPN BinIn')
        test['Counter']=self._counter
        test['ID']=self._VPM_ID
        print('Testmessage',test)
      #  self._callback(test)


        '''
        Run Task
        '''


        pinstate = self._hwHandle.ReadPin(self._hwid)

        if pinstate == 0:
            pinstate = self._off_value
        else:
            pinstate = self._on_value

        if self._interval > 0:
            '''
            If interval got definded, send messeg after each completed interval
            '''
            if (self._T0 + self._interval) < time.time():
                self._T0 = time.time()
                self.notify()


        if pinstate != self._pinstatesave:
            self._pinstatesave = pinstate

            '''
            Pin State changed during two runs
            now we have to send notification
            '''
            self.notify()


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
        notify_msg['VALUE'] = self._pinstatesave
        notify_msg['STATE'] = True

        self._callback(notify_msg)

    def request(msg):
        msgtype = msg.get('GET',None)

        self.notify()

    def on_cfg(self,msg):
        print('message',msg)
        portcfg = msg.select(self._VPM_ID)
        self.config(portcfg)

        return True