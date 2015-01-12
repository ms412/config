
import smbus
#import random

#from library.general.logAdapter import loghandle

class i2c(object):
    '''
    classdocs
    '''

    def __init__(self,Raspberry_Rev):
        '''
        Constructor
        '''
#        self._loghandle = loghandle()

      #  self._loghandle.info('i2cWrapper:init, Object created: Version: , Date: ')

        self._i2c = smbus.SMBus(Raspberry_Rev)
    #    self._i2c = 0

    def Write(self,i2cDeviceID,address,value):
        """ Write data to physical device
            address = register address
            int_data = data written to the register
        """
        self._i2c.write_byte_data(i2cDeviceID,address,value)

        return True

    def Read(self,i2cDeviceID,address):
        """ Read data from physical device
            address = register address
            returns
            int_data = data read from the register
        """
        value = self._i2c.read_byte_data(i2cDeviceID,address)
  #      value = random.randint(0,1)

        return value