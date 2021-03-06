
import json
import time

from library.libmsgbus import msgbus

#from module.manager.vdm import vdm

class trigger(msgbus):
    '''
    Function
    in case of a request port changes polarity for a pre-configure time and switch back after timer is expired

    Configuration Options
    HWID: hw address of the I/O pin
    INITIAL: inital value of the pin (ON/OFF)
    TIMER: float value in seconds how long the interface will change the polarity

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
        self._mode = 'TRIGGER'
        self._hwid = 0

        '''
        Define class variables
        '''
        self._pin_save = 'Unknown'
        self._T0 = time.time()
        self._T1 = 0.0
        self._trigger_act = False


       # self._update = False

        '''
        Maintenance Counter
        '''
        self._counter = 0

        self.setup()

    def __del__(self):
        logmsg ='Kill myself'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s Message: %s'%('CRITICAL', self._mode, self._VPM_ID, logmsg))
      #  print('kill myself',self._VPM_ID)
       # self.msgbus_publish('LOG','%s VPM Mode: %s Destroying myself: %s '%('CRITICAL', self._mode, self._VPM_ID))

    def setup(self):
        '''
        configure port as input port
        '''

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
        self._timer = float(cfg.getNode('TIMER',10))
        self._initial = str(cfg.getNode('INITIAL',None))
        self._interval = int(cfg.getNode('INTERVAL',0.0))
        self._hwid = int(cfg.getNode('HWID',None))

        if self._hwid is None:
            logmsg = 'HWID is missing in config'
            self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('ERROR', self._mode, self._VPM_ID, logmsg))
           # print('VPM::ERROR no HWID in config')
        else:
        #    print('VPM:', self._hwid)
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

        return True

    def run(self):
        '''
        run is getting called on a regular base from VDM, frequency of calls defined by update value in VDM configuration section
        '''
        self._counter = self._counter +1


        '''
        Pin can be reseated to initial value if T1 is exceeded
        '''

        if self._trigger_act == True:

            if self._T1 < time.time():
                self.notify('Trigger executed')
                self._trigger_act = False
                '''
                reset initial configuration
                '''
                if self._initial == self._on_value:
                    self._hwHandle.WritePin(self._hwid, 1)
                    self._pin_save  = self._on_value
                    self.notify()
                else:
                    self._hwHandle.WritePin(self._hwid, 0)
                    self._pin_save  =  self._off_value
                    self.notify()

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

    def notify(self,msg=None):
        '''
        in case potential of the pin changed, a notification will be emitted
        :return: dictionary
        PORT_ID = unique port name
        MSG = message to user (optional)
        STATE = whether value is true or false
        '''

        '''
        Read current pin state
        '''
        result = self._hwHandle.ReadPin(self._hwid)
        if result == 0:
            pin_act = self._off_value
        else:
            pin_act = self._on_value

       # notify_msg= {}

        #notify_msg['PORT_ID'] = self._VPM_ID
       # notify_msg['VALUE'] = pin_act
        #if msg:
         #   notify_msg['MSG'] = msg
        #notify_msg['STATE'] = 'TRUE'




        container = {}
        msg_container = {}

        msg_container['VALUE'] = self._pin_save
        if msg:
            msg_container['MSG'] = msg
        msg_container['STATE'] = 'TRUE'

        container[self._VPM_ID]=msg_container

        logmsg = 'Notification send to VDM'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('INFO', self._mode, self._VPM_ID, logmsg, container))


      #  print ('Sent Notification:,',notify_msg)
       # logmsg = 'Notification send to VDM'
        #self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('INFO', self._mode, self._VPM_ID, logmsg, notify_msg))

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
        temp_timer = float(msg.get('TIMER',-1))
      #  print('Get Notification',msg,msgtype)
        logmsg = 'Notification received'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('INFO', self._mode, self._VPM_ID, logmsg, msg))

        if 'SET' in msgtype:
            if self._on_value in cmd:
                self._trigger_act = True
                self._hwHandle.WritePin(self._hwid, 1)
                self._pin_save  = self._on_value
                if temp_timer < 1:
                    self._T1 = time.time() + self._timer
                else:
                    self._T1 = time.time() + temp_timer
            elif self._off_value in cmd:
                self._trigger_act = True
                self._hwHandle.WritePin(self._hwid, 0)
                self._pin_save  = self._off_value
                if temp_timer < 1:
                    self._T1 = time.time() + self._timer
                else:
                    self._T1 = time.time() + temp_timer
            else:
                logmsg = 'Command unknown'
                self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('ERROR', self._mode, self._VPM_ID, logmsg, cmd))
          #      print ('Command unknown')
        else:
            logmsg = 'Messagetype unknown'
            self.msgbus_publish('LOG','%s Mode: %s ID: %s; Message: %s , %s'%('ERROR', self._mode, self._VPM_ID, logmsg, msgtype))
            #print('Messagetype unknown')

        return True