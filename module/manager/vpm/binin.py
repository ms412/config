
import json
import time

from library.libmsgbus import msgbus

#from module.manager.vdm import vdm

class binin(msgbus):
    '''
    +++ Function +++
    configures the pin as Input

    +++ Configuration Parameter +++
    VDM_ID {
        OFF_VALUE: <string>
        ON_VALUE: <string>
        INTERVAL: <float>
        HWID: <int>
    }
    OFF_VALUE = contains parameter returned in case port has low potential at it's interface, if not configured in config file = 'OFF'; type string
    ON_VALUE = contains parameter returned in case port has high potential at it's interface, if not configured in config file = 'ON'; type string
    INTERVAL = update interval reports the current state of the pin after a pre-configured time interval, accuracy depending on the concerning VDM update interval on the,
                expected value is integer; default is 0 -> no update interval; type float
    HWID = hardware ID of the pin number at the hardware device; type int

    +++ Request Parameters +++
    VDM_ID {
        TYPE: GET
        COMMAND: GET
    }

    TYPE: indicates a GET message; type string
    COMMAND: REQUEST request a notification of the current port state; type string

    +++ Return Parameters +++
    VPM_ID {
        VALUE: <string>
        MSG: <string>
        STATE: True/False
    }
    VALUE: ad defined in OFF/ON_VALUE; type string
    MSG: in case a detailed message is available it will be delivered in this object; type string
    STATE: either True or False indicates state of the message; type bool
    '''

    def __init__(self,vpmID,hwHandle,callback):
        '''
        Constructor
        portID = unique VPM ID
        hwHandle = hardware_handle
        notifyIF = interface to which the VPM sends notifications towards VDM
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
        #print('kill myself',self._VPM_ID)
        logmsg ='Kill myself'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s Message: %s'%('CRITICAL', self._mode, self._VPM_ID, logmsg))

    def setup(self):
        '''
        configure port as input port
        '''
       # print('VPM Mode:', self._mode,'ID', self._VPM_ID,'hw handle',self._hwHandle)

      #  self._hwHandle.ConfigIO(self._hwid,1)

        logmsg = 'Startup'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s Message: %s'%('INFO', self._mode, self._VPM_ID, logmsg))

        return True

    def config(self,msg):
        '''
        :param msg: contains configuration as a tree object
        :return:
        '''

        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s Message: %s'%('INFO', self._mode, self._VPM_ID, msg))

        cfg = msg.select(self._VPM_ID)
        print('Config interface')
        self._off_value = str(cfg.getNode('OFF_VALUE','OFF'))
        self._on_value = str(cfg.getNode('ON_VALUE','ON'))
        self._interval = int(cfg.getNode('INTERVAL',0.0))
        self._hwid = int(cfg.getNode('HWID',None))

        if not self._hwid:
            logmsg = 'HWID is missing in config'
            self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('ERROR', self._mode, self._VPM_ID, logmsg))
           # print('VPM::ERROR no HWID in config')
        else:
        #    print('VPM:', self._hwid)
            self._hwHandle.ConfigIO(self._hwid,'IN')
        return True

    def run(self):
        '''
        run is getting called on a regular base from VDM, frequency of calls defined by update value in VDM configuration section
        '''
        self._counter = self._counter +1

        '''
        read pin state
        '''
        result = self._hwHandle.ReadPin(self._hwid)
      #  print('Binin',result,self._hwid)

        if result == 0:
            pin_act = self._off_value
        else:
            pin_act = self._on_value

        '''
        if a update interval defined, send notification message after each completed interval
        '''
        if self._interval > 0:
            if (self._T0 + self._interval) < time.time():
              #  print('Timeinterval', self._T0 + self._interval,'Actual',time.time())
                self._T0 = time.time()
                logmsg = ' Timeinterval expired'
                self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('INFO', self._mode, self._VPM_ID, logmsg))
                self.notify()

       # print('PinSave',self._pin_save,'PinAct',pin_act)
        '''
        if Pin State changed notification has to be changed
        '''
        if not self._pin_save in pin_act:
            self._pin_save = pin_act
            logmsg = 'Pin change detected'
            self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('INFO', self._mode, self._VPM_ID, logmsg))
            self.notify()

        return True

    def notify(self,msg=None):
        '''
        in case potential of the pin changed, a notification will be emitted
        :return: dictionary
        PORT_ID = unique port name
        VALUE = current state of Pin
        MSG = message to user (optional)
        STATE = whether value is true or false
        '''

        container = {}
        msg_container = {}

        msg_container['VALUE'] = self._pin_save
        if msg:
            msg_container['MSG'] = msg
        msg_container['STATE'] = 'TRUE'

        container[self._VPM_ID]=msg_container

    #    notify_msg= {}

     #   notify_msg['PORT_ID'] = self._VPM_ID
      #  notify_msg['VALUE'] = self._pin_save
      #  if msg:
       #     notify_msg['MSG'] = msg
       # notify_msg['STATE'] = True
      #  print ('Sent Notification:,',notify_msg)
        logmsg = 'Notification send to VDM'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('INFO', self._mode, self._VPM_ID, logmsg, container))

        self._callback(container)

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
        logmsg = 'Notification received'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('INFO', self._mode, self._VPM_ID, logmsg, msg))

        if 'GET' in msgtype:
            if 'REQUEST' in cmd:
                self.notify()
            else:
                logmsg = 'Command unknown'
                self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('ERROR', self._mode, self._VPM_ID, logmsg, cmd))
          #      print ('Command unknown')
        else:
            logmsg = 'Messagetype unknown'
            self.msgbus_publish('LOG','%s Mode: %s ID: %s; Message: %s , %s'%('ERROR', self._mode, self._VPM_ID, logmsg, msgtype))
            #print('Messagetype unknown')

        return True