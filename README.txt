Install mqtt broker::

Roger Light, Mosquitto's creator has thankfully (!) set up a Mosquitto Debian repository we can use to obtain the latest and greatest version, so we'll do just that. We first perform the required steps to add and activate the repository. The last step in particular can take a few moments.

curl -O http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key
sudo apt-key add mosquitto-repo.gpg.key
rm mosquitto-repo.gpg.key
cd /etc/apt/sources.list.d/
sudo curl -O http://repo.mosquitto.org/debian/mosquitto-repo.list
sudo apt-get update

Now we can go ahead and install Mosquitto proper. There are three packages:

    mosquitto is the MQTT broker (i.e. server)
    mosquitto-clients are the command-line clients, which I recommend you install
    python-mosquitto are the Python bindings, which I also think you should install

all three packages together require about 665Kb of space, which we can easily afford even on the tiny Pi.

sudo apt-get install mosquitto mosquitto-clients python-mosquitto

Regrettably, as with most Debian packages, the broker is immediately started; stop it.

sudo /etc/init.d/mosquitto stop

To do this, it is worth running the following commands in the Terminal to install the i2c-tools utility.
    sudo apt-get install python-smbus
    sudo apt-get install i2c-tools

 Depending on your distribution, you may also have a file called /etc/modprobe.d/raspi-blacklist.conf

If you do not have this file then there is nothing to do, however, if you do have this file, you need to edit it and comment out the lines below:

    blacklist spi-bcm2708
    blacklist i2c-bcm2708

.. by putting a # in front of them.

    sudo nano /etc/modules

and add these two lines to the end of the file:

    i2c-bcm2708
    i2c-dev

Install smbus library for python3

sudo apt-get update
sudo apt-get install python3-dev
wget http://ftp.de.debian.org/debian/pool/main/i/i2c-tools/i2c-tools_3.1.1.orig.tar.bz2
tar -xf i2c-tools_3.1.1.orig.tar.bz2
cd i2c-tools-3.1.1/py-smbus
cp smbusmodule.c smbusmodule.c.orig  # make backup
wget https://gist.githubusercontent.com/sebastianludwig/c648a9e06c0dc2264fbd/raw/2b74f9e72bbdffe298ce02214be8ea1c20aa290f/smbusmodule.c     # download patched (Python 3) source
    python3 setup.py build
    sudo python3 setup.py install

    http://procrastinative.ninja/2014/07/21/smbus-for-python34-on-raspberry/


mosquitto:
sudo apt-get install mosquitto
 sudo apt-get install mosquitto-clients


 Install:
 YAML
 sudo apt-get install python3-yaml

 Paho
 sudo apt-get install python3-pip
 sudo pip3 install paho-mqtt

RPIO
$ sudo apt-get install python3-setuptools
$ sudo easy_install3 -U RPIO

wget https://pypi.python.org/packages/source/R/RPi.GPIO/RPi.GPIO-0.5.9.tar.gz
tar xvf RPi.GPIO-0.5.9.tar.gz
cd RPi.GPIO-0.5.9/


smbtools
cd ~
sudo apt-get -y install python3-dev
wget http://ftp.de.debian.org/debian/pool/main/i/i2c-tools/i2c-tools_3.1.0.orig.tar.bz2
tar xf i2c-tools_3.1.0.orig.tar.bz2
cd i2c-tools-3.1.0/py-smbus
mv smbusmodule.c smbusmodule.c.orig
wget -O smbusmodule.c http://piborg.org/downloads/picoborgrev/smbusmodule.c.txt
wget http://lm-sensors.org/svn/lm-sensors/tags/V2-10-8/kernel/include/i2c-dev.h
python3 setup.py build
sudo python3 setup.py install