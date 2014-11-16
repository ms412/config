
import json

from library.libmsgbus import msgbus

class vpm_binin(msgbus):
    '''
    classdocs
    '''
    def __init__(self,cfg,devHandl):
        '''
        Constructor
        '''
        self._hwId = 0
        self._name = ''
        self._mode = 'BINARY-OUT'

        self._VPM_CFG = cfg

        self.Setup()

    def Setup(self):
        self.msgbus_publish('LOG','%s VPM Module BINARY IN Setup Configuration: %s '%('INFO', self._VPM_CFG))
        print('')