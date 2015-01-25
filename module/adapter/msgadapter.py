import json
import time
from queue import Queue
from threading import Thread

from library.libmsgbus import msgbus
from library.libtree import tree
#from library.libmqttbroker import mqttbroker
from library.libmqtt import mqttbroker

class msgadapter(Thread,msgbus):

    def __init__(self):
        Thread.__init__(self)

        self._consumer = ''
        self._mqtt_config_path = ''
        self._mqtt_subscribe_path = ''
        self._mqtt_publish_path = ''

        '''
        Setup message Queues
        '''
        self._configQ = Queue()
        self._notifyQ = Queue()

        self._mqttbroker = None

        msg = 'Create Object'
        self.msgbus_publish('LOG','%s msgadapter: %s '%('DEBUG',msg))

        print('start openhab Adapter')

    def __del__(self):
        msg = 'Delete Object'
        self.msgbus_publish('LOG','%s msgadapter: %s '%('DEBUG',msg))


    def setup(self):
        ''''
        setup message pipes
        '''
        self.msgbus_subscribe('CONFIG', self._on_config)
        self.msgbus_subscribe('DATA_TX', self._on_notify)
        return True

    def run(self):

        self.setup()

        threadRun = True

        while threadRun:

            while not self._configQ.empty():
                self.on_config(self._configQ.get())

            while not self._notifyQ.empty():
          #      print('zzzzz')
          #      if self._mqttbroker:
                self.on_notify(self._notifyQ.get())

            if self._mqttbroker:
              #  print('mqttbroker true',self._mqttbroker)
                while True:
                    msg = self._mqttbroker.rx_data()
                    if msg:
                        print('MEssage available',msg)
                        self.on_request(msg)
                    else:
                        break

            time.sleep(1)

        return True

    def _on_notify(self,msg):
     #   print('Receive notification',msg)
        self._notifyQ.put(msg)
        return True

    def _on_config(self,msg):
    #    print('Received config',msg)
        self._configQ.put(msg)

        return True

    def on_config(self,cfg_msg):
        msg = 'Config Object'
        self.msgbus_publish('LOG','%s msgadapter: %s Message: %s'%('INFO',msg,cfg_msg))

        broker = cfg_msg.select('BROKER')
        self._consumer = broker.getNode('CONSUMER','OPENHAB')
        self._mqtt_config_path = broker.getNode('CONFIG','/GPIO1/CONFIG')
        self._mqtt_subscribe_path = broker.getNode('SUBSCRIBE','/GPIO1')
        self._mqtt_publish_path = broker.getNode('PUBLISH','/OPENHAB')

        if not self._mqttbroker:
          #  print('Messagebroker:: initial startup',broker.getTree())
            self._mqttbroker = mqttbroker(broker.getTree())
            #print ('MEssagebroker: start new MQTT ',self._mqttbroker)
        else:
           # print ('MEssagebroker: New Configuration available restart broker',self._mqttbroker)

            self._mqttbroker.restart(broker.getTree())
            #del self._mqttbroker
            #time.sleep(0.5)
            #self._mqttbroker = mqttbroker(broker.getTree())
          #  print ('MEssagebroker: start new MQTT with updated ',self._mqttbroker)
        return True

    def on_notify(self,msg):

        if 'OPENHAB' in self._consumer:
            msg_log = 'Notification Publish for Openhab'
            self.msgbus_publish('LOG','%s msgadapter: %s '%('INFO',msg_log))
           # print('Publish OPENAB', self._consumer)
            self._mqttbroker.tx_data(self.gpio2openhab(msg))
        else:
            msg_log = 'Notification Publish Plaint'
            self.msgbus_publish('LOG','%s msgadapter: %s '%('INFO',msg_log))
        #    print('Publish PLAIN')
            msg['MESSAGE'] = self._generate_header('NOTIFY')
            self._mqttbroker.tx_data(self.gpio2plain(msg))
     #   print('messagebroker::msg broker',msg)
           # self._mqttbroker.tx_data(self._dict2json(msg))
       # self.msgbus_publish('MSG_TX',self._dict2json(msg))
        return True

    def on_request(self,msg):

        path = msg.get('CHANNEL',None)
        payload = msg.get('MESSAGE',None)
        payload = self._json2dict(payload)

        if path in self._mqtt_config_path:
            msg_log = 'Request Publish for Openhab'
            self.msgbus_publish('LOG','%s msgadapter: %s '%('INFO',msg_log))
        #    print ('PRODUCER sends GPIO2MQTT message format')
         #   print ('no conversion required',payload)
            self.on_message(payload)

        else:
            msg_log = 'Request Publish in plain mode'
            self.msgbus_publish('LOG','%s msgadapter: %s '%('INFO',msg_log))
        #    print ('PRODUCER is OPENHAB')
         #   print('convert messag to gpio2mqtt format',payload)

            self.on_message(self.openhab2gpio(path,payload))

        return True

    def on_message(self,msg):
        '''
        :param msg:
        :return:

        in MESSAGE Header
         -+ TYPE = CONFIG
          -+MODE = ADD | DEL | NEW
         -+TYPE = REQUEST
          -+MODE = NONE

        '''

        msg_header = msg.get('MESSAGE',None)
        del msg['MESSAGE']

        if msg_header:
            msg_type = msg_header.get('TYPE',None)

            if msg_type == 'CONFIG':
                msg_mode = msg_header.get('MODE',None)
                if msg_mode == 'ADD':
                    msg_log = 'Message: Config, Type: Add'
                    self.msgbus_publish('LOG','%s msgadapter: %s '%('INFO',msg_log))
               #     print('ADD message')
                    self.msgbus_publish('CFG_ADD',msg)
                elif msg_mode == 'DEL':
                    msg_log = 'Message: Config, Type: Del'
                    self.msgbus_publish('LOG','%s msgadapter: %s '%('INFO',msg_log))
                 #   print('DEL message')
                    self.msgbus_publish('CFG_DEL',msg)
                else:
                    self.msgbus_publish('CFG_NEW',msg)
                    msg_log = 'Message: Config, Type: New'
                    self.msgbus_publish('LOG','%s msgadapter: %s '%('INFO',msg_log))

            elif msg_type == 'REQUEST':
                msg_log = 'Message: Request'
                self.msgbus_publish('LOG','%s msgadapter: %s '%('INFO',msg_log))
       #         print('Request message')
                self.msgbus_publish('REQUEST',msg)

        else:
            msg_log = 'Message: UNKNOWN'
            self.msgbus_publish('LOG','%s msgadapter: %s Message: %s'%('ERROR',msg_log))

        return True

    def gpio2plain(self,msg):

        mqtt_msg ={}

        mqttpath = self._mqtt_publish_path
        #print('mqttpath',mqttpath,'mqttpayload',mqttpayload)

        mqtt_msg['CHANNEL']=mqttpath
        mqtt_msg['MESSAGE']=self._dict2json(msg)

        print('Message Plain',mqtt_msg)
        return mqtt_msg

    def openhab2gpio(self,mqttpath,mqttpayload):

      #  mqttpath = msg.get('PATH')
      #  mqttpayload = msg.get('MESSAGE')

        print('PATH:',mqttpath)
        print('MESSAGE',mqttpayload)
       # mqttpath = self._json2dict(mqttpath)
        #mqttpayload = self._json2dict(mqttpayload)

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

        return msg

    def gpio2openhab(self,msg):

        mqtt_msg = {}

        section = msg.get('DEVICES')
        print('DEVICES',section)

       # (mqttpath,mqttpayload) = self.recurs(section,'')
        (mqttpath,mqttpayload) = self._get_nested_dict_path(section,'')

      #  print(mqttpath,mqttpayload)
        mqttpath = self._mqtt_publish_path + mqttpath
        print('mqttpath',mqttpath,'mqttpayload',mqttpayload)

        mqtt_msg['CHANNEL']=mqttpath
        mqtt_msg['MESSAGE']=self._dict2json(mqttpayload)

        #self._mqttbroker.tx_data(mqtt_msg)
        return mqtt_msg

    def _get_nested_dict_path(self,section,path):
        #string = ''
        for key, item in section.items():
            print('Key,Items',key,item)
            if isinstance(item,dict):
                path+='/'
                path+=str(key)
                #print('mqttpath',string,item)
                (path,item)=self._get_nested_dict_path(item,path)

            else:
                path+='/'
                item = section
                break

        return path,item


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

    def _dict2json(self,dict):
       # return str(dict)
        return json.dumps(dict)

    def _json2dict(self,j_data):
        return json.loads(j_data.decode('utf8'))



