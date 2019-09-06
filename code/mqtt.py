import paho.mqtt.client as mqtt
import config
import time

print("MQTT.py started...")

# Define stuff for configs
MQTTConfig = config.MQTTConfig()
client = mqtt.Client()

HARD_LIMIT = 0


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTTConfig.topicStart)

# The callback for when a PUBLISH message is received from the server.


def setup():
    client.enable_logger(logger=None)
    client.on_connect = on_connect
    client.username_pw_set(MQTTConfig.username, MQTTConfig.password)
    client.connect(MQTTConfig.ip, int(MQTTConfig.port), 60)
    client.loop_start()



