


class tree(object):

     def __init__(self,tree):
    #   print('Tree init')
        self._treeObj = tree
        #print ('Tree',tree)

     def select_old(self,path = None):
         '''
         selects a subtree of the tree
         and creates a new DictTreeLib object on which
         all modification can be done
         '''
         tempTree = self._treeObj
         for temp in path.split('.'):
             tempTree = tempTree.get(temp)

         return tempTree

     def select(self,path = None):
         tempTree = self._treeObj
         for temp in path.split('.'):
          #   print('temptree',tempTree)
             tempTree = tempTree.get(temp)

         return tree(tempTree)


     def getTree(self):
         return self._treeObj

     def getRoot(self):
         return self._treeObj

     def getNodesKey(self):
         nodekeylist = []
         for k,v in self._treeObj.items():
             if isinstance(v,dict):
                 nodekeylist.append(k)
         return nodekeylist

     def getNodes(self):
         nodelist = []
         for k,v in self._treeObj.items():
             if isinstance(v,dict):
                 nodelist.append(self._treeObj[k])
         return nodelist

     def getLeafs(self):
         leaflist = []
         for k,v in self._treeObj.items():
             if not isinstance(v,dict):
                 leaflist.append(self._treeObj[k])
         return leaflist

     def getNode(self,key,default = None):
         return self._treeObj.get(key,default)

     def addNode(self,key,value):
         self._treeObj[key]=value

     def addLeaf(self,key,value):
         self.addNode(key,value)

     def delNode(self,key):
         del self._treeObj[key]

     def delLeaf(self,key):
         self.delNode(key)

     def debug(self):
         return(self._treeObj)

     def merge(self,dict):
      #   print('Dict', self._treeObj)
         return self._merge(self._treeObj,dict)

     def _merge(self, dict1, dict2):
         """ Recursively merges dict2 into dict1 """
         if not isinstance(dict1, dict) or not isinstance(dict2, dict):
             return dict2
         for k in dict2:
          #   print('k',k)
             if k in dict1:
                 dict1[k] = self._merge(dict1[k], dict2[k])
             else:
                 dict1[k] = dict2[k]
         return dict1

     def delete(self,dict):
         return self._delete(self._treeObj,dict)

     def _delete_oldold(self,dict1,dict2):
         print('Dict1',dict1,'Dict2',dict2)

         if not isinstance(dict2,dict):
             print('isnot')

         for k in dict2:
             if not isinstance(dict2[k],dict):
                 del dict1[k]
                 print('delete',k)
             elif k in dict1:
                 del dict1[k]
             else:
                 self._delete(dict1[k],dict2[k])
         print('Return',dict1)
         return dict1

     def _delete(self,dict1,dict2):
       # print('¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦¦')
        # print('Debug new:',dict1, dict2)
         for key,value in dict2.items():
            if isinstance(value,dict):
                temp1 = dict1.get(key)
                temp2 = dict2.get(key)
                self._delete(temp1,temp2)
            else:
         #       print('Delete',key)
               # del dict1[key]
                dict1.pop(key,None)
         return True

     def leafPath(self):
         return self._leafPath(self._treeObj)

     def _leafPath(self,dict):
         '''
         returns the path to each leaf of the tree, returns tree
         '''

         for key,value in dict.items():
             if not isinstance(value,dict):
                 yield tuple([key, value])
             else:
                 for subpath in self.leafPath(value):
                     yield (key,)+ subpath

        # return list(self)
