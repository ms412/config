

class pulse(msgbus):
    '''
    Function
    switch on/off the I/O port for a pre configured period. The ON/OFF period can be pre configured.

    Configuration Options
    HWID
    PULSE_OFF
    PULSE_ON
    MODE: PULSE

    Mandatory values
    vpmID contains unique ID of the VPM instance -> Port-Section-Name in Configuration
    hwHandle is the object instance performing operation on the hardware, started by the Virtual Device Manger(VDM)
    each port manager (VPM) started from a VDM Instance has the same hwHandle
    callback contains the notification interface of the concerning VDM instance

    _mode = contains the mode type of the VPM object

    ++ Mandatory Values ++
    _hwid = contains the hardware address of the concerning Pin (from configuration file)

    ++ Optional Values ++
    OFF_VALUE = contains parameter returned in case port has low potential at it's interface, if not configured in config file = 'OFF'
    ON_VALUE = contains parameter returned in case port has high potential at it's interface, if not configured in config file = 'ON'
    INTERVAL = update interval reports the current state of the pin after a pre-configured time interval, accuracy depending on the concerning VDM update interval on the,
                expected value is integer; default is 0 -> no update interval
    '''

    def __init__(self,vpmID,hwHandle,callback):

        test = test


