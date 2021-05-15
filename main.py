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
            #'query': '{"op": "=", "left": "state", "right": "1"}'
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
    hosts = {}

    ## colect hosts
    for host in json['value']:
        if (host['extensions']['host_name'] not in hosts):
            hosts[host['extensions']['host_name']] = {
                'normal':0, 
                'warning':0, 
                'critical':0
            }

    ## count normal, critical, warning
    for host in json['value']:
        if (host['extensions']['state'] == 0):
            hosts[host['extensions']['host_name']]['normal'] += 1
        if (host['extensions']['state'] == 1):
            hosts[host['extensions']['host_name']]['warning'] += 1
        if (host['extensions']['state'] == 2):
            hosts[host['extensions']['host_name']]['critical'] += 1

    ## Generate output
    output = "Status for \n"
    for host in hosts:
        output += '{hostName}: Critical {critical}; Warning {warning}\n'.format(
            hostName=host,
            critical=hosts[host]['critical'],
            warning=hosts[host]['warning']
        )
    
    return output[:-1]


if __name__ == "__main__":     
    ## Get the service Statuses
    check_mk = CheckMK(config.check_mk, config.check_mk_auth)
    serviceStatus = check_mk.getServiceStatus()

    ## Send the telegram message
    telegram = Telegram(config.telegram_auth, config.telegram_chat_id)
    telegram.send(generateOutput(serviceStatus))
    #print(generateOutput(serviceStatus))

