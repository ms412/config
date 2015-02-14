
import json
import time

from library.libmsgbus import msgbus

#from module.manager.vdm import vdm

class pulsee(msgbus):
    '''
    Function
    switch on/off the I/O port for a pre configured period. The ON/OFF period can be pre configured.

    Configuration Options
    HWID
    PULSE_OFF
    PULSE_ON
    MODE: PULSE

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
        self._T0 = 0.0
        self._T1 = 0.0
        self._T2 = 0.0
        self._pulsee_state = 'STOP'
        self._flash_act = False


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
        #print('Config interface')
        #self._off_value = str(cfg.getNode('OFF_VALUE','OFF'))
        #self._on_value = str(cfg.getNode('ON_VALUE','ON'))
        self._pulse_on = float(cfg.getNode('PULSE_ON',10))
        self._pulse_off = float(cfg.getNode('PULSE_OFF',self._pulse_on))
        self._notify = str(cfg.getNode('NOTIFY','OFF'))
        self._hwid = int(cfg.getNode('HWID',None))

        if not self._hwid:
            logmsg = 'HWID is missing in config'
            self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('ERROR', self._mode, self._VPM_ID, logmsg))
           # print('VPM::ERROR no HWID in config')
        else:
        #    print('VPM:', self._hwid)
            self._hwHandle.ConfigIO(self._hwid,'OUT')

        return True

    def run(self):
        '''
        run is getting called on a regular base from VDM, frequency of calls defined by update value in VDM configuration section
        '''
        self._counter = self._counter +1


        '''
        Pin can be reseated to initial value if T1 is exceeded
        '''


        if 'T1' in self._pulse_state:
            if self._T1 < time.time():
                print('T1 expired')
                self._T2 = time.time() + self._pulse_off
                self._hwHandle.WritePin(self._hwid, 0)
                self._pulse_state = 'T2'
                if 'ON' in self._notify:
                    self.notify('OFF')

        elif 'T2' in self._pulse_state:
            if self._T2 < time.time():
                print('T2 expired')
                self._T1 = time.time() + self._pulse_on
                self._hwHandle.WritePin(self._hwid, 1)
                self._pulse_state = 'T1'
                if 'ON' in self._notify:
                    self.notify('ON')

        elif 'T0' in self._pulse_state:
             print('T0')
             self._T1= time.time()+ self._pulse_on
             self._hwHandle.WritePin(self._hwid, 1)
             self._pulse_state = 'T1'

        elif 'STOP' in self._puls_state:
             print ('STOP')
             self._hwHandle.WritePin(self._hwid,0 )
             self._T1 = 0
             self._T2 = 0

        else:
             self._T0 = 0
             self._hwHandle.WritePin(self._hwid,0 )
             self._pulse_state = 'STOP'
                

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

        notify_msg= {}

        notify_msg['PORT_ID'] = self._VPM_ID
        #notify_msg['VALUE'] = pin_act
        if msg:
            notify_msg['MSG'] = msg
        notify_msg['STATE'] = True

      #  print ('Sent Notification:,',notify_msg)
        logmsg = 'Notification send to VDM'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('INFO', self._mode, self._VPM_ID, logmsg, notify_msg))

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
        self._pulse_on('PULSE_ON',self._pulse_on)
        self._pulse_off('PULSE_OFF',self._pulse_off)

        logmsg = 'Notification received'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('INFO', self._mode, self._VPM_ID, logmsg, msg))

        if 'SET' in msgtype:
            if 'START' in cmd:
                self._pulse_state = 'T0'


            elif 'STOP' in cmd:
                self._pulse_state = 'STOP'

            else:
                logmsg = 'Command unknown'
                self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('ERROR', self._mode, self._VPM_ID, logmsg, cmd))
          #      print ('Command unknown')
        else:
            logmsg = 'Messagetype unknown'
            self.msgbus_publish('LOG','%s Mode: %s ID: %s; Message: %s , %s'%('ERROR', self._mode, self._VPM_ID, logmsg, msgtype))
            #print('Messagetype unknown')

        return True