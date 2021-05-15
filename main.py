import requests
import config 

## Object that contains CheckMK functions
class CheckMK:
    def __init__(self, server, auth):
        self.headers = {
            'accept' : 'application/json',
            'Authorization' : auth
        }
        self.server = server

    def getServiceStatus(self): 
        url = "{server}/api/v0/domain-types/service/collections/all".format(server=self.server)        
        query = {
            'columns':['host_name', 'description', 'state'], 
            'query': '{"op": "=", "left": "state", "right": "1"}'
        }
        return requests.get(url, query, headers=self.headers).json()

## Simple Telegram messanging
class Telegram:
    def __init__(self, token, chatID):
        self.token = token
        self.chatID = chatID
    
    def send(self, message):
        url = "https://api.telegram.org/bot{token}/sendMessage?chat_id={chatID}&parse_mode=Markdown&text={message}".format(
            token=self.token,
            chatID=self.chatID,
            message=message
        )
        return requests.get(url)


## This function parses json from CheckMK.getServiceStatus() to string
def generateOutput(json):
    output = ""
    for value in json['value']:
        output += "Host: {host} Description: {desc} State: {state}\n".format(
            host=value['extensions']['host_name'],
            desc=value['extensions']['description'],
            state=value['extensions']['state']
        )
    return output[:-1]


if __name__ == "__main__":     
    ## Get the service Statuses
    check_mk = CheckMK(config.check_mk, config.check_mk_auth)
    serviceStatus = check_mk.getServiceStatus()

    ## Send the telegram message
    telegram = Telegram(config.telegram_auth, config.telegram_chat_id)
    telegram.send(generateOutput(serviceStatus))

