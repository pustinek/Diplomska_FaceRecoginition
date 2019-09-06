import imutils
import time
from azure import Azure
from cv2 import cv2
import json

import config
import mqtt

print("RUN.py started...")


def on_message(client, userdata, msg):
    global count
    global HARD_LIMIT
    print(msg.topic + " " + str(msg.payload))
    if msg.topic == MQTTConfig.topicStart:
        try:
            i = int(msg.payload)
            HARD_LIMIT = i
            count = 0
        except ValueError:
            print("please enter an integer")

mainConfig = config.MainConfig()
cameraConfig = config.CameraConfig()
MQTTConfig = config.MQTTConfig()

print("main Topic: ", MQTTConfig.topicMain)

# How many seconds should the code wait before calling the API again
api_call_time_limit = mainConfig.apiCallTimeLimit

azure = Azure()

camera_url = "rtsp://{0}:{1}@{2}".format(cameraConfig.username, cameraConfig.password, cameraConfig.ip)

HARD_LIMIT = 15

stream = cv2.VideoCapture(camera_url)
print("Stream starting !!...")
t_start = time.time()
count = 0

mqtt.setup()
mqtt.client.on_message = on_message

# LIMITED: the program is limited to 15 iterations/API calls, since we are limited with the request count
while True:
    r, f = stream.read()
    if time.time() - t_start > (api_call_time_limit / 1000):
        if count < HARD_LIMIT:
            count += 1
            t_start = time.time()
            frame = imutils.resize(f, width=1080)
            res = azure.doTheMagic(frame)
            to_send = json.dumps(res)
            print("mainTopic:", MQTTConfig.topicMain)
            mqtt.client.publish(MQTTConfig.topicMain, to_send)

            mqtt.client.publish(MQTTConfig.topicInfo, "Executing API call ({0}/{1})".format(count, HARD_LIMIT))
            print("Stream sending to azure...!!", count)
        else:
            mqtt.client.publish(MQTTConfig.topicInfo, "Not executing API calls, waiting for start command")

        t_start = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
