
import json

from library.libmsgbus import msgbus

class vpm_binin(msgbus):
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


        '''
        name pipe
        communication channel
        '''
        self._commConf_Handle = 'CONF_VPM'+self._commHandle
        self._commReq_Handle = 'REQ_VPM'+self._commHandle
        self._commNotify_Handle = 'NOTIFY_VDM'+self._commHandle

       # self._VPM_CFG = cfg

        self.Setup()

    def setup(self):
       # self.msgbus_publish('LOG','%s VPM Module BINARY IN Setup Configuration: %s '%('INFO', self._VPM_CFG))    def setup(self):

        self.msgbus_subscribe(self._commConf_Handle, self._on_cfg)
        self.msgbus_subscribe(self._commReq_Handle, self._on_vdm_request)
        self.msgbus_subscribe(self._commNotify_Handle, self._on_vpm_notify)



    def run(self):
        print ('VPN BinIn')