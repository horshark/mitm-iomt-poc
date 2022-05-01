"""
Client / Sensor

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

serverMACAddress = 'XX:XX:XX:XX:XX:XX'
password = "1234567890123456" # CODE THAT DOESN'T CHANGE, LINKED TO THE HARDWARE.
port = 3

###############################################
######### MAIN
###############################################


### INIT: Setup connection.
server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print("## INIT: Attempting connection...")

server.connect((serverMACAddress, port))
print("\n## INIT: Connected!")

print("\n## INIT: Waiting for ACK PASS...")

rep = server.recv(1024)
if(decrypt(rep, password) != b"ACK PASS"):
    print("\n## INIT: Wrong password!!!")
    exit()

print("\n## INIT: Received ACK PASS")


### STEP 1: We get an average of RSSI to setup a new password.
print("\n## STEP 1: Calculating RSSI")
rssi_avg = get_rssi_avg(serverMACAddress)
print("RSSI average (out of 3): ", rssi_avg)


### STEP 2: Client sends RSSI & wait for ACK.
print("\n## STEP 2: Sending RSSI...")
msg_clear = "RSSI " + rssi_avg
msg = encrypt(msg_clear, password)

res = send_wait_answer(server, msg)
res_clear = decrypt(res, password)
print(res_clear)
rssi_server = res_clear.decode().split(" ")[1]
print("Received:\t ", res_clear)


### STEP 3: Wait for the server's RSSI & send ACK.
print("\n## STEP 3: Waiting for server's RSSI...")
msg_clear = "ACK RSSI"
msg = encrypt(msg_clear, password)

res = receive_and_reply(server, msg)
res_clear = decrypt(res, password)
rssi_server = res_clear.decode().split(" ")[1]
print("Received:\t ", res_clear)

# Compare the server's RSSI to the one we calculate.
rssi_server_trfm = rssi_transform(int(rssi_server))
rssi_avg_trfm = rssi_transform(int(rssi_avg))
if not rssi_close(int(rssi_server), int(rssi_avg)):
    # RSSIs are too far appart.
    # Close connection or whatever you chose to do. But don't continue.
    server.close()
    exit()


### STEP 4: Change the password to the average of both RSSI.
password = str((rssi_server_trfm + rssi_avg_trfm) // 2)


### STEP 5: Send data to the server, using the new password.
print("\n## STEP 5: Sending data...")

msg_clear = "DATA Hello World!"
msg = encrypt(msg_clear, password)

print("Clear data:\t ", msg_clear)
print("Encrypted data:\t ", msg)

res = send_wait_answer(server, msg)
res_clear = decrypt(res, password)
print("Received:\t ", res_clear)

##### You now have a secured connection, that is not using the default PIN password.
##### Repeat step 1 to 4 every X minutes to renew the encryption key. -> can be done in the background with locks & such.

sleep(30)
