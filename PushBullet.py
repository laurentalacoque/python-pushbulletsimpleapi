import requests
import json

class PushBullet:
    """Give access to pushbullet messaging
    
        Usage:
        pb = PushBullet('<api key>')
        pb.message("hello!")
        pb.sms("+33634242424","hello!")
        
        phones = pb.get_sms_phones()
        pb.sms("+33634242424" , phones[1])

    """

    def __init__(self, auth_token):
        """initialize the object with the authentication token <auth_token>"""
        
        self.auth_token = auth_token
        #Get token owner info
        resp = requests.get('https://api.pushbullet.com/v2/users/me',
                            headers={'Authorization': 'Bearer ' + self.auth_token, 
                                     'Content-Type': 'application/json'})
        self.__check_pb_error(resp.status_code)
        self.token_owner = json.loads(resp.text)
        
        #Get token owner list of devices
        resp = requests.get('https://api.pushbullet.com/v2/devices',
                            headers={'Authorization': 'Bearer ' + self.auth_token, 
                                     'Content-Type': 'application/json'})
        self.__check_pb_error(resp.status_code)
        self.devices = json.loads(resp.text)
        
    def sms(self, phone_number, body, sending_phone = None):
        """Send a text message with body <body> to contact <phone_number>
        if sending_phone_iden is None, we will try to use the first phone 
        in the list of devices that can send text messages.
        
        self.devices contains the list of registered devices
        if obj.devices[0]['has_sms']: 
            obj.sms('0760039432','Hello there :)', sending_phone = obj.devices[0]['iden'])
        """
        #find phone!
        target_device_iden=None
        try:
            if sending_phone is None:
                #take the first one
                all_phones = self.get_sms_phones()
                target_device_iden = all_phones[0]['iden']
            elif type(sending_phone) is str:
                #use this as iden
                target_device_iden = sending_phone
            elif type(sending_phone) is dict:
                #intepret as {"name":"<name>","iden":"xjfkldsfjq"} dict
                target_device_iden = sending_phone['iden']
            
            #here the target device should be set
            #if not, raise an exception
            if  not target_device_iden: raise Exception()

        except:
            raise Exception('Phone Error')

        data_send = {
            'push': {
                'conversation_iden': phone_number,
                'message': body,
                'package_name': 'com.pushbullet.android',
                'source_user_iden': self.token_owner['iden'],
                'target_device_iden': target_device_iden,
                'type': 'messaging_extension_reply'
                },
            'type' : 'push'
        }
        resp = requests.post('https://api.pushbullet.com/v2/ephemerals', 
                             data=json.dumps(data_send),
                             headers={'Authorization': 'Bearer ' + self.auth_token, 'Content-Type': 'application/json'})
        self.__check_pb_error(resp.status_code)
        
        #print(json.dumps(data_send,indent=4))
        #print("response: ",resp.text)
        
    
    def get_sms_phones(self):
        """Get a list of dict with format {"name":"<phone_name>","iden":"<phone_iden>"}, ...  """
        phone_list = []
        for device in self.devices['devices']:
            try:
                if device['type'] == 'android' and device['has_sms'] :
                    phone_list.append({"name": device['nickname'], "iden": device['iden']})
            except:
                pass
                
        return phone_list
 
    def message(self, title, body = ""):
        """send message with title <title> and body <body> to the connected app"""
        data_send = {"type": "note", "title": title, "body": body}
        resp = requests.post('https://api.pushbullet.com/v2/pushes', 
                             data=json.dumps(data_send),
                             headers={'Authorization': 'Bearer ' + self.auth_token, 'Content-Type': 'application/json'})
        self.__check_pb_error(resp.status_code)
        #print(json.dumps(json.loads(resp.text),indent=4))
    
    # Private methods below
    def __check_pb_error(self, status_code):
        """React to pushbullet errors"""
        if status_code ==  200: return
        elif status_code == 400: raise Exception('Bad Request')
        elif status_code == 401: raise Exception('Authorization error: Unauthorized')
        elif status_code == 403: raise Exception('Authorization error: Forbidden')
        elif status_code == 404: raise Exception('API error: Address not found')
        elif status_code == 429: raise Exception('Too many Requests')
        elif status_code >= 500 and status_code < 600 : raise Exception('Temporary Server error %d'%status_code)
        else: raise Exception('Unspecified error %d' % resp.status_code)    
        
