
import time
import os
import library.libpaho as mqtt
#import paho.mqtt.client as mqtt

from queue import Queue
from library.libmsgbus import msgbus


class mqttbroker(msgbus):

    def __init__(self,config):
        '''
        setup mqtt broker
        config = dictionary with configuration
        '''

        self._config = config

        '''
        broker object
        '''
        self._mqtt = ''

        '''
        Transmit and Receive Queues objects
        '''
        self._rxQueue = Queue()

        print('MQTT: Init Mqtt object Startup', self)

        '''
        create mqtt session
        '''
        #self.create()
        #self._mqttc = mqtt.Client(str(os.getpid()))

        self.setup(self._config)

    def __del__(self):
        print("Delete libmqttbroker")
        self._mqttc.disconnect()

    def restart(self,config):
        print('MQTT::restart')
        time.sleep(1)
        self.unsubscribe()
        self.disconnect()
        self.setup(config)
        time.sleep(1)
        self.reinitialise()
        time.sleep(1)
        self.start()

        return True

    def start(self):
        print('MQTT::start')
        '''
        start broker
        '''
        self._mqttc=self.create()
        self.callback()
        self.connect(self._host,self._port)
        for item in self._subscribe:
            self.subscribe(item)

        return True

    def callback(self):
        '''
        setup callbacks
        '''
        self._mqttc.on_message = self.on_message
        self._mqttc.on_connect = self.on_connect
        self._mqttc.on_publish = self.on_publish
        self._mqttc.on_subscribe = self.on_subscribe
        self._mqttc.on_disconnect = self.on_disconnect
        self._mqttc.on_log = self.on_log
        return True

    def setup(self,config):
        print ('MQTT::Setup libmqttbroker:',self._config)

        '''
        setup callbacks
        '''
     #   self._mqttc.on_message = self.on_message
      #  self._mqttc.on_connect = self.on_connect
      #  self._mqttc.on_publish = self.on_publish
      #  self._mqttc.on_subscribe = self.on_subscribe
      #  self._mqttc.on_disconnect = self.on_disconnect
      #  self._mqttc.on_log = self.on_log

        '''
        broker Configuration
        '''

       # self.msgbus_publish('LOG','%s start broker with configuration %s '%('INFO', config))

        self._host = str(config.get('HOST','localhost'))
        self._port = int(config.get('PORT',1883))
        #temp = str(config.get('SUBSCRIBE','/SUBSCRIBE'))
        #self._subscribe = temp.split(",")

        self._subscribe = config.get('SUBSCRIBE',None)

        self._publish = str(config.get('PUBLISH','/PUBLISH'))

        '''
        start broker
        '''
    #    self.connect(self._host,self._port)
     #   for item in self._subscribe:
      #      self.subscribe(item)
        return True

    def run(self):
        self._mqttc.loop_start()

    def tx_data(self,message):
        self.publish(message)
        print('Transmitt message,',message)

        return True

    def rx_data(self):

        if not self._rxQueue.empty():
            msg = self._rxQueue.get()
            message = msg.get('MESSAGE',None)
            channel = msg.get('CHANNEL',None)
        else:
            message = None
            channel = None

        return (message,channel)


    def on_connect(self, client, userdata, flags, rc):
        print('MQTT:: connect to host:', self._host,str(rc))
        self._connectState = True
        self.msgbus_publish('LOG','%s Broker: Connected %s'%('INFO', self._connectState))

        return True

    def on_disconnect(self, client, userdata, rc):
        print('Mqtt:: Disconnect', userdata, rc)
    #    self._connectState = False
     #   if rc != 0:
      #      conn_state = 'Unexpected'
       #     self.msgbus_publish('LOG','%s Broker: Lost Connection to MQTT:%s '%('INFO',conn_state))
        #    self._mqttc.connect(self._host, self._port, 60)

        return True

    def on_message(self, client, userdata, msg):
    #    print('Mqtt received: ',msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        message ={}
       # print('RECEIVE',msg.topic, msg.payload)
        #list_topic = msg.topic.split("/")
        message.update({'CHANNEL':msg.topic})
        message.update({'MESSAGE':msg.payload})
        print('Receive',message)
      #  self.msgbus_publish('LOG','%s Broker: received Date Device: %s , Port: %s , Message: %s'%('INFO',message['CHANNEL'], message['PORT_NAME'], message['MESSAGE']))
        self._rxQueue.put(message)
        return True

    def on_publish(self, client, userdata, mid):
        print('MQTT on_published '+str(mid))
        return True

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print('MQTT: on_subscribe: '+str(userdata)+' '+str(granted_qos))
        return True

    def on_unsubscribe(self, client, userdata, mid):
        print('MQTT:: unsubscribe',client, userdata,mid)
        return True

    def on_log(self, client, userdata, level, buf):
        '''
        Test
        :param client:
        :param userdata:
        :param level:
        :param buf:
        :return:
        '''
        print('MQTT: Log',client, userdata, level, buf)
        return True

    def create(self):
        print('mqtt create mqtt object')
        return mqtt.Client(str(os.getpid()))
   #     return True

    def reinitialise(self):
        print('mqtt reinitialise')
        self._mqttc.reinitialise(str(os.getpid()), clean_session=True)

        return True

    def connect(self,host,port):
      #  print ('mqtt connected')
        #self._mqttc.connect('localhost')

        self._mqttc.connect(host, port,60)
        self._mqttc.loop_start()
        return True

    def disconnect(self):
        print('dissconnect')
        self._mqttc.disconnect()
        return True

    def subscribe(self,channel = None):
      #  if not channel:
       #for item in self._subscribe:
        #    print('Subscribe',item)
        self._mqttc.subscribe(channel,0)
        return True

    def unsubscribe(self):
        self._mqttc.unsubscribe(self._subscribe)
        return True

    def publish(self,message):

      #        message.update({'CHANNEL':msg.topic})
       # message.update({'MESSAGE':msg.payload})
       # print('Receive',message)
        #print('Publish:',message)
     #   self._mqttc.publish(message)
        self._mqttc.publish(message.get('CHANNEL'), message.get('MESSAGE'), 0)
        return True

if __name__ == "__main__":

    config1 = {'HOST':'192.168.1.107','PUBLISH':'/TEST','SUBSCRIBE':['/TEST/#','/TEST2']}
    config2 = {'HOST':'192.168.1.107','PUBLISH':'/TEST','SUBSCRIBE':['/TEST1/#','/TEST3','/TEST4']}
    msg = {'CHANNEL':'/TTT','MESSAGE':'{ioioookko}'}
    broker = mqttbroker(config1)
  #  broker = setup(config)
    broker.start()

#    broker.connect()
 #   broker.subscribe()
    time.sleep(10)
    broker.restart(config2)
    time.sleep(10)

    while True:
        time.sleep(10)
        broker.publish(msg)
   # time.sleep(2)