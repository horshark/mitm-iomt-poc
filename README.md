# Preventing MitM in IoMT: How to provide confidentiality, integrity, and authentication in a vulnerable environment

__**Disclaimer**__: These scripts are not a template to base your work upon. They are not an ideal use-case either. They were written to demonstrate and as support material for our article to help readers undertand our methodology. If you plan on using our solution, you would need to write your own protocol, use the algorithm of your choice and tweak the settings accordingly.

# How to use the POC
If you wish to reproduce the environement here are the steps to follow.

## Setup
1- Have two devices that are capable of using Bluetooth and have Python installed.
2- Define which device will be the Access Point and which will be the Sensor.
3- Copy the right files on the devices.
   - On the Access Point: poc_bluetooth_server.py, poc_lib.py, requirements.txt
   - On the Sensor: poc_bluetooth_sensor.py, poc_lib.py, requirements.txt
4- On both devices you need to use pip to install the packages from the requirements.txt file ``sudo pip3 install -r requirements.txt``
5- Now you will need to fetch the MAC address of the AP device. To do so you can use ``hcitool dev``.
6- You need to replace the MAC address in both ``poc_bluetooth_<server|sensor>.py`` files for the variables called ``serverMACAddress``, ``hostMACAddress``. (This can be avoided by implementing a dynamic recognition of AP devices using broadcasting)

## Run
1- Before starting the POC, you need to use the tool ``bluetoothctl`` to enable pairing and being discoverable. NOTE: the pairing and discoverable state will expire, if you can't connect in the following steps, make sure they are on.
```bash
$_sudo bluetoothctl
> default-agent
> agent on
> pairable on
> discoverable on
> pair <MAC_ADDRESS>
```
2- You can now start the server POC (order matters) using ``sudo python3 poc_bluetooth_server.py``, the server will listen for a new connection.
3- Now start the sensor POC ``sudo python3 poc_bluetooth_sensor.py``, it will connect to the server with the matching MAC address.

## Done!
You're all set, feel free to experiment with different values to assess how they can affect the performances.
