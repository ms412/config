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
        self._sub_channel = '/OPENHAB'
        self._pub_channel = '/GPIO1'

        self._mqttc = mqtt.Client(str(os.getpid()))

        '''
        Setup callbacks
        '''
        self._mqttc.on_message = self.mqtt_on_message
        self._mqttc.on_connect = self.mqtt_on_connect
        self._mqttc.on_publish = self.mqtt_on_publish
        self._mqttc.on_subscribe = self.mqtt_on_subscribe

        self.connect()
        self.subscribe()

    def mqtt_on_connect(self,mosq,obj,flags,rc):
        print('MQTT: connect to host:', self._host,str(rc))
        return True

    def mqtt_on_subscribe(self,mosq,obj,mid,granded_qos):
        print ('MQTT: subscribe to channel', self._sub_channel,str(mid))
        return True

    def mqtt_on_publish(self,mosq,obj,mid):
        print ('MQTT: publish message the channel', self._pub_channel,str(mid))
        return True

    def mqtt_on_message(self,mqtt,obj,msg):
        print('MQTT: message received:',msg.topic,msg.payload)
        return True

    def connect(self):
        print ('Connect')
        self._mqttc.connect(self._host, self._port)
        self._mqttc.loop_start()

    def subscribe(self):
        self._mqttc.subscribe(self._sub_channel,0)

    def publish(self,channel, message):
        self._mqttc.publish(channel, message, 0)


def binout_toggle():
    on = {'TYPE':'SET','COMMAND':'ON'}
    off = {'TYPE':'SET','COMMAND':'OFF'}
    broker.publish("/GPIO1/MCP23017_2/Port9", json.dumps(on))
    time.sleep(5)
    broker.publish("/GPIO1/MCP23017_2/Port9", json.dumps(off))
    time.sleep(5)
    return True

def binout_add():
    msg_add_binout = {'MESSAGE':{'TYPE':'CONFIG','MODE':'ADD'},'DEVICES':{'MCP23017_2':{'Port12':{'HWID':12,'MODE':'BINARY-OUT','OFF_VALUE':'AAA','ON_VALUE':'BBB','INITIAL':'AAA'}}}}
    broker.publish("/GPIO1/CONFIG", json.dumps(msg_add_binout))
    time.sleep(5)
    msg_set1 = {'TYPE':'SET','COMMAND':'BBB'}
    broker.publish("/GPIO1/MCP23017_2/Port12", json.dumps(msg_set1))
    time.sleep(5)
    msg_set2 = {'TYPE':'SET','COMMAND':'AAA'}
    broker.publish("/GPIO1/MCP23017_2/Port12", json.dumps(msg_set2))
    time.sleep(5)
    msg_del_binout2 = {'MESSAGE':{'TYPE':'CONFIG','MODE':'DEL'},'DEVICES':{'MCP23017_2':{'Port12':''}}}
    broker.publish("/GPIO1/CONFIG", json.dumps(msg_del_binout2))
    time.sleep(5)

def lcd_write():
    rest_lcd = {'TYPE':'SET','COMMAND':'RESET'}
    msg_lcd = {'TYPE':'SET','COMMAND':'MESSAGE','MESSAGE':'TEST'}
    broker.publish("/GPIO1/I2C_x26/LCD-01",json.dumps(msg_lcd))
    time.sleep(5)

if __name__ == '__main__':
    #ADD MQTT Broker
   # MSG = {'MESSAGE':{'TYPE':'CONFIG','MODE':'ADD'},'BROKER':{'HOSTS':'localhost','PORTE':1883}}
    msg_get1 = {'MESSAGE':{'TYPE':'REQUEST'},'DEVICES':{'MCP23017_2':{'Port1':{'TYPE':'GET','COMMAND':'GET'}}}}

    msg_set11 = {'MESSAGE':{'TYPE':'REQUEST'},'DEVICES':{'MCP23017_2':{'Port9':{'TYPE':'SET','COMMAND':'ON'}}}}
    msg_set12 = {'MESSAGE':{'TYPE':'REQUEST'},'DEVICES':{'MCP23017_2':{'Port9':{'TYPE':'SET','COMMAND':'OFF'}}}}

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
    time.sleep(3)
  #  binout_toggle()
   # binout_add()
    lcd_write()




