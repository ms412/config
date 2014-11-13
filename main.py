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


import os
import sys
import time

from library.libtree import tree
from library.libmsgbus import msgbus

from module.adapter.config import configmodule
from module.adapter.logging import loghandle
from module.adapter.broker import mqttClient



class manager(msgbus):

    def __init__(self,cfg_file='config.yaml'):

        self._cfg_file = cfg_file

        self._cfg_root_handle = None
        self._cfg_general_handle = None
        self._cfg_broker_handle = None
        self._cfg_device_hanlde = None

        self._log_handle = None


    def start_config(self):
        print('Start Configuration',self._cfg_file)
        cfg_module = configmodule()
        self._cfg_root_handle = cfg_module.loadFile(self._cfg_file)
        self._cfg_general_handle = cfg_module.select('GENERAL')
        self._cfg_broker_handle = cfg_module.select('BROKER')
      #  print ('GENERAL', self._cfg_general_handle.debug())
       # print ('BROKER', self._cfg_broker_handle.debug())

    def start_logging(self):
        print('Debug Logging1', self._cfg_general_handle.debug())
        logfile = self._cfg_general_handle.getNode('LOGFILE','/var/log/mqtt2gpio.log')
        logmode = self._cfg_general_handle.getNode('LOGMODE','DEBUG')
        self._log_handle = loghandle()
        self._log_handle.open(logfile,logmode)

        self.msgbus_publish('LOG','%s Start mqtt2gpio adapter; Version: %s, %s '%('INFO', __VERSION__ ,__DATE__))

    def start_borker(self):
        self._log_handle.info('Start MQTT Broker')
        self._brokerThread = mqttClient()
        self._brokerThread.start()

    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
        self.start_config()
        self.start_logging()
     #  self.start_borker()







if __name__ == "__main__":

    print ('main')
    if len(sys.argv) == 3:
        configfile = sys.argv[2]
    else:
        configfile = './config/config.yaml'

    print('Configfile',configfile)
    mgr_handle = manager(configfile)
    mgr_handle.run()