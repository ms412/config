
import time
import os

from threading import Thread, Lock
from queue import Queue

#import paho.mqtt.client as mqtt

try:
    import paho.mqtt.client as mqtt
except:
    import paho as mqtt
    print ('start local mqtt driver')

from library.libmsgbus import msgbus


class mqtt_adapter(Thread,msgbus):

    def __init__(self):
        Thread.__init__(self)

        print('init mqtt adapter')

        self.cfg_queue = Queue()
        self.log_queue = Queue()

        self.cfgQueue = Queue()
        self.dataRxQueue = Queue()
        self.dataTxQueue = Queue()

        self.mqttRxQu = Queue()

        '''
        creaste mqtt object
        '''
        self._mqttc = mqtt.Client(str(os.getpid()))

        self._host = str('iot.eclipse.org')
        self._port = int(1883)
        self._subscribe = []
      #  self._subscribe = str('/RECEIVER')
        self._publish = ''
        self._config = ''

        self._connectState = False





    def run(self):

        self.setup()
        #self.connect()
        self.msgbus_publish('LOG','%s Broker Thread Startup '%('INFO'))

        threadRun = True

        while threadRun:

          #  time.sleep(2)


            while not self.cfg_queue.empty():
                self.on_cfg(self.cfg_queue.get())

            while not self.dataTxQueue.empty():
                temp = self.dataTxQueue.get()
                self.publish(str(temp.get('MESSAGE',None)))
            print('mqtt loop', self._connectState)

            if self._connectState:
                self.publish('The quick brown fox jumps over the lazy dog')

            time.sleep(2)
      #      self.mqttc.loop()
        return


    def setup(self):
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

        print('Broker init')
        '''
        setup message pipes
        '''
        self.msgbus_subscribe('CONF', self._on_cfg)
        self.msgbus_subscribe('DATA',self._on_data)
#        self.msgbus_subscribe('NBI', self._on_data)
        return




    def _on_cfg(self,cfg_msg):
        print('mqtt config data arived')
        self.cfg_queue.put(cfg_msg)
        return

    def _on_data(self,msg):
        self.dataTxQueue.put(msg)
        return

    def on_cfg(self,cfg_msg):

        print('broker configuratio update on_cfg')
        broker = cfg_msg.select('BROKER')
        self.msgbus_publish('LOG','%s Broker Received new configuration %s '%('INFO', broker.getTree()))

        self._host = str(broker.getNode('HOST','localhost'))
        self._port = int(broker.getNode('PORT',1883))
        temp = str(broker.getNode('SUBSCRIBE','/SUBSCRIBE'))
        self._subscribe = temp.split(",")
       # self._subscribe.append(str(broker.getNode('CONFIG','/CONFIG')))
        self._publish = str(broker.getNode('PUBLISH','/PUBLISH'))



      #  self.disconnect()
       # self.reinitialise()
        self.connect()
        self.subscribe()

        return

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
            self.mqttc.connect(self.host, self.port, 60)

        return 0

    def on_message(self, client, userdata, msg):
        print('Mqtt received: ',msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        resultDict ={}

        list_topic = msg.topic.split("/")
        resultDict.update({'DEVICE_NAME':list_topic[-2]})
        resultDict.update({'PORT_NAME':list_topic[-1]})
        resultDict.update({'MESSAGE':msg.payload})

        #print ('device name', resultDict['DEVICE_NAME'],'Port name:', resultDict['PORT_NAME'],'message', resultDict['MESSAGE'])
        self.msgbus_publish('LOG','%s Broker: received Date Device: %s , Port: %s , Message: %s'%('INFO',resultDict['DEVICE_NAME'], resultDict['PORT_NAME'], resultDict['MESSAGE']))
 #       self.mqttRxQu.put(resultDict)
 #       self.publish('NBI','test')
        self.msgbus_publish('DATA_RX',msg)
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
        print ('Conn3ect')
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
        self._mqttc.publish(self._publish, message, 0)






