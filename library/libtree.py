


class tree(object):

     def __init__(self,tree):

         self._treeObj = tree

     def select(self,path = None):
         '''
         selects a subtree of the tree
         and creates a new DictTreeLib object on which
         all modification can be done
         '''
         tempTree = self._treeObj
         for temp in path.split('.'):
             tempTree = tempTree.get(temp)

         return tempTree

     def getTree(self):
         return self._treeObj

     def getRoot(self):
         return self._treeObj

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

     def _delete(self,dict1,dict2):
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

         return list(self)
