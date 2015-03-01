
import json
import time
from library.libmsgbus import msgbus

#from module.manager.vdm import vdm

# Commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80
# Entry flags
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00
# Control flags
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00
# Move flags
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00
# Function set flags
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00
# Offset for up to 4 rows.
LCD_ROW_OFFSETS = (0x00, 0x40, 0x14, 0x54)
# Char LCD plate GPIO numbers.
LCD_PLATE_RS = 15
LCD_PLATE_RW = 14
LCD_PLATE_EN = 13
LCD_PLATE_D4 = 12
LCD_PLATE_D5 = 11
LCD_PLATE_D6 = 10
LCD_PLATE_D7 = 9
LCD_PLATE_RED = 6
LCD_PLATE_GREEN = 7
LCD_PLATE_BLUE = 8
# Char LCD plate button names.
SELECT = 0
RIGHT = 1
DOWN = 2
UP = 3
LEFT = 4


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
    PIN_RS = hardware ID of the RS-Pin number at the hardware device; type int
    PIN_E  = hardware ID of the Enable-Pin number at the hardware device; type int
    PIN_D  = hardware ID of the Data-Pin 1-4 number at the hardware device; type int array

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

        self._pin_rs = int(cfg.getNode('PIN_RS',-1))
        self._pin_rw = int(cfg.getNode('PIN_RW',-1))
        self._pin_e = int(cfg.getNode('PIN_E',-1))
        self._pin_d = list(cfg.getNode('PIN_D',-1))
       # test = map(int,self._pin_d)
        self._pin_d = [int(i) for i in self._pin_d]

        print('LCD Config interface',self._pin_rs, self._pin_e, self._pin_rw, self._pin_d)

        #if not self._pin_rs or not self._pin_e or not self._pin_rw:
        if self._pin_rs < 0:
            print ('LCD PIN RS Missing')
            logmsg = 'Register Select Pin configuration missing'
            self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('ERROR', self._mode, self._VPM_ID, logmsg))
        #    print('VPM::ERROR no HWID in config')
        elif self._pin_rw < 0:
            print('LCD Pin RW missing')
            logmsg = 'Read/Write Pin configuration missing'
            self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('ERROR', self._mode, self._VPM_ID, logmsg))
        elif self._pin_e < 0:
            print ('LCD Pin E missing')
            logmsg = 'Enable Pin configuration missing'
            self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('ERROR', self._mode, self._VPM_ID, logmsg))
        elif len(self._pin_d) < 4:
            print ('LCD Pin D missing')
            logmsg = 'DATA Pin configuration not complete'
            self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('ERROR', self._mode, self._VPM_ID, logmsg))
        else:
        #    print('VPM:', self._hwid)
            print('LCD set at output')
            self._hwHandle.ConfigIO(self._pin_rs,'OUT')
            self._hwHandle.ConfigIO(self._pin_e,'OUT')
            self._hwHandle.WritePin(self._pin_e,0)
            self._hwHandle.ConfigIO(self._pin_rw,'OUT')
            self._hwHandle.WritePin(self._pin_rw,0)

            for pin in self._pin_d:
                print('LCD pin id',pin)
                self._hwHandle.ConfigIO(pin,'OUT')
                self._hwHandle.WritePin(pin,0)

            time.sleep(1)

            self._lcd_reset()
            time.sleep(3)
            self._lcd_message('TEST \n 123')

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

      #  time.sleep(0.001)
        bits=bin(bits)[2:].zfill(8)

        self._hwHandle.WritePin(self._pin_rs, char_mode)
       # time.sleep(0.001)
       # GPIO.output(self.pin_rs, char_mode)

        #for pin in self._pin_d:
       #     self._hwHandle.WritePin(pin,0)
        print ('Write 1-4')
        for i in range(4):
            print ('Int',i,bits,bits[i],self._pin_d,self._pin_d[::-1][i])
            if bits[i] == "1":
                self._hwHandle.WritePin(self._pin_d[::-1][i],1)
            else:
                self._hwHandle.WritePin(self._pin_d[::-1][i],0)
           #     print ('Write 1-4', self._pin_d, bits, bits[i])


        self._pulse_enable()
       # self._hwHandle.WritePin(self._pin_e,1)
       # self._hwHandle.WritePin(self._pin_e,0)
      #  GPIO.output(self.pin_e, True)
       # GPIO.output(self.pin_e, False)

       # for pin in self._pin_d:
        #    self._hwHandle.WritePin(pin,0)
        print ('Write 5-8')
        for i in range(4,8):
            print ('Int',i,bits,bits[i],self._pin_d,self._pin_d[::-1][i-4])
            if bits[i] == "1":
                self._hwHandle.WritePin(self._pin_d[::-1][i-4],1)
            else:
                self._hwHandle.WritePin(self._pin_d[::-1][i-4],0)
           #     print ('Write 5-8', self._pin_d, bits, bits[i])
              #  GPIO.output(self.pins_db[::-1][i-4], True)

        self._pulse_enable()

       # for pin in self._pin_d:
        #    self._hwHandle.WritePin(pin,0)

   #     self._hwHandle.WritePin(self._pin_e,1)
    #    self._hwHandle.WritePin(self._pin_e,0)

    #@    GPIO.output(self.pin_e, True)
     #   GPIO.output(self.pin_e, False)

    def _lcd_reset(self):
        """ Blank / Reset LCD """

        self._lcd_cmd(0x33) # $33 8-bit mode
        self._lcd_cmd(0x32) # $32 8-bit mode
        self._lcd_cmd(0x28) # $28 8-bit mode
        self._lcd_cmd(0x0C) # $0C 8-bit mode
        self._lcd_cmd(0x06) # $06 8-bit mode

        # Write registers.
        #self._lcd_cmd(LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF)
        #self._lcd_cmd(LCD_4BITMODE | LCD_1LINE | LCD_2LINE | LCD_5x8DOTS)
        #self._lcd_cmd(LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT)
       # print('DISPLAY',LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF)
       # print('DISPLAY',LCD_4BITMODE | LCD_1LINE | LCD_2LINE | LCD_5x8DOTS)
        #print('DISPLAY',LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT)

        self._lcd_clear()

        return True

    def _lcd_clear(self):
        self._lcd_cmd(LCD_CLEARDISPLAY)# $01 8-bit mode
        time.sleep(0.001)

        return True

    def _lcd_message(self, text):
        """ Send string to LCD. Newline wraps to second line"""

        for char in text:
            if char == '\n':
                self._lcd_cmd(0xC0) # next line
            else:
                self._lcd_cmd(ord(char),True)

        return True

    def _pulse_enable(self):
        print('LCD Pulse Enable')
        time.sleep(0.001)
        self._hwHandle.WritePin(self._pin_e,0)
        time.sleep(0.003)
        self._hwHandle.WritePin(self._pin_e,1)
        time.sleep(0.001)
        self._hwHandle.WritePin(self._pin_e,0)
        #time.sleep(0.001)

        return True


