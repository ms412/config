
import time
import os
import paho.mqtt.client as mqtt

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

        self.setup(self._config)

    def __del__(self):
        self._mqttc.disconnect()

    def setup(self,config):
        print ('Setup mqtt')

        '''
        create mqtt session
        '''
        #self.create()
        self._mqttc = mqtt.Client(str(os.getpid()))

        '''
        setup callbacks
        '''
        self._mqttc.on_message = self.on_message
        self._mqttc.on_connect = self.on_connect
        self._mqttc.on_publish = self.on_publish
        self._mqttc.on_subscribe = self.on_subscribe
        self._mqttc.on_disconnect = self.on_disconnect

        '''
        broker Configuration
        '''

        self.msgbus_publish('LOG','%s start broker with configuration %s '%('INFO', config))

        self._host = str(config.get('HOST','localhost'))
        self._port = int(config.get('PORT',1883))
        temp = str(config.get('SUBSCRIBE','/SUBSCRIBE'))
        self._subscribe = temp.split(",")

        self._publish = str(config.get('PUBLISH','/PUBLISH'))

        '''
        start broker
        '''
        self.connect()
        self.subscribe()
        return True

    def tx_data(self,message):
        self.publish(message)
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
        print('MQTT: connect to host:', self._host,str(rc))
        self._connectState = True
        self.msgbus_publish('LOG','%s Broker: Connected %s'%('INFO', self._connectState))

        return True

    def on_disconnect(self, client, userdata, rc):
        print('Mqtt Disconnect', rc)
        self._connectState = False
        if rc != 0:
            conn_state = 'Unexpected'
            self.msgbus_publish('LOG','%s Broker: Lost Connection to MQTT:%s '%('INFO',conn_state))
            self._mqttc.connect(self._host, self._port, 60)

        return 0

    def on_message(self, client, userdata, msg):
        print('Mqtt received: ',msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        message ={}

        list_topic = msg.topic.split("/")
        message.update({'CHANNEL':list_topic[-2]})
        message.update({'PORT_NAME':list_topic[-1]})
        message.update({'MESSAGE':msg.payload})
        self.msgbus_publish('LOG','%s Broker: received Date Device: %s , Port: %s , Message: %s'%('INFO',message['CHANNEL'], message['PORT_NAME'], message['MESSAGE']))
        self._rxQueue.put(message)
        return 0

    def on_publish(self, client, userdata, mid):
        print('MQTT on_published '+str(mid))
        return 0

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print('MQTT: Subscribed: '+str(mid)+' '+str(granted_qos))
        return 0

    def create(self):
        print('mqtt create mqtt object')
        self._mqttc = mqtt.Client(str(os.getpid()))
        return True

    def reinitialise(self):
        print('mqtt reinitialise')
        self._mqttc.reinitialise(str(os.getpid()), clean_session=True)
        return True

    def connect(self):
        print ('mqtt connected')
        #self._mqttc.connect('localhost')

        self._mqttc.connect(self._host, self._port,60)
        self._mqttc.loop_start()
        return True

    def disconnect(self):
        print('dissconnect')
        self._mqttc.disconnect()

    def subscribe(self,channel = None):
        if not channel:
            for item in self._subscribe:
                self._mqttc.subscribe(item + str('/#'),0)
                print('mqtt subscribe',item)

        else:
            print('mqtt subscribe by commandline',channel)
            self._mqttc.subscribe(channel,0)

        return True


    def publish(self,message):
        print('Publish:',message)
     #   self._mqttc.publish(message)
        self._mqttc.publish(self._publish, message, 0)


if __name__ == "__main__":

    config = {'HOST':'localhost','PUBLISH':'/TEST','SUBSCRIBE':'/TEST'}
    broker = mqttbroker(config)
    time.sleep(2)
    broker.tx_data('hhdhdhdhdhd')
    time.sleep(1)
    counter = 5
    loopcounter = 0
    loop = True
    while loop:
        data = broker.rx_data()
        print ('Loop:', loopcounter, 'DATA:',data)

        time.sleep(0.5)
        if counter > loopcounter:
            print ('TRUE')
            loop = True
            loopcounter = loopcounter + 1
        else:
            loop = False
            print ('FALSE')