

import time

#from threading import Thread, Lock
from queue import Queue

from library.libmsgbus import msgbus
from library.libtree import tree
from module.adapter.config import configmodule

from module.interface.vdm import VDM

class VHM(msgbus):

    def __init__(self):
      #  Thread.__init__(self)

        self.cfg_queue = Queue()

        self.req_vhm_queue = Queue()
        self.notify_vdm_queue = Queue()

        self.threadList = {}

        self.msgObj = 0

        print ('InitVHM')
        self.setup()

    def setup(self):

        self.msgbus_subscribe('CONF', self._on_cfg)
        self.msgbus_subscribe('VHM_REQUEST', self._on_vhm_request)
        self.msgbus_subscribe('VDM_NOTIFY', self._on_vdm_notify)

    def run(self):

        print ('run VHM')
        self.setup()

        threadRun = True

        while threadRun:
            print('loop vhm')

            while not self.cfg_queue.empty():
                self.on_cfg(self.cfg_queue.get())

            while not self.req_vhm_queue.empty():
                self.on_vhm_request(self.req_vhm_queue.get())

            while not self.notify_vdm_queue.empty():
                self.on_vdm_notify(self.notify_vdm_queue.get())

            time.sleep(1)
        return

    def _on_cfg(self,cfg_msg):
        self.cfg_queue.put(cfg_msg)
        return

    def on_cfg(self,msg):
       # print('Config message',cfg_msg)
        devices = cfg_msg.select('DEVICES')
        self.msgbus_publish('LOG','%s VHM Configuration %s '%('INFO', devices.getTree()))
        for item in devices.getNodes():
            self.msgbus_publish('VDM_REQUEST',item)
        return

    def _on_vhm_request(self,req):
        self.req_vhm_queue.put(req)
        return

    def on_vhm_request(self,req):
        return

    def _on_vdm_notify(self,notify):
        self.req_vdm_queue.put(notify)
        return

    def on_vhm_modify(self,msg):
        return

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



