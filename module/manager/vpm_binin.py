
import json

from library.libmsgbus import msgbus

class vpm_binin(msgbus):
    '''
    classdocs
    '''
    def __init__(self,portID,hwHandle,callback):
        '''
        Constructor
        portID = unique IF VPM listens to
        hwHandle = handle for the hardware
        notifyIF = interface to which the VPM sends notifications
        '''

        self._VPM_ID = portID
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
        self._pinstatesave = 0
        self._update = False



        self._counter = 0

        self.setup()

    def setup(self):
       # self.msgbus_publish('LOG','%s VPM Module BINARY IN Setup Configuration: %s '%('INFO', self._VPM_CFG))    def setup(self):

        print('VPM Mode:', self._mode,'ID', self._VPM_ID)



    def config(self,msg):
        print('Config interface')
        self._off_value = str(msg.getNode('OFF_VALUE','OFF'))
        self._on_value = str(msg.getNode('ON_VALUE','ON'))
        self._hwid = int(msg.getNode('HWID',None))

        if not self._hwid:
            print('VPM::ERROR no HWID in config')

        '''
        configure port as input port
        '''
        self._hwHandle.ConfigIO(self._hwid,1)


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

        pinstate = self._hwHandle.ReadPin(self._hwid)

        if pinstate != self._pinstatesave:
            self._pinstatesave = pinstate

            '''
            Pin State changed during two runs
            now we have to send notification
            '''
            self.notify()


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