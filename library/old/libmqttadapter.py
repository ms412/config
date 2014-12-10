import time
import os


from queue import Queue
from threading import Thread, Lock
from library.libmsgbus import msgbus

try:
    import paho.mqtt.client as mqtt
except:
    import paho as mqtt
    print ('start local mqtt driver')


class mqtt_adapter(msgbus):

    def __init__(self):

        '''
        setup queues
        '''
        self._receiveQ = Queue()
        self._transmittQ = Queue()

        '''
        creaste mqtt object
        '''
        self._mqttc  = ''
        self.create()

        '''
        setup callbacks
        '''
        self._mqttc.on_message = self.on_message
        self._mqttc.on_connect = self.on_connect
        self._mqttc.on_publish = self.on_publish
        self._mqttc.on_subscribe = self.on_subscribe
        self._mqttc.on_disconnect = self.on_disconnect

        '''
        default configuration
        '''
        self._host = str('iot.eclipse.org')
        self._port = int(1883)
        self._subscribe = []
        self._publish = []

        self.msgbus_publish('LOG','%s MQTT Adapter initialisation object finished'%('DEBUG'))


    def config(self,cfg_msg=None):

        broker = cfg_msg.select('BROKER')
        self.msgbus_publish('LOG','%s MQTT Adapter received configuration update %s '%('DEBUG', broker.getTree()))

        self._host = str(broker.getNode('HOST','iot.eclipse.org'))
        self._port = int(broker.getNode('PORT',1883))
        temp = str(broker.getNode('SUBSCRIBE','/SUBSCRIBE'))
        self._subscribe = temp.split(",")
        temp = str(broker.getNode('PUBLISH','/PUBLISH'))
        self._publish = temp.split(",")

        self.disconnect()
        self.connect()
        self.subscribe()

        return True

    def receiveQ(self):
        item =''
        if not self._receiveQ.empty():
            item = self._receiveQ.get()
        return item


    def on_connect(self, client, userdata, flags, rc):
        print('MQTT: connect to host:', self._host,str(rc))
        self._connectState = True

        self.msgbus_publish('LOG','%s Broker: Connected %s'%('INFO', self._connectState))

        return True

    def on_disconnect(self, client, userdata, rc):
        print('Mqtt::on_disconnect', rc, userdata)
        self._connectState = False
        if rc != 0:
            conn_state = 'Unexpected'
            self.msgbus_publish('LOG','%s Broker: Lost Connection to MQTT:%s '%('INFO',conn_state))
            self._mqttc.connect(self._host, self._port, 60)

        return True

    def on_message(self, client, userdata, msg):

        msg_dict ={}
        list_topic = msg.topic.split("/")
        msg_dict.update({'DEVICE_NAME':list_topic[-2]})
        msg_dict.update({'PORT_NAME':list_topic[-1]})
        msg_dict.update({'MESSAGE':msg.payload})

        self._receiveQ.put(msg_dict)
        self.msgbus_publish('LOG','%s Broker: received Date Device: %s , Port: %s , Message: %s'%('DEBUG',msg_dict['DEVICE_NAME'], msg_dict['PORT_NAME'], msg_dict['MESSAGE']))
        return True

    def on_publish(self, client, userdata, mid):
        print('MQTT on_published '+str(mid))
        return True

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print('MQTT: Subscribed: '+str(mid)+' '+str(granted_qos)+ ' ' +str(userdata)+ ' ' +str(client))
        return True

    def create(self):
        print('mqtt::create')
        self._mqttc = mqtt.Client(str(os.getpid()))
        return True

    def reinitialise(self):
        self._mqttc.reinitialise(str(os.getpid()), clean_session=True)
        return True

    def connect(self):
        print ('mqtt::connect')
        self._mqttc.connect(self._host, self._port,60)
        self._mqttc.loop_start()
        return True

    def disconnect(self):
        print('mqtt::dissconnect')
        self._mqttc.disconnect()
        return True

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
        print('Message',type(message),message)
        for item in self._publish:
          #  message = 'TEST'
            self._mqttc.publish(item, message, 0)
        return True






