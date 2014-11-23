
import json

from queue import Queue

from library.libmsgbus import msgbus


class messagebroker(msgbus):

    def __init__(self):

        '''
        Setup message Queues
        '''
        self.dataRx_queue = Queue()

        self.setup()
        print('INIT Messagebroker')

    def run(self):

        print('RUN messagebroker')
        while not self.dataRx_queue.empty():
                self.on_data_rx(self.dataRx_queue.get())



    def setup(self):
        ''''
        setup message pipes
        '''

        self.msgbus_subscribe('DATA_RX', self._on_data_rx)


    def _on_data_rx(self,msg):
        self.dataRx_queue.put(msg)
        return

    def on_data_rx(self,msg):
        msg = self._json2dict(msg.payload)
        msg_header = msg.get('MESSAGE',None)
        if msg_header:
            msg_type = msg_header.get('TYPE',None)

            if msg_type == 'CONFIG':
                msg_mode = msg_header.get('MODE',None)
                if msg_mode == 'ADD':
                    self.msgbus_publish('CFG_ADD',msg)
                elif msg_mode == 'DEL':
                    self.msgbus_publish('CFG_DEL',msg)
                else:
                    self.msgbus_publish('CFG_NEW',msg)

            elif msg_type == 'REQUEST':
                self.msgbus_subscribe('REQ_MSG',msg)

            else:
                print('Not found',msg)


    def _json2dict(self,j_data):
        return json.loads(j_data.decode('utf8'))[0]