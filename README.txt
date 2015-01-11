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