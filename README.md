# python-pushbulletsimpleapi
A basic class for SMS and messaging using pushbullet v2 API

To use this, you should install PushBullet on your phone and get an Access Token on [[your account settings page|https://www.pushbullet.com/#settings/account]].

The access token is also referred to as "Api key"

## Usage

```python

#Initialization
pb = PushBullet('<myAPIKey>')

#Send Pushbullet messages
pb.message("title only")
pb.message("title and body","Here's the body")

#Get phone attached to the api_key account
myphones = pb.get_sms_phones()
for phone in myphones:
  print(phone['name'])
  
#Send SMS
pb.sms('<phone number>','message') #defaults to first phone
pb.sms('<phone number>','message', sending_phone=myphones[1])

```
