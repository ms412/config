import json
import time
from queue import Queue
from threading import Thread

from library.libmsgbus import msgbus
from library.libtree import tree
from library.libmqttbroker import mqttbroker

class interpreter(Thread,msgbus):

    def __init__(self):
        Thread.__init__(self)

        self._mqttbroker = None

        '''
        Setup message Queues
        '''
        self._configQ = Queue()
        self._notifyQ = Queue()
       # self._msg_rxQ = Queue()
        print('Init messagebroker object')
        self.cfg = {'BROKER':{'HOST':'192.168.1.107','PORT':'1883','SUBSCRIBE':'/INTERPRETER','PUBLISH':'/OPENHAB'}}


    def run(self):

        self.setup()

        threadRun = True

        self.on_config(self.cfg)

        while threadRun:
            print('run')

            time.sleep(1)

        return True

    def setup(self):
        ''''
        setup message pipes
        '''
        self.msgbus_subscribe('DATA_TX', self._on_notify)
        return True

    def _on_notify(self,msg):
     #   print('TTTTTTTTTTTTTTTTTT')
        self._notifyQ.put(msg)
        return True

    def on_config(self,cfg_msg):
        broker = cfg_msg.get('BROKER')
        if not self._mqttbroker:
            print('Messagebroker:: initial startup')
            self._mqttbroker = mqttbroker(broker)
            #print ('MEssagebroker: start new MQTT ',self._mqttbroker)
        else:
            print ('MEssagebroker: New Configuration available restart broker',self._mqttbroker)
            self._mqttbroker.reconfig(broker)
            #del self._mqttbroker
            #time.sleep(0.5)
            #self._mqttbroker = mqttbroker(broker.getTree())
          #  print ('MEssagebroker: start new MQTT with updated ',self._mqttbroker)
        return True



if __name__ == "__main__":
    inter = interpreter()
    inter.start()