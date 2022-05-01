"""
Server / phone or home station

YOU MUST PAIR DEVICES BEFORE HAND!
DEVICE MUST BE DISCOVERABLE!

Be aware that the RSSI check can fail if the bluetooth hardware are too different.
"""

import bluetooth
from time import sleep
from poc_lib import *


###############################################
######### CONFIG
###############################################

hostMACAddress = 'XX:XX:XX:XX:XX:XX' # The MAC address of a Bluetooth adapter on the server. The server might have multiple Bluetooth adapters. 
salt = "" # user input -> will be prompted to enter the code from the hardware trying to connect
port = 3
backlog = 1

###############################################
######### MAIN
###############################################

#####################
##### CONNECTION INIT
#####################


### INIT: Setup connection.
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
s.bind((hostMACAddress, port))
s.listen(backlog)
print("## INIT: Listening...")

client, clientInfo = s.accept()
print("\n## INIT: Connection from: ", clientInfo)


### INIT: We ask for the code that is associated with the sensor.
password = input("Please enter the sensor's code: ")

print("\n## INIT: Sending ACK PASS")
client.send(encrypt("ACK PASS", password))

### STEP 1: Calculate RSSI with the client.
print("\n## STEP 1: Calculating RSSI")
rssi_avg = get_rssi_avg(clientInfo[0])
print("RSSI average (out of 3): ", rssi_avg)


### STEP 2: Wait for client's RSSI & send ACK.
print("\n## STEP 2: Waiting for sensor's RSSI...")
msg_clear = "ACK RSSI"
msg = encrypt(msg_clear, password)

res = receive_and_reply(client, msg)
res_clear = decrypt(res, password)
rssi_client = res_clear.decode().split(" ")[1]
print("Received:\t ", res_clear)

# Compare the sensor's RSSI to the one we calculate.
rssi_client_trfm = rssi_transform(int(rssi_client))
rssi_avg_trfm = rssi_transform(int(rssi_avg))
if not rssi_close(int(rssi_client), int(rssi_avg)):
    # RSSIs are too far appart.
    # Close connection or whatever you chose to do. But don't continue.
    client.close()
    exit()


### STEP 3: We sends RSSI & wait for ACK.
print("\n## STEP 3: Sending RSSI...")
msg_clear = "RSSI " + rssi_avg
msg = encrypt(msg_clear, password)

res = send_wait_answer(client, msg)
res_clear = decrypt(res, password)
print("Received:\t ", res_clear)


### STEP 4: Change the password to the average of both RSSI.
password = str((rssi_client_trfm + rssi_avg_trfm) // 2)


### STEP 5: Wait for data from the sensor, using the new password.
print("\n## STEP 5: Waiting for sensor's data...")

msg_clear = "ACK DATA"
msg = encrypt(msg_clear, password)

res = receive_and_reply(client, msg)
res_clear = decrypt(res, password)

print("Encrypted data:\t ", res)
print("Clear data:\t ", res_clear)

##### You now have a secured connection, that is not using the default PIN password.
##### Repeat step 1 to 4 every X minutes to renew the encryption key. -> can be done in the background with locks & such.

sleep(30)
