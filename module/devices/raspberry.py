from library.libbitoperation import bitoperation

import RPIO as GPIO
from RPIO import PWM

'''
Pin     Numbers    RPi.GPIO    Raspberry Pi Name    BCM2835
P1_01    1             3V3
P1_02    2             5V0
P1_03    3             SDA0         GPIO0
P1_04    4             DNC
P1_05    5             SCL0         GPIO1
P1_06    6             GND
P1_07    7             GPIO7        GPIO4
P1_08    8             TXD          GPIO14
P1_09    9             DNC
P1_10    10            RXD          GPIO15
P1_11    11            GPIO0        GPIO17
P1_12    12            GPIO1        GPIO18
P1_13    13            GPIO2        GPIO21
P1_14    14            DNC
P1_15    15            GPIO3        GPIO22
P1_16    16            GPIO4        GPIO23
P1_17    17            DNC
P1_18    18            GPIO5        GPIO24
P1_19    19            SPI_MOSI     GPIO10
P1_20    20            DNC
P1_21    21            SPI_MISO     GPIO9
P1_22    22            GPIO6        GPIO25
P1_23    23            SPI_SCLK     GPIO11
P1_24    24            SPI_CE0_N    GPIO8
P1_25    25            DNC
P1_26    26            SPI_CE1_N    GPIO7
'''

class raspberry(object):

    def __init__(self):
        #define log object
   #     self._loghandle = loghandle()
        self._gpio = GPIO
        self._pwm = PWM.Servo()
        self._pwmState = False
 #       self._gpio.setmode(self._gpio.BOARD)
        self._gpio.setmode(GPIO.BCM)
        self._gpio.setwarnings(False)

        self.Reset()

    def Reset (self):
        self._gpio.cleanup()


    def setup(self, mode, pin):

        return True

    def ConfigIO(self,ioPin,iodir):

        print("ConfigPort  ioPin:",ioPin,"Direction:",iodir)

        if iodir == 1:
           # self._gpio.setup(ioPin, self._gpio.IN)
            self._gpio.setup(ioPin,self._gpio.IN)
        else:
            #self._gpio.setup(ioPin,self._gpio.OUT, initial=self._gpio.HIGH)
            self._gpio.setup(ioPin,self._gpio.OUT)

        return True


    def ConfigPWM(self,ioPin):
         self._loghandle.info('hwIF_raspberry::ConfigPWM Set PWM mode for Port: %s',ioPin)
         self._gpio.setup(ioPin,self._gpio.OUT)

 #        self._pwm.Servo()

         return True

    def WritePWM(self,ioPin,value):
        value = int(value)

       # print "wirtepwm", ioPin, value

        if value <= 3:
            if self._pwmState == True:
        #        print"WritePWM 3, pwmState True"
                self._pwm.stop_servo(ioPin)
                self.ConfigIO(ioPin,0)
                self.WritePin(ioPin,0)
                self._pwmState = False
            else:
                self.WritePin(ioPin,0)

            self._loghandle.info('hwIF_raspberry::WritePWM Stop PWM value: Low for Port: %s',ioPin)
        elif value >= 97:
            if self._pwmState == True:
                #print"WritePWM 97, pwmState True"
                self._pwm.stop_servo(ioPin)
                self.ConfigIO(ioPin,0)
                self.WritePin(ioPin,1)
                self._pwmState = False
            else:
                self.WritePin(ioPin,1)
#             self._pwm.stop_servo(ioPin)
#             self._gpio.output(ioPin, 1)
            #value = 19900
            #self._pwm.set_servo(ioPin,value)
            self._loghandle.info('hwIF_raspberry::WritePWM Stop PWM value: High for Port: %s',ioPin)
        else:
            if self._pwmState == False:
                self.ConfigPWM(ioPin)
                self._pwmState = True
               # print"WritePWM else, pwmState True"

            self._loghandle.info('hwIF_raspberry::WritePWM Set PWM value: %s for Port: %s',value,ioPin)
            value = value*200
            self._pwm.set_servo(ioPin,value)

       # self._pwm.set_servo(ioPin,value)

        return True




    def WritePin(self,ioPin,value):
        self._loghandle.info('hwIF_raspberry::WritePin ioPin %s, value: %s', ioPin, value)
        self._gpio.output(ioPin, value)

        return True


    def ReadPin(self,ioPin):

        value = self._gpio.input(ioPin)
        self._loghandle.info('hwIF_raspberry::ReadPin ioPin %s, value: %s', ioPin, value)

        return value
