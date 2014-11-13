
import yaml
import json

from module.libtree import Tree



class Configuration(object):

     def __init__(self):
         self._rootPtr = ''

     def _create(self,dictCfg):
         self._rootPtr = Tree(dictCfg)
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

     def select(self,path=None):
         tempPtr = self._rootPtr.select(path)
         print('kkkk',tempPtr)
         tempObj = Tree(tempPtr)
     #    tempObj.set(tempPtr)
         return tempObj


if __name__ == '__main__':

     A = {'HEADER':{'TEST':123},'A1':{'A11':{'A111':'V111','A112':'V112','A113':'V113'},'A13':'V13'},'A2':{'A21':{'A211':{'A2111':{'A21111':'V2111'}},'A2112':'V2112'}}}
     B = {'A3':{'A11':{'A111':'V111B','B113':'V113B'}},'A2':{'B22':'V22B'}}
     D = {'A3':{'A11':{'A111':'V111B','B113':'V113B'}},'A2':{'B22':'V22B'}}
     C = {'A1':{'A11':{'A111':''},'A13':''},'A2':{'A21':{'A211':{}}}}

     x = Configuration()
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

