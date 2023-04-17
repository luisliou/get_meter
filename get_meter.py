import socket
import struct
import os
import paho.mqtt.client as mqtt
import time
import logging
import yaml
import codecs

data_items = {
    'Voltage': '8193',
    'Current': '8195',
    'Power': '8201',
    'Freq': '8207',
    'Consumption': '16385'
}

isConnected = False

f = codecs.open('config.yaml', 'r', encoding="utf-8")
conf = yaml.load(f, Loader=yaml.FullLoader)


def get_data():
    modpoll_output = os.popen(
        './modpoll -m enc 192.168.0.126 -p 23 -a 04 -c 18 -r 8193 -t 4:hex -1 | grep -E [\[][0-9]*]:.0x').read()

    modpoll_output += os.popen(
        './modpoll -m enc 192.168.0.126 -p 23 -a 04 -c 2 -r 16385 -t 4:hex -1 | grep -E [\[][0-9]*]:.0x').read()

    lines = modpoll_output.split("\n")
    response = {}
    for line in lines:
        item = line.split(": ")
        if len(item) == 2:
            #    key = item[0].replace('[', '').replace(']','')
            data_key = item[0]
            data_value = item[1]
            #    value = item[1].replace('0x', '')
            #      print('key:' + key + '   value:' + value)
            response[data_key] = data_value
    #  print(response)

    result = {}
    for data_key, data_value in data_items.items():
        value0 = response['[' + data_value + ']'].replace('0x', '')
        #    print(key)
        # print(value0)
        value1 = response['[' + str(int(data_value) + 1) + ']'].replace('0x', '')
        print(value0 + value1)
        float_value = struct.unpack('!f', bytes.fromhex(value0 + value1))[0]
        print(float_value)
        #    print('----')
        result[data_key] = float_value
    return result
    #  print(str(response[int(value) + 1]))


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global isConnected
    isConnected = True
    logging.info("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("device_tracker/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logging.info(msg.topic + " " + str(msg.payload))
    print(msg.topic + " " + str(msg.payload))


def on_disconnect(client, userdata, rc):
    global isConnected
    if rc != 0:
        logging.error("Unexpected MQTT disconnection. Will auto-reconnect")
    isConnected = False


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect
try:
    mqtt_client.username_pw_set(username=conf['mqtt']['user'], password=conf['mqtt']['pass'])
    mqtt_client.connect(conf['mqtt']['host'], conf['mqtt']['port'], 60)
except socket.error as e:
    print("mqtt error")
    exit(-1)
mqtt_client.loop_start()

while True:
    print(isConnected)
    if isConnected:
        ret = get_data()
        for key, value in ret.items():
            print(key + str(value))
            mqtt_client.publish(conf['mqtt']['topic'] + key, str(value), True)
    time.sleep(conf['global']['sleep'])
