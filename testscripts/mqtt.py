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
    #ADD MQTT Broker
   # MSG = {'MESSAGE':{'TYPE':'CONFIG','MODE':'ADD'},'BROKER':{'HOSTS':'localhost','PORTE':1883}}
    msg_get1 = {'MESSAGE':{'TYPE':'REQUEST'},'DEVICES':{'MCP23017_2':{'Port1':{'TYPE':'GET','COMMAND':'GET'}}}}

    msg_add_binout1 = {'MESSAGE':{'TYPE':'CONFIG','MODE':'ADD'},'DEVICES':{'MCP23017_2':{'Port12':{'HWID':12,'MODE':'BINARY-OUT','OFF_VALUE':'AAA','ON_VALUE':'BBB','INITIAL':'AAA'}}}}
    msg_set1 = {'MESSAGE':{'TYPE':'REQUEST'},'DEVICES':{'MCP23017_2':{'Port12':{'TYPE':'SET','COMMAND':'BBB'}}}}
    msg_set2 = {'MESSAGE':{'TYPE':'REQUEST'},'DEVICES':{'MCP23017_2':{'Port12':{'TYPE':'SET','COMMAND':'AAA'}}}}
    msg_del_binout2 = {'MESSAGE':{'TYPE':'CONFIG','MODE':'DEL'},'DEVICES':{'MCP23017_2':{'Port12':''}}}

    #ADD configuration
    msg_add1 = {'MESSAGE':{'TYPE':'CONFIG','MODE':'ADD'},'DEVICES':{'MCP23017_2':{'Port5':{'HWID':5,'MODE':'BINARY-IN','INTERVAL':30}}}}
    msg_del1 = {'MESSAGE':{'TYPE':'CONFIG','MODE':'DEL'},'DEVICES':{'MCP23017_2':{'Port5':'','Port9':''}}}
    msg_del2 = {'MESSAGE':{'TYPE':'CONFIG','MODE':'DEL'},'DEVICES':{'MCP23017_2':{'Port5':''}}}
    msg_add2 = {'MESSAGE':{'TYPE':'CONFIG','MODE':'ADD'},'DEVICES':{'MCP23017_1':{'Port8':{'HWID':8,'MODE':'BINARY-IN','INTERVAL':30},'SYSTEM':'RASPBERRY_B1','I2C_ADDRESS':'0x20','TYPE':'MCP23017','UPDATE':5}}}

    msg_add_trigger1 = {'MESSAGE':{'TYPE':'CONFIG','MODE':'ADD'},'DEVICES':{'MCP23017_2':{'Port10':{'HWID':10,'MODE':'TRIGGER','PULS_LENGTH':30,'OFF_VALUE':'0','ON_VALUE':'1','INITIAL':'1'}}}}
    msg_trigger1 = {'MESSAGE':{'TYPE':'REQUEST'},'DEVICES':{'MCP23017_2':{'Port10':{'TYPE':'SET','COMMAND':'0'}}}}
    msg_trigger2 = {'MESSAGE':{'TYPE':'REQUEST'},'DEVICES':{'MCP23017_2':{'Port10':{'TYPE':'SET','COMMAND':'0','PULS_LENGTH':'10'}}}}
    msg_del_trigger1 = {'MESSAGE':{'TYPE':'CONFIG','MODE':'DEL'},'DEVICES':{'MCP23017_2':{'Port10':''}}}
  # msgStr = json.dumps(MSG)

    broker = mqttclient()
    broker.setpubchannel('/GPIO_1')
    broker.setsubchannel('/RECEIVER')
    broker.connect()
    broker.subscribe()

  #  input('Press Enter for add command..')
    #broker.publish(json.dumps(msg_add))

   # input('Press Enter for delete command..')
    broker.publish(json.dumps(msg_add_binout1))
    time.sleep(10)
    broker.publish(json.dumps(msg_set1))
    time.sleep(20)
    broker.publish(json.dumps(msg_set2))
    time.sleep(10)
    broker.publish(json.dumps(msg_set1))
    time.sleep(20)
    broker.publish(json.dumps(msg_add_binout1))

    rc= 0
    while rc == 0:
        rc = broker.loop()
    print("rc:", str(rc))