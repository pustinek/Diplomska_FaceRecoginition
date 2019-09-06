# This is intended for creating a cache of persons in a person group

# call this function to recall the azure API and get the newest copies of persons
import config as config
import requests

mainConfig = config.MainConfig()
idConfig = config.FaceIndentificationConfig()

persons = []


def getPersonByCandidate(candidate):
    for index, element in enumerate(persons):
        if element["personId"] == candidate["personId"]:
            return element
    return None

def reCachePersons():
    global persons
    headers = {
        'Ocp-Apim-Subscription-Key': mainConfig.apiKey,
        'Content-Type': 'application/json'
    }

    for group in idConfig.groups:
        person_get_api = 'https://{0}.api.cognitive.microsoft.com/face/v1.0/persongroups/{1}/persons'.format(
            mainConfig.region, group)
        response = requests.get(person_get_api, headers=headers)
        if (response.status_code == 200):
            # On success, loop through persons and save them to dictionary
            responseJSON = response.json()
            persons = responseJSON


# on first init, re-cache it
reCachePersons()