if __name__ == "__main__":



    def startup():
        broker = {}
        test = {}

        broker['HOST']='localhost'
        broker['PORT']=1883
        broker['PUBLISH']='/OPENHAB'
        broker['SUBSCRIBE']='/GPIO1/'
        broker['CONFIG']='/GPIO1/CONFIG/'
        broker['CONSUMER']='OPENHAB'

        test['BROKER']=broker
        t = tree(test)

        bus.msgbus_publish('CONFIG',t)

        return True

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
      #  notify_msg = {'DEVICES': {'MCP23017_1': {'PORT10': {'AA': {'BB': {'CC': {'DD': {'EE': {'STATUS': 'ON','PORT':'OPEN','VALUE':'ON'}}}}}}}}, 'MESSAGE': {'TIME': 1421862422, 'TYPE': 'REQUEST'}}
        notify_msg = {'DEVICES': {'MCP23017_1': {'PORT10':{'STATUS': 'ON','PORT':'OPEN','VALUE':'ON'}}}}
        #oh.gpio2openhab(notify_msg)
        bus.msgbus_publish('DATA_TX',notify_msg)
        return True

    bus = msgbus()
    #broker =msgbroker()
    oh = msgadapter()
    oh.start()


    #request()
    #notify()
    startup()
    time.sleep(20)
    notify()