import os
import time
import json

try:
    import paho.mqtt.client as mqtt
except:
    import paho as mqtt
    print ('start local mqtt driver')

class mqttclient(object):

    def __init__(self):

        self._host = '192.168.1.107'
        self._port = 1883
        self._sub_channel = '/subscribe'
        self._pub_channel = '/publish'

        self._mqttc = mqtt.Client(str(os.getpid()))

        '''
        Setup callbacks
        '''
        self._mqttc.on_message = self.mqtt_on_message
        self._mqttc.on_connect = self.mqtt_on_connect
        self._mqttc.on_publish = self.mqtt_on_publish
        self._mqttc.on_subscribe = self.mqtt_on_subscribe
        #self._mqttc.on_disconnect = self.mqtt_on_disconnect
        print('INIT')

    def mqtt_on_connect(self,mosq,obj,flags,rc):
        print('MQTT: connect to host:', self._host,str(rc))
        return True

    def mqtt_on_subscribe(self,mosq,obj,mid,granded_qos):
        print ('MQTT: subscribe to channel', self._sub_channel,str(mid))
        return True

    def mqtt_on_publish(self,mosq,obj,mid):
        print ('MQTT: publish message th channel', self._pub_channel,str(mid))
        return True

    def mqtt_on_message(self,mqtt,obj,msg):
        print('MQTT: message received:',msg.topic,msg.payload)
        return True

    def sethost(self,host):
        self._host = host
        return True

    def setport(self,port):
        self._port = port
        return True

    def setsubchannel(self,sub_channel):
        self._sub_channel = sub_channel
        return True

    def setpubchannel(self,pub_channel):
        self._pub_channel = pub_channel
        return True

    def connect(self):
        print ('Connect')
        self._mqttc.connect(self._host, self._port)

    def subscribe(self):
        self._mqttc.subscribe(self._sub_channel,0)

    def publish(self,message):
        self._mqttc.publish(self._pub_channel, message, 0)

    def loop(self):
        return self._mqttc.loop()


if __name__ == '__main__':
   # MSG = {'MESSAGE':{'TYPE':'CONFIG','MODE':'ADD'},'BROKER':{'HOSTS':'localhost','PORTE':1883}}
   # MSG = {'MESSAGE':{'TYPE':'REQUEST'},'DEVICES':{'MCP23017_2':{'Port1':{'TYPE':'GET'}}}}
    MSG = {'MESSAGE':{'TYPE':'REQUEST'},'DEVICES':{'MCP23017_2':{'Port9':{'TYPE':'SET','COMMAND':'ON'}}}}

    msgStr = json.dumps(MSG)

    broker = mqttclient()
    broker.setpubchannel('/GPIO_1')
    broker.setsubchannel('/RECEIVER')
    broker.connect()
    broker.subscribe()
    broker.publish(msgStr)

    rc= 0
    while rc == 0:
        rc = broker.loop()
    print("rc:", str(rc))