
import json

from module.general.msgbus import MsgBus

class VPM_BinaryOut(MsgBus):
    '''
    classdocs
    '''
    def __init__(self,devHandl):
        '''
        Constructor
        '''
        self._hwId = 0
        self._name = ''
        self._mode = 'BINARY-OUT'


        print('Start VPM',self.threadName)

        self.Setup()

    def Setup(self):
        print('')