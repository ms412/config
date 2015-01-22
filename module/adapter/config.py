
import yaml
import json
import time
import datetime
from queue import Queue

from threading import Thread, Lock

from library.libtree import tree
from library.libmsgbus import msgbus

class configmodule(Thread,msgbus):

     def __init__(self,cfg_file=None):
         Thread.__init__(self)
         self._rootPtr = ''
         self.cfg_file = cfg_file

         '''
         Setup message Queues
         '''
         self.msg_queue = Queue()
         self.add_queue = Queue()
         self.del_queue = Queue()
         self.new_queue = Queue()


     def run(self):

   #     print ('run config adapter')

        self.setup(self.cfg_file)

        threadRun = True

        while threadRun:
            time.sleep(1)
    #        print('config loop')
         #   self.msgbus_publish('LOG','%s Configuration loop '%('WARNING'))

            while not self.msg_queue.empty():
                self.on_msg(self.msg_queue.get())

            while not self.add_queue.empty():
                self.on_add(self.add_queue.get())

            while not self.del_queue.empty():
                self.on_del(self.del_queue.get())

        return True

     def _on_msg(self,msg):
        self.msg_queue.put(msg)
        return True

     def _on_add(self,msg):
         self.add_queue.put(msg)
         return True

     def _on_del(self,msg):
         self.del_queue.put(msg)
         return True

     def _on_new(self,msg):
         self.new_queue.put(msg)
         return True

     def on_msg(self,msg):
         print('CONFIG message received',msg)
         return True

     def on_add(self,msg):
         self.msgbus_publish('LOG','%s CONFIG: ADD Message received %s'%('TRACE',msg))
         self._rootPtr.merge(msg)
         ts = time.time()
         time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M')
         self.saveFile(self.cfg_file+'_'+time_stamp)
         self.publishUpdate(self._rootPtr)
         return True

     def on_del(self,msg):
         self.msgbus_publish('LOG','%s CONFIG: DEL Message received %s'%('TRACE',msg))
         self._rootPtr.delete(msg)
         ts = time.time()
         time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M')
         self.saveFile(self.cfg_file+'_'+time_stamp)
         self.publishUpdate(self._rootPtr)
         return True

     def setup(self,filename):
         if self.cfg_file:
            cfg_tree = self.loadFile(filename)
            self.publishUpdate(cfg_tree)
            #self.msgbus_publish('CONF',x)

         ''''
         setup message pipes
         '''
         self.msgbus_subscribe('CFG_ADD',self._on_add)
         self.msgbus_subscribe('CFG_DEL',self._on_del)
         self.msgbus_subscribe('CFG_NEW',self._on_new)
    #     self.msgbus_subscribe('CONF_MSG', self._on_msg)

         return True

     def publishUpdate(self,cfg_tree):
         self.msgbus_publish('LOG','%s CONFIG: Publish new configuration %s'%('TRACE',cfg_tree.getTree()))
         self.msgbus_publish('CONFIG',cfg_tree)
       #  self.msgbus_publish('CONF',cfg_tree)
         return True

     def createTree(self,dictCfg):
         self._rootPtr = tree(dictCfg)
         #elf._rootPtr.set(dictCfg)
         return self._rootPtr

     def loadDict(self,dictCfg):
         return self.createTree(dictCfg)

     def loadJson(self,jsonstr):
         '''
         receives Json String and converts it to dictionary
         :param jsonStr:
         :return:
         '''
      #   print('String',jsonstr)
         jdata = json.loads(jsonstr)
         if 'HEADER' in jdata:
             print('jsting',jdata)
         return

     def loadFile(self,filename):
         handle = open(filename,'r')
         dictCfg = yaml.load(handle,yaml.BaseLoader)
         handle.close()
         return self.createTree(dictCfg)

     def saveFile(self, filename):
         '''
         saves the tree and saves it as a Yaml file
         '''
         handle = open(filename,"w")
         yaml.dump(self._rootPtr.getTree(), handle)
         handle.close()
         return

     def publish(self):
    #     print('Root Pointer',self._rootPtr)
       #  self.msgbus_publish('CONF',self._rootPtr)
         self.msgbus_publish('CONFIG',self._rootPtr)

     def select(self,path=None):
         tempPtr = self._rootPtr.select(path)
      #   print('kkkk',tempPtr)
         tempObj = tree(tempPtr)
     #    tempObj.set(tempPtr)
         return tempObj


if __name__ == '__main__':

     A = {'HEADER':{'TEST':123},'A1':{'A11':{'A111':'V111','A112':'V112','A113':'V113'},'A13':'V13'},'A2':{'A21':{'A211':{'A2111':{'A21111':'V2111'}},'A2112':'V2112'}}}
     B = {'A3':{'A11':{'A111':'V111B','B113':'V113B'}},'A2':{'B22':'V22B'}}
     D = {'A3':{'A11':{'A111':'V111B','B113':'V113B'}},'A2':{'B22':'V22B'}}
     C = {'A1':{'A11':{'A111':''},'A13':''},'A2':{'A21':{'A211':{}}}}

     x = configmodule()
     r= x.loadDict(A)
     y = x.select('A1')
     print('kk',y)
     print('Debug',y.debug())
   #  y.delNode('A11')
     print('Delete Node',y.debug())
   #  y.addLeaf('A14','V14')
     print('Add Leaf',y.debug())
     print('Tree',r.debug())
     y.merge(B)
     print('Merge',y.debug())
     print('Leaf',y.leafPath())
     y.delete(D)
     print('Delete',y.debug())


