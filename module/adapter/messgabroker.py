
import json
import time

from queue import Queue
from threading import Thread, Lock
from library.libmsgbus import msgbus
from library.libtree import tree
from library.libmqttadapter import mqtt_adapter


class msgbroker(Thread,msgbus):

    def __init__(self):
        Thread.__init__(self)

        self.mqttAdapter = ''

        '''
        Setup message Queues
        '''
        self._configQ = Queue()
        self._notifyQ = Queue()


    def run(self):

        self.setup()

        threadRun = True

        while threadRun:

           # while not self._receiveQ.empty():
            #    self.on_data_rx(self.dataRx_queue.get())

            while not self._configQ.empty():
                self.on_config(self._configQ.get())


            while not self._notifyQ.empty():
                self.on_notify(self._notifyQ.get())


        return True

    def setup(self):
        ''''
        setup message pipes
        '''
        self.msgbus_subscribe('NOTIFY', self._on_notify)
        self.msgbus_subscribe('CONFIG', self._on_config)

        self.mqttAdapter = mqtt_adapter()


        return True

    def _on_notify(self,msg):
        self._notifyQ.put(msg)
        return True

    def _on_config(self,msg):
        self._configQ.put(msg)
        return True

    def on_config(self,cfg_msg):
        self.mqttAdapter.config(cfg_msg)
        return True

    def on_notify(self,msg):
        msg['MESSAGE'] = self._generate_header('NOTIFY')
        print('TEST',msg)
        self.mqttAdapter.publish(self._dict2json(msg))
        return True

    def _on_data_rx(self,msg):
        self.dataRx_queue.put(msg)
        return True

    def on_data_rx(self,msg):
        msg = self._json2dict(msg.payload)
        msg_header = msg.get('MESSAGE',None)
        if msg_header:
            msg_type = msg_header.get('TYPE',None)

            if msg_type == 'CONFIG':
                msg_mode = msg_header.get('MODE',None)
                if msg_mode == 'ADD':
                    self.msgbus_publish('CFG_ADD',msg)
                elif msg_mode == 'DEL':
                    self.msgbus_publish('CFG_DEL',msg)
                else:
                    self.msgbus_publish('CFG_NEW',msg)

            elif msg_type == 'REQUEST':
                self.msgbus_subscribe('REQ_MSG',msg)

            else:
                print('Not found',msg)

        return True


    def _generate_header(self,header_type):

        msg_header= {}

        if 'NOTIFY' in header_type:
            msg_header['TYPE']='NOTIFY'

        elif 'CONFIG' in header_type:
            msg_header['TYPE']='ADD'

        else:
            msg_header['TYPE']='UNKNOWN'

        msg_header['TIME']=int(time.time())

        return msg_header


    def _json2dict(self,j_data):
        return json.loads(j_data.decode('utf8'))[0]

    def _dict2json(self,dict):
       # return str(dict)
        return json.dumps(dict)



if __name__ == "__main__":

    bus = msgbus()

    broker =msgbroker()
    broker.start()

    broker = {}
    test = {}
    broker['HOST']='localhost'
    broker['PORT']=1883
    test['BROKER']=broker
    t = tree(test)

    bus.msgbus_publish('CONFIG',t)
    time.sleep(1)
    bus.msgbus_publish('NOTIFY',test)
