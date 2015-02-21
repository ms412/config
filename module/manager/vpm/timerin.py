
import json
import time

from library.libmsgbus import msgbus

class timerin(msgbus):
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

