__author__ = 'oper'

import json

import yaml

from library.libdicttree import *


class Config(Tree):

    def __init__(self):

        self.treeHandle = ''

    def openYaml(self, filename):
        '''
        opens a file Yaml and reads the content
        '''
        handle = open(filename, 'r')
        tempCfg = yaml.load(handle,yaml.BaseLoader)
        handle.close()
        self.treeHandle = Tree(tempCfg)
        #print ('Test',self.config)

    def saveYaml(self, filename):
        '''
        saves the tree and saves it as a Yaml file
        '''
        handle = open(filename,"w")
        yaml.dump(self.config, handle)
        handle.close()

    def importJson(self,jconfig):
        '''
        receives Json String and converts it to dictionary
        :param jsonStr:
        :return:
        '''

        tmpTree = Tree(json.loads(jconfig))

        if 'HEADER' in tmpTree.list():
           # print('MSG',tmpTree.list())
           # print ('Treepointer',tmpTree.select('HEADER'))
            if 'TYPE' in tmpTree.list() and 'CONFIG' in tmpTree.listLeafs():
                print('TYPE',tmpTree.listLeafs())
                print('Merge',self.treeHandle.merge(json.loads(jconfig)))

            elif 'TYPE' in tmpTree.list() and 'DELETE'in tmpTree.listLeafs():
                tmpTree.reset()
                tmpTree.delNode('HEADER')
                print('MSG',tmpTree.list())
                print('Delete',self.treeHandle.delete(json.loads(jconfig)))

        return

    def yaml2json(self,filename):
        handle = open(filename,'r')
        yml = yaml.load(handle,yaml.BaseLoader)
        handle.close()

        return(json.dumps(yml))

    def debug(self):
        print('Output',yaml.dump(self.treeHandle,default_flow_style=False))



if __name__ == '__main__':

    cfg = Config()
    cfg.openYaml('config.yaml')

   # str = '{"MESSAGE":{"TYPE":"ADD"},"TEST":{"MORE":"TEST"}}'
    #jtest = json.loads(str)



    #cfg.importJson(jtest)
    tt = cfg.yaml2json('yaml.yaml')
    print ('tt',tt)
    cfg.importJson(tt)
    cfg.debug()


