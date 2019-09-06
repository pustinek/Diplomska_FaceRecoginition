import requests
import cv2
import config as config
import personsCache


class Azure:
    idConfig = config.FaceIndentificationConfig()
    mainConfig = config.MainConfig()

    errors = []
    detectionObj = {}
    identificationObj = {}

    # TODO: return full object that will be sent over MQTT
    def doTheMagic(self, frame_data):
        # clean up previous errors
        self.errors = []

        detectionRes = self.faceDetection(frame_data)
        detectionResJson = detectionRes.json()
        # Success:
        if detectionRes.status_code == 200:
            if len(detectionResJson) > 0:
                self.detectionObj = MQTTDetection("PERSONS_DETECTED", len(detectionResJson))
                identificationRes = self.faceIdentification(detectionResJson)

                self.errors.append(identificationRes["errors"])
                self.identificationObj = MQTTIdentification("PERSONS_IDENTIFIED", len(identificationRes["persons"]),
                                                            identificationRes["persons"])
            else:
                # No faces detected
                self.identificationObj = MQTTIdentification("NO_PERSONS_IDENTIFIED", 0, [])
                self.detectionObj = MQTTDetection("NO_PERSONS_DETECTED", 0)
        else:
            # TODO: something has failed, create error object and add to array
            error = MQTTError(detectionResJson["error"]["code"], detectionResJson["error"]["message"])
            self.errors.append(error.__dict__)

        return {
            "detection": self.detectionObj.__dict__,
            "identification": self.identificationObj.__dict__,
            "errors": self.errors
        }

    def faceIdentification(self, detection_data):

        face_identify_api = 'https://{0}.api.cognitive.microsoft.com/face/v1.0/identify'.format(
            self.mainConfig.region)
        identify_headers = {
            'Ocp-Apim-Subscription-Key': self.mainConfig.apiKey,
            'Content-Type': 'application/json'
        }

        identify_params = {
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': '',
        }

        if detection_data is not None:
            # Extract face id's from the data received by
            # the azure face detection api
            # They are required to identify a person
            face_ids = []
            for face_data in detection_data:
                face_id = face_data.get("faceId", "")
                face_ids.append(face_id)

            errors = []
            persons = []
            for group in self.idConfig.groups:
                data = {
                    'faceIds': face_ids,
                    'personGroupId': group,
                    'maxNumOfCandidatesReturned': 10,  # Default:10 (optional)
                    'confidenceThreshold': 0.5
                }
                response = requests.post(
                    face_identify_api, headers=identify_headers, json=data)
                if response.status_code == 200 or response.status_code == 201:
                    responseJSON = response.json()
                    # array of identified faces

                    for identification in responseJSON:
                        if len(identification["candidates"]) > 0:
                            candidate = identification["candidates"][0]
                            matchingPerson = personsCache.getPersonByCandidate(candidate)
                            name = matchingPerson["name"]
                            userdata = matchingPerson["userData"]

                            person = MQTTPerson(group, name, userdata, candidate['confidence'])
                            persons.append(person.__dict__)

                    # TODO: create MQTTPerson object and add to persons array !
                else:
                    print("[{0}] - {1}".format(response.status_code, response.json()))

                    error = MQTTError(response.json()["error"]["code"], response.json()["error"]["message"])
                    errors.append(error.__dict__)

            return {"persons": persons, "errors": errors}

    def faceDetection(self, frame_data):
        suc, a_numpy = cv2.imencode('.jpg', frame_data)
        frame_data = a_numpy.tostring()
        face_detect_api = 'https://{0}.api.cognitive.microsoft.com/face/v1.0/detect'.format(
            self.mainConfig.region)

        detect_headers = {
            'Ocp-Apim-Subscription-Key': self.mainConfig.apiKey,
            'Content-Type': 'application/octet-stream'
        }
        detect_params = {
            'returnFaceId': 'true',
            'recognitionModel': 'recognition_01',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': '',
        }
        response = requests.post(
            face_detect_api, headers=detect_headers, params=detect_params, data=frame_data)

        return response


class MQTTDetection:
    code = "SUCCESS"
    detections = 0

    def __init__(self, code, detections):
        self.code = code
        self.detections = detections


class MQTTIdentification:
    code = "UNKNOWN"
    identified = 0
    persons = []

    def __init__(self, code, identified, persons):
        self.code = code
        self.identified = identified
        self.persons = persons


class MQTTPerson:
    group = "UNKNOWN"
    name = ""
    userData = ""
    confidence = 0

    def __init__(self, group, name, userData, confidence):
        self.group = group
        self.name = name
        self.confidence = confidence
        self.userData = userData


# Error class used in MQTT communication
class MQTTError:
    code = ""
    message = ""

    def __init__(self, code, message):
        self.code = code
        self.message = message
