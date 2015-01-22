import json
import time
from queue import Queue
from threading import Thread

from library.libmsgbus import msgbus
from library.libtree import tree
from library.libmqttbroker import mqttbroker

class openhabAdapter(msgbus):

    def __init__(self):

        self._mqtt_config_path = '/GPIO1/CONFIG'
        self._mqtt_subscribe_path = '/GPIO1'
        self._mqtt_publish_path = ''

        print('start openhab Adapter')

    def openhab2gpio(self,msg):

        mqttpath = msg.get('PATH')
        mqttpayload = msg.get('MESSAGE')

        print('PATH:',mqttpath)
        print('MESSAGE',mqttpayload)

        if mqttpath not in self._mqtt_config_path:

            devices_msg = {}
            path_list = mqttpath.split('/')
            print('Pathlist',path_list)

            devices_msg[path_list.pop(-1)] = mqttpayload
         #   print('Devices',devices_msg)
            for id, item in reversed(list(enumerate(path_list))):
             #   print('Test',id,item)
                if item not in self._mqtt_subscribe_path:
              #      print('Create',item)
                    temp={}
                    temp[item]=devices_msg
                    devices_msg=temp
               #     print('TEMP',devices_msg)
            #print('Result',devices_msg)
            msg={}
            msg['DEVICES']=devices_msg
            msg['MESSAGE'] = self._generate_header('REQUEST')

        else:
            print('CONFIG Mesage')

         #   devices_msg['DEVICES']=path_list[]

        print('Message',msg)

        return True

    def gpio2openhab(self,msg):

        temp = msg.get('DEVICES')
        print('DEVICES',temp)

        (mqttpath,mqttpayload) = self.recurs(temp,'')

        mqttpath = '/'+'DEVICES'+mqttpath
        print('mqttpath',mqttpath,'mqttpayload',mqttpayload)

    def recurs(self,temp,string):

        for key, item in temp.items():
            print('Key,Items',key,item)
            if isinstance(item,dict):
                string+='/'
                string+=str(key)
                #print('mqttpath',string,item)
                (string,item)=self.recurs(item,string)

            else:
                string+='/'
                item = temp
                break

        return string,item



    def _generate_header(self,header_type):

        msg_header= {}

        if 'NOTIFY' in header_type:
            msg_header['TYPE']='NOTIFY'

        elif 'REQUEST' in header_type:
            msg_header['TYPE']='REQUEST'

        elif 'CONFIG' in header_type:
            msg_header['TYPE']='ADD'

        else:
            msg_header['TYPE']='UNKNOWN'

        msg_header['TIME']=int(time.time())

        return msg_header


if __name__ == "__main__":


    def request():
        mqttpath = '/GPIO1/MCP23017_1/PORT10/AA/BB/CC/DD/EE'
        mqttpayload = {'STATUS':'ON'}
        msg = {'PATH':mqttpath,'MESSAGE':mqttpayload}

        oh.openhab2gpio(msg)
        return True

    def config():
        mqttpath = '/GPIO1/CONFIG'
        mqttpayload = {'STATUS':'ON'}
        msg = {'PATH':mqttpath,'MESSAGE':mqttpayload}

        oh.openhab2gpio(msg)
        return True

    def notify():
        notify_msg = {'DEVICES': {'MCP23017_1': {'PORT10': {'AA': {'BB': {'CC': {'DD': {'EE': {'STATUS': 'ON','PORT':'OPEN','VALUE':'ON'}}}}}}}}, 'MESSAGE': {'TIME': 1421862422, 'TYPE': 'REQUEST'}}

        oh.gpio2openhab(notify_msg)
        return True

    oh = openhabAdapter()

    #request()
    notify()