
import yaml
import json
import time
from queue import Queue

from threading import Thread, Lock

from library.libtree import tree
from library.libmsgbus import msgbus

class configmodule(Thread,msgbus):

     def __init__(self,cfg_file):
         Thread.__init__(self)
         self._rootPtr = ''
         self.cfg_file = cfg_file

         '''
         Setup message Queues
         '''
         self.msg_queue = Queue()



     def run(self):

        print ('run config adapter')

        self.setup(self.cfg_file)

        threadRun = True

        while threadRun:
            time.sleep(3)
            print('config loop')
            self.msgbus_publish('LOG','%s Configuration loop '%('WARNING'))

            while not self.msg_queue.empty():
                self.on_msg(self.msg_queue.get())

        return True

     def _on_msg(self,msg):
        self.msg_queue.put(msg)
        return True

     def on_msg(self,msg):
         print('CONFIG message received',msg)
         return True

     def setup(self,filename):
         x = self.loadFile(filename)
         self.msgbus_publish('CONF',x)

         ''''
         setup message pipes
         '''
         self.msgbus_subscribe('CONF_MSG', self._on_msg)

         return True

     def _create(self,dictCfg):
         self._rootPtr = tree(dictCfg)
         #elf._rootPtr.set(dictCfg)
         return self._rootPtr

     def loadDict(self,dictCfg):
         return self._create(dictCfg)

     def loadJson(self,jsonstr):
         '''
         receives Json String and converts it to dictionary
         :param jsonStr:
         :return:
         '''
         print('String',jsonstr)
         jdata = json.loads(jsonstr)
         if 'HEADER' in jdata:
             print('jsting',jdata)
         return

     def loadFile(self,filename):
         handle = open(filename,'r')
         dictCfg = yaml.load(handle,yaml.BaseLoader)
         handle.close()
         return self._create(dictCfg)

     def saveFile(self, filename):
         '''
         saves the tree and saves it as a Yaml file
         '''
         handle = open(filename,"w")
         yaml.dump(self._rootPtr.gettree(), handle)
         handle.close()
         return

     def publish(self):
         print('Root Pointer',self._rootPtr)
         self.msgbus_publish('CONF',self._rootPtr)

     def select(self,path=None):
         tempPtr = self._rootPtr.select(path)
         print('kkkk',tempPtr)
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
     y.delNode('A11')
     print('Delete Node',y.debug())
     y.addLeaf('A14','V14')
     print('Add Leaf',y.debug())
     print('Tree',r.debug())
     y.merge(B)
     print('Merge',y.debug())
     print('Leaf',y.leafPath())
     y.delete(D)
     print('Delete',y.debug())


