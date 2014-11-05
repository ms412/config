'''
Created on Feb 16, 2014

@author: tgdscm41
'''
from module.hardware.i2cAdapter import i2c
#from library.general.logAdapter import loghandle
from module.general.bitoperation import bitoperation


class MCP23017(object):

    def __init__(self,RaspberryRev = 1,i2cAddr = 0x20):

        self._loghandle = loghandle()

  #      self._loghandle.info('mcp23017Driver::init, Object created: Version: %s, Date: %s',__VERSION__,__DATE__)
        self._loghandle.debug('Start MCP23017 Driver Raspberry Rev. %s, i2c Address: %s', RaspberryRev,i2cAddr)

        self._i2cAdd = i2cAddr
        #Create i2c Object
        self._i2c = i2c(RaspberryRev)
        #Create Bit manipulation object
        self._bit = bitoperation()

        # define device register address
        self._IODIRA =      0x00
        self._IODIRB =      0x01
        self._IOPOLA =      0x02
        self._IOPOLB =      0x03
        self._GPINTENA =    0x04
        self._GPINTENB =    0x05
        self._DEFVALA =     0x06
        self._DEFVALB =     0x07
        self._INTCONA =     0x08
        self._INTCONB =     0x09
        self._IOCONA =      0x0A
        self._IOCONB =      0x0B
        self._GPPUA =       0x0C
        self._GPPUB =       0x0D
        self._INTFA =       0x0E
        self._INTFB =       0x0F
        self._INTCAPA =     0x10
        self._INTCAPB =     0x11
        self._GPIOA =       0x12
        self._GPIOB =       0x13
        self._OLATA =       0x14
        self._OLATB =       0x15

        #rest device to its default values
        self.Reset()

    def Reset (self):
        """ Setup device register to default values
        """
        self._loghandle.debug('mcp23017Driver::Reset, prepare initial setup of device')

        print("reset")
        self._i2c.Write(self._i2cAdd,self._IODIRA,0xFF)
        self._i2c.Write(self._i2cAdd,self._IOPOLA,0x00)
        self._i2c.Write(self._i2cAdd,self._GPINTENA,0x00)
        self._i2c.Write(self._i2cAdd,self._DEFVALA,0x00)
        self._i2c.Write(self._i2cAdd,self._INTCONA,0x00)
        self._i2c.Write(self._i2cAdd,self._GPPUA,0x00)
        #self.Write_i2c(self._GPIOA,0x00)

        self._i2c.Write(self._i2cAdd,self._IODIRB,0xFF)
        self._i2c.Write(self._i2cAdd,self._IOPOLB,0x00)
        self._i2c.Write(self._i2cAdd,self._GPINTENB,0x00)
        self._i2c.Write(self._i2cAdd,self._DEFVALB,0x00)
        self._i2c.Write(self._i2cAdd,self._INTCONB,0x00)
        self._i2c.Write(self._i2cAdd,self._IOCONB,0x00)
        self._i2c.Write(self._i2cAdd,self._GPPUB,0x00)

        return True

    def ConfigIO(self,ioPin,iodir):
        """ Setup ioPin configuration
            ioPin = pin 0...15 as integer
            iodir = 0 output / 1 input
        """
        self._loghandle.debug('mcp23017Driver::ConfigIO, ioPin-number: %d Direction: %s",ioPin,iodir')

        if ioPin <= 7:
            temp = self._i2c.Read(self._i2cAdd,self._IODIRA)

            if iodir == 1:
                temp = self._bit.setBit(temp,ioPin)
            else:
                temp = self._bit.clearBit(temp,ioPin)

            self._i2c.Write(self._i2cAdd,self._GPPUA,temp)
            self._i2c.Write(self._i2cAdd,self._IODIRA,temp)

        else:
            ioPin = ioPin -8
            temp = self._i2c.Read(self._i2cAdd,self._IODIRB)
            if iodir == 1:
                temp = self._bit.setBit(temp,ioPin)
            else:
                temp = self._bit.clearBit(temp,ioPin)

            self._i2c.Write(self._i2cAdd,self._GPPUB,temp)
            self._i2c.Write(self._i2cAdd,self._IODIRB,temp)

        return True

    def WritePin(self,ioPin,value):

        if ioPin <= 7:
            temp = self._i2c.Read(self._i2cAdd,self._GPIOA)
            if value == 1:
                temp = self._bit.setBit(temp,ioPin)
            else:
                temp = self._bit.clearBit(temp,ioPin)

            self._i2c.Write(self._i2cAdd,self._GPIOA, temp)

        else:
            ioPin = ioPin -8
            temp = self._i2c.Read(self._i2cAdd,self._GPIOB)
            if value == 1:
                temp = self._bit.setBit(temp,ioPin)
            else:
                temp = self._bit.clearBit(temp,ioPin)

            self._i2c.Write(self._i2cAdd,self._GPIOB,temp)

        return True

    def ReadPin(self,ioPin):

        if ioPin <= 7:
            temp = self._i2c.Read(self._i2cAdd,self._GPIOA)
         #   print "Debug Read:", hex(temp)
            temp = self._bit.testBit(temp, ioPin)
        else:
            ioPin = ioPin -8
            temp = self._i2c.Read(self._i2cAdd,self._GPIOB)
          #  print "Debug Read:", hex(temp)
            temp = self._bit.testBit(temp, ioPin)

        return temp

    def DebugReg(self):
        print("IODIRA: ",hex(self._i2c.Read(self._i2cAdd,self._IODIRA)))
        print("IODIRB: ",hex(self._i2c.Read(self._i2cAdd,self._IODIRB)))
        print("IOPOLA: ",hex(self._i2c.Read(self._i2cAdd,self._IOPOLA)))
        print("IOPOLB: ",hex(self._i2c.Read(self._i2cAdd,self._IOPOLB)))
        print("GPINTENA: ",hex(self._i2c.Read(self._i2cAdd,self._GPINTENA)))
        print("GPINTENB: ",hex(self._i2c.Read(self._i2cAdd,self._GPINTENB)))
        print("DEFVALA: ",hex(self._i2c.Read(self._i2cAdd,self._DEFVALA)))
        print("DEFVALB: ",hex(self._i2c.Read(self._i2cAdd,self._DEFVALB)))
        print("INTCONA: ",hex(self._i2c.Read(self._i2cAdd,self._INTCONA)))
        print("INTCONB: ",hex(self._i2c.Read(self._i2cAdd,self._INTCONB)))
        print("IOCONA: ",hex(self._i2c.Read(self._i2cAdd,self._IOCONA)))
        print("IOCONB: ",hex(self._i2c.Read(self._i2cAdd,self._IOCONB)))
        print("GPPUA: ",hex(self._i2c.Read(self._i2cAdd,self._GPPUA)))
        print("GPPUB: ",hex(self._i2c.Read(self._i2cAdd,self._GPPUB)))
        print("INTFA: ",hex(self._i2c.Read(self._i2cAdd,self._INTFA)))
        print("INTFB: ",hex(self._i2c.Read(self._i2cAdd,self._INTFB)))
        print("INTCAPA: ",hex(self._i2c.Read(self._i2cAdd,self._INTCAPA)))
        print("INTCAPB: ",hex(self._i2c.Read(self._i2cAdd,self._INTCAPB)))
        print("GPIOA: ",hex(self._i2c.Read(self._i2cAdd,self._GPIOA)))
        print("GPIOB: ",hex(self._i2c.Read(self._i2cAdd,self._GPIOB)))
        print("OLATA: ",hex(self._i2c.Read(self._i2cAdd,self._OLATA)))
        print("OLATB: ",hex(self._i2c.Read(self._i2cAdd,self._OLATB)))

        print("####################################")

        return True