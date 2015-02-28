
import json
import time
from queue import Queue

from library.libmsgbus import msgbus
#from module.manager.vdm import vdm

class binout(msgbus):
    '''
    +++ Function +++
    configures the pin as Input

    +++ Configuration Parameter +++
    VDM_ID {
        OFF_VALUE: <string>
        ON_VALUE: <string>
        INITIAL: <string>
        HWID: <int>
    }
    OFF_VALUE = contains parameter returned in case port has low potential at it's interface, if not configured in config file = 'OFF'; type string
    ON_VALUE = contains parameter returned in case port has high potential at it's interface, if not configured in config file = 'ON'; type string
    INITIAL = initial value of the pin polarity after device reset, configuration according OFF/ON_VALUE; type string
    INTERVAL = update interval reports the current state of the pin after a pre-configured time interval, accuracy depending on the concerning VDM update interval on the,
                expected value is integer; default is 0 -> no update interval; type float
    HWID = hardware ID of the pin number at the hardware device; type int

    +++ Request Parameters +++
    VDM_ID {
        TYPE: SET
        COMMAND: <string>
    }

    TYPE: SET indicates that the port pin shall be set; type string
    COMMAND: value must be either OFF or ON_VALUE as defined above; type string

    +++ Return Parameters +++
    VPM_ID {
        VALUE: <string>
        MSG: <string>
        STATE: True/False
    }
    VALUE: current state of the port pin as defined in OFF/ON_VALUE; type string
    MSG: in case a detailed message is available it will be delivered in this object; type string
    STATE: either True or False indicates state of the message; type bool
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
        self._T0 = time.time()

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
        self._off_value = str(cfg.getNode('OFF_VALUE','OFF'))
        self._on_value = str(cfg.getNode('ON_VALUE','ON'))
        self._initial = str(cfg.getNode('INITIAL','self._off_value'))
        self._interval = int(cfg.getNode('INTERVAL',0.0))
        self._hwid = int(cfg.getNode('HWID',None))

        if self._hwid is None:
            logmsg = 'HWID is missing in config'
            self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('ERROR', self._mode, self._VPM_ID, logmsg))
           # print('VPM::ERROR no HWID in config')
        else:
           # print('VPM:', self._hwid)
            self._hwHandle.ConfigIO(self._hwid,'OUT')

        '''
        set initial configuration
        '''
        if self._initial == self._on_value:
            self._hwHandle.WritePin(self._hwid, 1)
            self._pin_save  = self._on_value
        else:
            self._hwHandle.WritePin(self._hwid, 0)
            self._pin_save  =  self._off_value
         #   self.Set(self._initial)

        return True

    def run(self):
        '''
        Run Task
        '''
        self._counter = self._counter +1

        '''
        if a update interval defined, send notification message after each completed interval
        '''
        if self._interval > 0:
            if (self._T0 + self._interval) < time.time():
              #  print('Timeinterval', self._T0 + self._interval,'Actual',time.time())
                self._T0 = time.time()
                logmsg = ' Timeinterval expired'
                self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('INFO', self._mode, self._VPM_ID, logmsg))
                self.notify('UPDATE')


        return True

    def request(self,msg):
        '''
        Port set port polarity; value as defined in ON_VALUE or OFF_VALUE
        '''

        msgtype = msg.get('TYPE',None)
        cmd = msg.get('COMMAND',self._off_value)
        print('Set Request',msg,msgtype,cmd)
        self.msgbus_publish('LOG','%s VPM BinaryOut Port: %s Unknown value'%('ERROR','TESTESTETET'))

        if 'SET' in msgtype:
            if self._on_value in cmd:
                self._hwHandle.WritePin(self._hwid, 1)
                self._pin_save  = self._on_value
            elif self._off_value in cmd:
                self._hwHandle.WritePin(self._hwid, 0)
                self._pin_save  = self._off_value
            else:
                self.msgbus_publish('LOG','%s VPM BinaryOut Port: %s Unknown value'%('ERROR',cmd))
        else:
            print('Messagetype unknown',msgtype)

        self.notify()

        return True

    def notify(self,msg=None):

       # notify_msg= {}

      #  notify_msg['PORT_ID'] = self._VPM_ID
       # notify_msg['VALUE'] = self._pin_save
        #if msg:
         #   notify_msg['MSG'] = msg
        #notify_msg['STATE'] = True

        container = {}
        msg_container = {}

        msg_container['VALUE'] = self._pin_save
        if msg:
            msg_container['MSG'] = msg
        msg_container['STATE'] = 'TRUE'

        container[self._VPM_ID]=msg_container

        logmsg = 'Notification send to VDM'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('INFO', self._mode, self._VPM_ID, logmsg, container))

        self._callback(container)

        return True

