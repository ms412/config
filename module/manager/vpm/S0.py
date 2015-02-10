
import json
import time

from library.libmsgbus import msgbus

#from module.manager.vdm import vdm

class S0(msgbus):
    '''
    +++ Function +++
    configures the pin as Input

    +++ Configuration Parameter +++
    VDM_ID {
        FACTOR: <ing>
        HWID: <int>
    }
    FACTOR = sets the number of pulses required for the basis unit such as 1kWatt; type int
    HWID = hardware ID of the pin number at the hardware device; type int

    +++ Request Parameters +++
    VDM_ID {
        TYPE: GET
        COMMAND: GET
    }

    TYPE: indicates a GET message; type string
    COMMAND: REQUEST request a notification of the current port state; type string

    +++ Return Parameters +++
    VPM_ID {
        VALUE: <string>
        MSG: <string>
        STATE: True/False
    }
    VALUE: ad defined in OFF/ON_VALUE; type string
    MSG: in case a detailed message is available it will be delivered in this object; type string
    STATE: either True or False indicates state of the message; type bool
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
        self._mode = 'S0'
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
        print('Config interface S0', self._VPM_ID)
        self._factor = int(cfg.getNode('FACTOR',0))
        self._hwid = int(cfg.getNode('HWID',None))

        if self._hwid is None:
            logmsg = 'HWID is missing in config'
            self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s'%('ERROR', self._mode, self._VPM_ID, logmsg))
            print('S0 VPM::ERROR no HWID in config')
        else:
            print('S0 VPM:', self._hwid)
            self._hwHandle.ConfigIO(self._hwid,'IN')

            '''
            Define class variables
            '''
            self._SavePinState = 0

            self._T0 = time.time()
            self._T1 = 0.0
            self._T2 = 0.0
         #   self._T3 = time.time()

            self._baseState = 0

            self._ResultAvailable = False

            self._watt = 0.0
            self._energySum = 0.0
            self._energyDelta = 0.0
            self._pulsCount = 0
        return True

    def run(self):
        '''
        run is getting called on a regular base from VDM, frequency of calls defined by update value in VDM configuration section
        '''

  #      print('run',self._hwHandle.ReadPin(self._hwid),self._hwid)

        if self._SavePinState > 1 and self._hwHandle.ReadPin(self._hwid) == 0:

           # print "state1"
            print ("SavePinState", self._SavePinState)
            print ("PinState", self._hwHandle.ReadPin(self._hwid))
            self._SavePinState = self._hwHandle.ReadPin(self._hwid)

            if self._T0 == 0:
                '''
                0 -> 1 transient  =T0
                '''
                print ("T0: load current time")
                self._T0 = time.time()

            else:
                print ("T2: measure time T2 -T0")
                self._T2 = time.time()
                self._T1 = self._T2 -self._T0
                print ("T2", self._T2,"T0", self._T0)
                print ("delta T1:",self._T1)
                self._T0 = time.time()
                print ("T0new", self._T0)
                self._power()
                self._energy()
                self._T2 = 0
                self.notify('UPDATE')
                print ("SavePinState", self._SavePinState)
                print ("PinState", self._hwHandle.ReadPin(self._hwid))
#                watt = 1/factor*3600/self._T1*1000


        elif self._SavePinState == 0 and self._hwHandle.ReadPin(self._hwid) > 1:
            print ("State2")
            print ("SavePinState", self._SavePinState)
            print ("PinState", self._hwHandle.ReadPin(self._hwid))
            self._SavePinState = self._hwHandle.ReadPin(self._hwid)

      #  return update
       # self._counter = self._counter +1


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

        msg_container['POWER'] = self._watt
        msg_container['ENERGY'] = self._energySum
        msg_container['DELTA'] = self._energyDelta
        if msg:
            msg_container['MSG'] = msg
        msg_container['STATE'] = 'TRUE'

        container[self._VPM_ID]=msg_container

        logmsg = 'Notification send to VDM'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('INFO', self._mode, self._VPM_ID, logmsg, container))

        self._callback(container)

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

        if 'GET' in msgtype:
            if 'REQUEST' in cmd:
                self.notify()
            else:
                logmsg = 'Command unknown'
                self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s; Message: %s , %s'%('ERROR', self._mode, self._VPM_ID, logmsg, cmd))
          #      print ('Command unknown')
        else:
            logmsg = 'Messagetype unknown'
            self.msgbus_publish('LOG','%s Mode: %s ID: %s; Message: %s , %s'%('ERROR', self._mode, self._VPM_ID, logmsg, msgtype))
            #print('Messagetype unknown')

        return True

    def _power(self):
        self._watt = 1/self._factor * 3600 / self._T1 * 1000
        self._pulsCount = self._pulsCount +1
        print ("POWER", self._watt)

        return self._watt

    def _energy(self):
        energyCurr = float(self._pulsCount / self._factor)
        self._energyDelta = energyCurr - self._energySum
        self._energySum = energyCurr
 #       print self._pulsCount / self._E_FACTOR
        print ("Energy Current %f" % energyCurr, "EnergyDelata %f" % self._energyDelta, "EnergySum %f" % self._energySum, "Pulscounte", self._pulsCount)
        return True