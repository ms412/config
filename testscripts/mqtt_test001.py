#!/usr/bin/python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


__app__ = "mqtt2gpio Adapter"
__VERSION__ = "0.8"
__DATE__ = "01.12.2014"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2014 Markus Schiesser"
__license__ = 'GPL v3'

import sys
import time

from library.libmsgbus import msgbus
from module.adapter.config import configmodule
from module.adapter.logging import log_adapter
from module.adapter.messagebroker import msgbroker
from module.manager.vhm import vhm


class manager(msgbus):

    def __init__(self,cfg_file='config.yaml'):

        self._cfg_file = cfg_file

        self._cfg_root_handle = None
        self._cfg_general_handle = None
        self._cfg_broker_handle = None
        self._cfg_device_hanlde = None
        self._msgbroker = None

        self._log_handle = None


    def start_config(self):
        print('Start Configuration',self._cfg_file)
        self._cfg_thread = configmodule(self._cfg_file)
        self._cfg_thread.start()

    def start_logging(self):
        print('Debug Logging1')
        self._log_thread = log_adapter()
        self._log_thread.start()
        self.msgbus_publish('LOG','%s Start Logging Adapter')

    #def start_borker(self):
    def start_msgbroker(self):
        print('Start Message Broker')
       # self.msgbus_publish('LOG','%s Start MQTT broker'%('INFO'))
        self._msgbroker = msgbroker()
        self._msgbroker.start()
        #self.msgbus_publish('LOG','%s Start Message broker')

   # def start_mqttbroker(self):
    #    print('Start Broker')
     #   self._mqttbroker = mqttbroker()
      #  self._mqttbroker.start()


    #    self._broker_thread = mqtt_adapter()
   #     self._broker_thread.start()

    #def start_msgbroker(self):
     #   print('Start Message Broker')
      #  self._msgbroker = msgbroker()


    def start_devices(self):
        print('Start Devices')
        self.msgbus_publish('LOG','%s Start VHM Virtual Hardware Manager')
        self._vhm_thread = vhm()
       # self._vhm_thread.start()

    def run(self):
        """
        Entry point, initiates components and loops forever...
        """

        self.start_config()
        self.start_logging()
       # self.start_mqttbroker()
        self.start_msgbroker()
      #  self.start_msgbroker()
   #     self.msgbus_publish('LOG','%s Start mqtt2gpio adapter; Version: %s, %s '%('INFO', __VERSION__ ,__DATE__))
       # self.start_borker()

        #self._msgbroker.run()
    #    self.start_devices()
       # time.sleep(5)$
        time.sleep(2)

        self._cfg_thread.publish()

        #while True:
         #   self._msgbroker.run()
        #cfg = configmodule
        #
        time.sleep(2)
        MSG = {'MESSAGE':{'TYPE':'CONFIG','MODE':'ADD'},'BROKER':{'HOSTS':'localhost','PORT':1883}}

        self.msgbus_publish('DATA_TX',MSG)


      #  self.start_borker()







if __name__ == "__main__":

    print ('main')
    if len(sys.argv) == 3:
        configfile = sys.argv[2]
    else:
        configfile = '../config/config.yaml'

    print('Configfile',configfile)
    mgr_handle = manager(configfile)
    mgr_handle.run()