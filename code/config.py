import yaml
import pathlib


class Config(object):
    def __init__(self):
        fileLoc = pathlib.Path(__file__).parent / "config.yaml"
        with open(fileLoc, "r") as stream:
            try:
                self._config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def get_property(self, property_name):
        properties = property_name.split(".")
        try:
            if len(properties) == 1:
                return self._config[properties[0]]
            elif len(properties) == 2:
                return self._config[properties[0]][properties[1]]
            elif len(properties) == 3:
                return self._config[properties[0]][properties[1]][properties[2]]
        except:
            return None


class MainConfig(Config):
    @property
    def apiKey(self):
        return self.get_property('main.apiKey')

    @property
    def region(self):
        return self.get_property('main.region')

    @property
    def apiCallTimeLimit(self):
        return self.get_property('main.apiCallTimeLimit')


class CameraConfig(Config):
    @property
    def ip(self):
        return self.get_property("camera.ip")

    @property
    def username(self):
        return self.get_property("camera.username")

    @property
    def password(self):
        return self.get_property("camera.password")


class FaceIndentificationConfig(Config):
    @property
    def groups(self):
        return self.get_property('faceIdentification.groups')

    @property
    def maxNumOfCandidatesReturned(self):
        return self.get_property('faceIdentification.maxNumOfCandidatesReturned')

    @property
    def confidenceThreshold(self):
        return self.get_property('faceIdentification.confidenceThreshold')


class FaceDetectionConfig(Config):
    @property
    def returnFaceId(self):
        return self.get_property('faceDetection.returnFaceId')


class MQTTConfig(Config):
    @property
    def ip(self):
        return self.get_property("MQTT.ip")

    @property
    def port(self):
        return self.get_property("MQTT.port")

    @property
    def username(self):
        return self.get_property("MQTT.username")

    @property
    def password(self):
        return self.get_property("MQTT.password")

    @property
    def topicMain(self):
        return self.get_property("MQTT.topics.main")

    @property
    def topicInfo(self):
        return self.get_property("MQTT.topics.status")

    @property
    def topicStart(self):
        return self.get_property("MQTT.topics.start")
