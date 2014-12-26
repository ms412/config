
import json
from queue import Queue

from library.libmsgbus import msgbus
#from module.manager.vdm import vdm

class binout(msgbus):
    '''
    Class documentation
    '''
    def __init__(self,ID,hwHandle,callback):
        '''
        Constructor
        ID = unique Port ID VPM listens to
        hwHandle = handle for the hardware
        notifyIF = interface to which the VPM sends notifications
        '''

        self._ID = ID
        self._hwHandle = hwHandle
        self._callback = callback

        '''
        System parameter
        '''
        self._mode = 'BINARY-IN'
        self._hwID

        '''
        Class variables
        '''
        self._pinstatesave = 0
        self._update = False



        self._counter = 0

        self.setup()

    def setup(self):
        '''
        this method is called from init
        add mandatory functions during setup the object
        '''
        self.msgbus_publish('LOG','%s VPM Module Mode: %s Created with vpmID: %s '%('DEBUG', self._mode, self._ID))

        return True


    def config(self,msg):
        '''
        Configuration interface
        msg =  data type tree
        '''
        result = False

        '''
        mandatory values
        '''
        try:
            self._hwID = int(msg.getNode('HWID'))
        except:
            self.msgbus_publish(self._log,'%s VPM Port: %s Mandatory Parameter missing'%('ERROR',self._ID))

        '''
        optional configuration Items
        '''
        self._OFF_VALUE = self._config.get('OFF_VALUE','OFF')
        self._ON_VALUE = self._config.get('ON_VALUE','ON')
        self._INITIAL = self._config.get('INITIAL',None)

        '''
        configure port as output
        '''
        self._hwHandle.ConfigIO(self._hwid,0)

        '''
        set initial configuration
        '''
        if self._INITIAL == self._ON_VALUE:
            self._hwHandle.WritePin(self._HWID, 1)
            self._SavePinState  = 1
        else:
            self._hwHandle.WritePin(self._HWID, 0)
            self._SavePinState  = 0
            self.Set(self._INITIAL)

        return result

    def run(self):
        test ={}
        self._counter = self._counter+1
        print ('VPN BinIn')
        test['Counter']=self._counter
        test['ID']=self._VPM_ID
        print('Testmessage',test)
      #  self._callback(test)

        '''
        Run Task
        '''


    def on_req(self,value):

        '''
        Port set port polarity; value as defined in ON_VALUE or OFF_VALUE
        '''
        if self._ON_VALUE in value:
            self._hwHandle.WritePin(self._HWID, 1)
            self._SavePinState  = 1

        elif self._OFF_VALUE in value:
            self._hwHandle.WritePin(self._HWID, 0)
            self._SavePinState  = 0

        else:
            self.msgbus_publish(self._log,'%s VPM BinaryOut Port: %s Unknown value'%('ERROR',value))

        return True

    def notify(self):

        notify_msg= {}

        notify_msg['PORT_ID'] = self._VPM_ID
        notify_msg['VALUE'] = self._pinstatesave
        notify_msg['STATE'] = True

        self._callback(notify_msg)

    def on_cfg(self,msg):
        print('message',msg)
        portcfg = msg.select(self._VPM_ID)
        self.config(portcfg)

        return True