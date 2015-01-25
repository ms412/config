#!/bin/bash -e

DIR=/opt/gpio2mqtt
CONFIG_DIR=/etc/gpio2mqtt
INIT_DIR=/etc/init.d


if [ -d "$DIR" ]; then
    echo $DIR already exists.
else
    sudo mkdir $DIR
fi
sudo cp -r ./module $DIR/
sudo cp -r ./library $DIR/
sudo cp gpio2mqtt.py $DIR
sudo chmod 755 $DIR/gpio2mqtt.py


if [ -d "$CONFIG_DIR" ]; then
    echo $CONFIG_DIR already exists.
else
    sudo mkdir $CONFIG_DIR
fi

#sudo cp .confg/gpio2mqtt.yaml $CONFIG_DIR/

if [ ! -f "$CONFIG_DIR/gpio2mqtt.yaml" ]; then
    sudo cp .confg/gpio2mqtt.yaml $CONFIG_DIR/
else
    echo $CONFIG_DIR/gpio2mqtt.yaml already exists.
fi

if [ -d "$INIT_DIR" ]; then
    echo $INIT_DIR exists.
else
    echo ERROR
    echo $INIT_DIR does not exist
    exit
fi

if [ ! -f "$INIT_DIR/gpio2mqtt" ]; then
    sudo cp .scripts/gpio2mqtt/gpio2mqtt $INIT_DIR/
else
    echo $INIT_DIR/gpio2mqtt already exists.
fi

exit 0

