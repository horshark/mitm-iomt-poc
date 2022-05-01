import base64
import subprocess
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512

###############################################
######### CONFIG
###############################################

size = 1024
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

###############################################
######### UTILS
###############################################

## Getting RSSI.
### We decided to get an average of 3 value to make it more accurate & avoid off values due to the environment.
### You could use more than 3 to improve it, we are not doing so as this is a POC & the way we fetch values (through a BASH command) is fairly slow.

def get_rssi_one(addr):
    p = subprocess.Popen('sudo btmgmt find | grep {}'.format(addr), stdout=subprocess.PIPE, shell=True)
    a, b = p.communicate()
    read_lst = []

    for reading in str(a).split('\\n')[:-1]:
        reading = reading.split('rssi ')[1]
        reading = reading.split(' flags')[0]
        reading = int(reading)
        read_lst.append(reading)

    if len(read_lst) == 0:
        return 0

    return sum(read_lst) / len(read_lst)

def get_rssi_avg(addr):
    values = []

    for i in range(3):
        print("## Fetching RSSI {}/3...".format(i+1))
        values.append(get_rssi_one(addr))

    return str(round(sum(values) / len(values)))

## RSSI actions.
### Basic things to transform the RSSI into bigger values & check if the RSSI are close to one another.

def rssi_transform(x):
    res = 0
    for i in range(5):
        res = res + pow(x, i)
    print("RSSI: ", x, "\nTransformed RSSI: ", res)
    return res

def rssi_close(x, y):
    res = abs(x - y)
    return res <= 3

## Encryption.

def encrypt(raw, password):
    salt = Random.new().read(AES.block_size)
    private_key = PBKDF2(password, salt, 16, count=10000, hmac_hash_module=SHA512)

    raw = pad(raw)
    raw = raw.encode("utf-8")
    cipher = AES.new(private_key, AES.MODE_CBC, salt)
    return base64.b64encode(salt + cipher.encrypt(raw))

def decrypt(enc, password):
    enc = base64.b64decode(enc)
    salt = enc[:16]

    private_key = PBKDF2(password, salt, 16, count=10000, hmac_hash_module=SHA512)

    cipher = AES.new(private_key, AES.MODE_CBC, salt)
    return unpad(cipher.decrypt(enc[16:]))

## Sending & receiving packets.

def send_wait_answer(client, msg):
    client.send(msg)
    return client.recv(size)

def receive_and_reply(client, msg):
    res = client.recv(size)
    client.send(msg)
    return res