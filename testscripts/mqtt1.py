import os
import json
import time
#import paho.mqtt.client as mqtt
import library.libpaho as mqtt

# Define event callbacks
def on_connect(mosq, obj, rc):
    print("rc: " + str(rc))

def on_message(mosq, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)

mqttc = mqtt.Client()
# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Uncomment to enable debug messages
#mqttc.on_log = on_log

# Parse CLOUDMQTT_URL (or fallback to localhost)
#url_str = os.environ.get('CLOUDMQTT_URL', 'mqtt://localhost:1883')
#url = urlparse.urlparse(url_str)

# Connect
#mqttc.username_pw_set(url.username, url.password)
mqttc.connect('192.168.1.107', 1883)

# Start subscribe, with QoS level 0
#mqttc.subscribe("hello/world", 0)
def _dict2json(self,dict):
    # return str(dict)
    return json.dumps(dict)

header_add = {'MESSAGE':{'TYPE':'CONFIG','MODE':'ADD'},'DEVICES':{'DEV1':{'PORT1':{'123':45,'PI':'878'}}}}
header_del = {'MESSAGE':{'TYPE':'CONFIG','MODE':'DEL'},'DEVICES':{'DEV1':{'PORT1':{'123':45,'PI':'878'}}}}
header_new = {'MESSAGE':{'TYPE':'CONFIG','MODE':'NEW'},'DEVICES':{'DEV1':{'PORT1':{'123':45,'PI':'878'}}}}
header_req = {'MESSAGE':{'TYPE':'REQUEST'},'DEVICES':{'DEV1':{'PORT1':{'123':45,'PI':'878'}}}}
openhab_set = {'SET':'123','MODE':'632'}
openhab_req = {'123':45,'PI':'878'}
openhab_on = {'TYPE':'SET','COMMAND':'ON'}
openhab_off = {'TYPE':'SET','COMMAND':'OFF'}
dict = {}
dict['TEST']='HELP'
dict['MESSAGE']='1234'
# Publish a message
print('Dict',dict,json.dumps(dict))
#mqttc.publish("/GPIO1/CONFIG", json.dumps(header_add),0)
#time.sleep(3)
#mqttc.publish("/GPIO1/CONFIG/ii", json.dumps(openhab_on),0)
time.sleep(3)
mqttc.publish("/GPIO1/MCP23017_2/Port9", json.dumps(openhab_off),0)
#time.sleep(3)
#mqttc.publish("/TEST/CONFIG", json.dumps(header_req),0)
#time.sleep(3)
#mqttc.publish("/XXX/DEVICEn/PORTn", json.dumps(openhab_set),0)

# Continue the network loop, exit when an error occurs
#rc = 0
#while rc == 0:
#    rc = mqttc.loop()
#print("rc: " + str(rc))