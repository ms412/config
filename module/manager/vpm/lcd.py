
import json
import time

from library.libmsgbus import msgbus

#from module.manager.vdm import vdm

class lcd(msgbus):
    '''
    +++ Function +++
    configures the pin as Input

    +++ Configuration Parameter +++
    VDM_ID {
        PIN_RS: <int>
        PIN_E: <int>
        PIN_D: <int_array>
    }
    PIN_RS = hardware ID of the RS-Pin number of the hardware device; type int
    PIN_E  = hardware ID of the Enable-Pin number of the hardware device; type int
    PIN_D  = hardware ID of the Data-Pin 1-4 number of the hardware device; type int array

    +++ Request Parameters +++
    VDM_ID {
        TYPE: SET
        COMMAND: RESET/MESSAGE
        MESSAGE: <string>
    }

    TYPE: indicates a SET message; type string
    COMMAND: RESET resets LCD;
             MESSAGE indicates that a message has to be displayed at the LCD; type string
    MESSAGE: contains the message to be displayed; type string

    +++ Return Parameters +++
    None
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
        self._mode = 'LCD'
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
        self._pin_rs = int(cfg.getNode('PIN_RS',None))
        self._pin_e = int(cfg.getNode('PIN_E',None))
        self._pin_d = list(cfg.getNode('PIN_D',None))

        if not self._pin_rs | self._pin_e | self._pin_d:
            logmsg = 'Either of the mandatory Port Pin configuration is missing'
            self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('ERROR', self._mode, self._VPM_ID, logmsg))
           # print('VPM::ERROR no HWID in config')
        else:
        #    print('VPM:', self._hwid)
            self._hwHandle.ConfigIO(self._pin_rs,'OUT')
            self._hwHandle.ConfigIO(self._pin_r,'OUT')
            for pin in self._pin_d:
                self._hwHandle.ConfigIO(pin,'OUT')

            self._lcd_reset()

        return True

    def run(self):
        '''
        run is getting called on a regular base from VDM, frequency of calls defined by update value in VDM configuration section
        '''
        self._counter = self._counter +1

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

        if 'SET' in msgtype:
            if 'MESSAGE' in cmd:
                msg = msg.get('MESSAGE',None)
                if not msg:
                    logmsg = 'Message Empty'
                    self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('ERROR', self._mode, self._VPM_ID, logmsg))
                else:
                    self._lcd_message(msg)

            elif 'RESET' in cmd:
                self._lcd_reset()
            else:
                logmsg = 'Command unknown'
                self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('ERROR', self._mode, self._VPM_ID, logmsg, cmd))
          #      print ('Command unknown')
        else:
            logmsg = 'Messagetype unknown'
            self.msgbus_publish('LOG','%s Mode: %s ID: %s; Message: %s , %s'%('ERROR', self._mode, self._VPM_ID, logmsg, msgtype))
            #print('Messagetype unknown')

        return True

    def _lcd_cmd(self, bits, char_mode=False):
        """ Send command to LCD """

        sleep(0.001)
        bits=bin(bits)[2:].zfill(8)

        self._hwHandle.WritePin(self._pin_rs, char_mode)

       # GPIO.output(self.pin_rs, char_mode)

        for pin in self._pin_d:
            self._hwHandle.WritePin(pin,'0')

        for i in range(4):
            if bits[i] == "1":
                self._hwHandle.WritePin(self._pin_d[::-1][i],'1')

        self._hwHandle.WritePin(self._pin_e,'1')
        self._hwHandle.WritePin(self._pin_e,'0')
      #  GPIO.output(self.pin_e, True)
       # GPIO.output(self.pin_e, False)

        for pin in self._pins_d:
            self._hwHandle.WritePin(pin,'0')

        for i in range(4,8):
            if bits[i] == "1":
                self._hwHandle.WritePin(self._pin_d[::-1][i-4],'1')
              #  GPIO.output(self.pins_db[::-1][i-4], True)

        self._hwHandle.WritePin(self._pin_e,'1')
        self._hwHandle.WritePin(self._pin_e,'0')

    #@    GPIO.output(self.pin_e, True)
     #   GPIO.output(self.pin_e, False)

    def _lcd_reset(self):
        """ Blank / Reset LCD """

        self.cmd(0x33) # $33 8-bit mode
        self.cmd(0x32) # $32 8-bit mode
        self.cmd(0x28) # $28 8-bit mode
        self.cmd(0x0C) # $0C 8-bit mode
        self.cmd(0x06) # $06 8-bit mode
        self.cmd(0x01) # $01 8-bit mode

    def _lcd_message(self, text):
        """ Send string to LCD. Newline wraps to second line"""

        for char in text:
            if char == '\n':
                self.cmd(0xC0) # next line
            else:
                self.cmd(ord(char),True)

