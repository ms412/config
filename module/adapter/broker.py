
import time
import os

from threading import Thread, Lock
from queue import Queue

import paho.mqtt.client as mqtt

from library.libmsgbus import msgbus


class mqttClient(Thread,msgbus):

    def __init__(self):
        Thread.__init__(self)

        self.cfgQueue = Queue()
        self.dataRxQueue = Queue()
        self.dataTxQueue = Queue()

        self.mqttRxQu = Queue()

        self.mqttc = ''


        self.host = str('iot.eclipse.org')
        self.port = int(1883)
        self.topic = str('$SYS/#')
        self.publish = str('/OPENHAB02')

    def run(self):

        print ('run mqtt')

        self.setup()

        threadRun = True

        while(threadRun == True):
            #print('loop mqtt')
            try:
                self.msgObj = self.cfgQueue.get_nowait()
                print('MQTT Config available',self.msgObj)
                self.msgHeader()
            except:
                threadRun = True
            #    print ('MQTT Queu Empty')
           # time.sleep(1)
            self.mqttc.loop()
        return


    def setup(self):

        print ('SEtup mqtt')

        self.mqttc = mqtt.Client(str(os.getpid()))

        self.mqttc.connect(self.host, self.port, 60)
        self.mqttc.subscribe(self.topic, 0)

        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_subscribe = self.on_subscribe
        self.mqttc.on_disconnect = self.on_disconnect

        self.msgbus_subscribe('NBI', self._on_data)

    def on_connect(self, mqttc, obj, rc):
        print('Mqtt Connected', str(rc))

    def on_disconnect(self, rc):
        print('Mqtt Disconnect', rc)
        self.mqttc.connect(self.host, self.port, 60)
        return 0

    def on_message(self, mqttc, obj, msg):
        print('Mqtt received: ',msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        resultDict ={}

        list_topic = msg.topic.split("/")
        resultDict.update({'DEVICE_NAME':list_topic[-2]})
        resultDict.update({'PORT_NAME':list_topic[-1]})
        resultDict.update({'PORT_STATE':msg.payload})

 #       self.mqttRxQu.put(resultDict)
 #       self.publish('NBI','test')
        self.msgBus_publish('NBI',resultDict)
        return 0

    def on_publish(self, mqttc, obj, mid):
        print("Mqtt published "+str(mid))
        return 0

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))
        return 0

    def mqtt_send(self,msgDict):
        self._sendQueue.put(msgDict)

    def mqtt_publish(self,msg,channel=None):

        if channel is None:
            channel = self._mqtt_pub_ch

        channel = str(self._mqtt_pub_ch +'/' + channel)

        self._loghandle.info('MqttWrapper::Publish to Channel: %s Message: %s',channel, msg)
        self._mqttc.publish(channel, msg)

        return True



    def on_config(self,message):

   #     print ('Receive mqtt config',message)

        item = message.get('BROKER',None)
        if None not in item:
            print ('Write in mqtt Queue')
            self.cfgQueue.put(item)

       # print ('BROKER message',item)

        return

    def on_dataRx(self,message):


        self.msgObj = self.dataRxQueue.get_nowait()
        self.publish('DATA_TX',self.msgObj)

        return

    def on_dataTx(self,message):

        item = message.get('DEVICES',None)
        if None not in item:
            print ('Write in mqtt DataTx Queue')
            self.dataTxQueue.put(item)
        return

    def _on_data(self,msg):
        print ('her',msg)

