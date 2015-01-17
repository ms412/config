
import json
from queue import Queue

from library.libmsgbus import msgbus
#from module.manager.vdm import vdm

class binout(msgbus):
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
    INITIAL = contains the port value during the startup, default value parameter as defined in the OFF_VALUE parameter
    '''

    def __init__(self,ID,hwHandle,callback):
        '''
        Constructor
        ID = unique Port ID VPM listens to
        hwHandle = handle for the hardware
        notifyIF = interface to which the VPM sends notifications
        '''

        self._VPM_ID = ID
        self._hwHandle = hwHandle
        self._callback = callback

        '''
        System parameter
        '''
        self._mode = 'BINARY-OUT'
        self._hwid = 0

        '''
        Class variables
        '''
        self._pin_save = 'Unknown'
        self._update = False

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
        this method is called from init
        add mandatory functions during setup the object
        '''

        '''
        configure port as output
        '''
    #    self._hwHandle.ConfigIO(self._hwid,0)

        self.msgbus_publish('LOG','%s VPM Module Mode: %s Created with vpmID: %s '%('DEBUG', self._mode, self._VPM_ID))

        return True

    def config(self,msg):
        '''
        Configuration interface
        msg =  data type tree
        '''
      #  result = False
       # IN = 1
        #OUT = 0

        cfg = msg.select(self._VPM_ID)

        '''
        mandatory values
        '''
        try:
            self._hwid = int(cfg.getNode('HWID'))
        except:
            self.msgbus_publish(self._log,'%s VPM Port: %s Mandatory Parameter missing'%('ERROR',self._ID))

        '''
        optional configuration Items
        '''
        self._OFF_VALUE = str(cfg.getNode('OFF_VALUE','OFF'))
        self._ON_VALUE = str(cfg.getNode('ON_VALUE','ON'))
        self._INITIAL = str(cfg.getNode('INITIAL',None))
        self._hwid = int(cfg.getNode('HWID',None))

        if not self._hwid:
            print('VPM::ERROR no HWID in config')
        else:
           # print('VPM:', self._hwid)
            self._hwHandle.ConfigIO(self._hwid,'OUT')

        '''
        set initial configuration
        '''
        if self._INITIAL == self._ON_VALUE:
            self._hwHandle.WritePin(self._hwid, 1)
            self._pin_save  = self._ON_VALUE
        else:
            self._hwHandle.WritePin(self._hwid, 0)
            self._pin_save  =  self._OFF_VALUE
         #   self.Set(self._INITIAL)

        return True

    def run(self):
        '''
        Run Task
        '''
        self._counter = self._counter +1


        return True

    def request(self,msg):
        '''
        Port set port polarity; value as defined in ON_VALUE or OFF_VALUE
        '''

        msgtype = msg.get('TYPE',None)
        cmd = msg.get('COMMAND',self._OFF_VALUE)
        print('Set Request',msg,msgtype,cmd)

        if 'SET' in msgtype:
            if self._ON_VALUE in cmd:
                self._hwHandle.WritePin(self._hwid, 1)
                self._pin_save  = self._ON_VALUE
            elif self._OFF_VALUE in cmd:
                self._hwHandle.WritePin(self._hwid, 0)
                self._pin_save  = self._OFF_VALUE
            else:
                self.msgbus_publish('LOG','%s VPM BinaryOut Port: %s Unknown value'%('ERROR',cmd))
        else:
            print('Messagetype unknown',msgtype)

        self.notify()

        return True

    def notify(self,msg=None):

        notify_msg= {}

        notify_msg['PORT_ID'] = self._VPM_ID
        notify_msg['VALUE'] = self._pin_save
        if msg:
            notify_msg['MSG'] = msg
        notify_msg['STATE'] = True

        self._callback(notify_msg)

        return True

