
import json
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
    HWID = hardware ID of the pin number of the hardware device; type int

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
        self._INITIAL = str(cfg.getNode('INITIAL','self._OFF_VALUE'))
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
        msg_container['STATE'] = True

        container[self._VPM_ID]=msg_container

        logmsg = 'Notification send to VDM'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('INFO', self._mode, self._VPM_ID, logmsg, container))

        self._callback(container)

        return True

