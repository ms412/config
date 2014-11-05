

import time

#from threading import Thread, Lock
from queue import Queue

from module.general.msgbus import MsgBus
from module.general.dicttree import DictionaryTree

from module.interface.vdm import VDM

class VHM(MsgBus):

    def __init__(self):
      #  Thread.__init__(self)

        self.cfgQueue = Queue()
        self.RequestQueue = Queue()
        self.NotifyQueue = Queue()

        self.threadList = {}

        self.msgObj = 0

        print ('InitVHM')
        self.Setup()

    def run(self):

        print ('run mqtt')
        self.setup()

        threadRun = True

        while(threadRun == True):
            print('loop vhm')
            try:
                self.msgObj = self.cfgQueue.get_nowait()
                print('VHM Config available',self.msgObj)
                self.msgHeader()
            except:
                print ('VHM Queu Empty')
            time.sleep(1)
        return

    def Setup(self):

        '''
        Subscribe to Notification Channels
        '''

        self.subscribe('CONFIG', self.ConfigIF)
        self.subscribe('REQUEST', self.RequestIF)
        self.subscribe('NOTIFY', self.NotifyIF)

        print('VHM Setup Completed')

    def ConfigIF(self,message):

        print ('Receive VHM config',message)

        cfgMsg = message.get('DEVICES',None)
        print ('ConfigMessage',cfgMsg)
   #     if None not in cfgMsg:
        if cfgMsg:
            self.VHMConfig = DictionaryTree(cfgMsg)
            self._SelfConfig(self.VHMConfig.GetLeafs())
            self._VDMConfig(self.VHMConfig.GetNodes())

        else:
            print('Nothing to do')


   #         VHMcfg = cfgMsg.Get.Leafs()
            '''
            has Devices config
            '''
    #        cfgDevMsg = cfgMsg.tree.get('DEVICES',None)
     #       if None not in cfgDevMsg:
     #           self._VHMCfg(cfgDevMsg.tree.local())
      #          self._VDMCfg(cfgDevMsg.subtree())
            '''
            has Device xyz config

            does Device xyz exists
            '''
            print ('Received Configuration Message')
          #  self.cfgQueue.put(cfgMsg)
        return

    def RequestIF(self,message):

        item = message.get('DEVICES',None)
        if None not in item:
            print ('Write in vhm DataRx Queue')
            self.cfgQueue.put(item)
        return

    def NotifyIF(self, message):

        print('Get data', message)

        return

    def _SelfConfig(self,VHMcfg):

        print ('_SelfConfig', VHMcfg,len(VHMcfg))

        if len(VHMcfg) > 0:
            print ('VHM Config')

        return

    def _VDMConfig(self,cfgMsg):
        print('_VDMConfig',cfgMsg)

        for key in cfgMsg.keys():
            print('KEY',key)
            '''
            Look up if the VDM instance already exists
            '''
            item = self.threadList.get(key,None)
            if item:
                '''
                instance exists
                '''
             #   print('call VDH Instance',item)
  #              self.cfgQueue.put(cfgMsg)
                self.MsgBusPublish('VDM_CFG',cfgMsg)
            else:
                '''
                create VDM instance
                '''
                threadID = VDM(key)

#                threadID.setName(key)
                threadID.start()
                self.threadList[key]=threadID
                print('Thread Lists',self.threadList)
                self.MsgBusPublish('VDM_CFG',cfgMsg)



