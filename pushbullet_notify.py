#!/usr/bin/python
# This is for python 2
# it does not require requests module
# it does require 'curl' to be present on the system

import argparse
# define the argument list
parser = argparse.ArgumentParser()
parser.add_argument("message", type=str, help="the message to send (title line)")
parser.add_argument("-b","--body", help="set the body of the message (optional body)", type=str)

#parse arguments
args = parser.parse_args()

#here, args.message contains the title and args.body optionally contains the message body
#change None to "" if necessary
if args.body == None:
    args.body = ""

#retrieve pushbullet authentication key
import json

authorization = None
#search in home auth file
from os.path import expanduser
home = expanduser("~")
auth_file = home + "/.pushbullet_auth"

try:
    fid = open(auth_file,'r')
    auth_file_content = fid.read()
    authorization = json.loads(auth_file_content)
    if len(authorization['key']) == 0 :
        authorization = None
except:
    authorization = None
    pass
finally:
    try:
        fid.close()
    except:
        pass

# if not found, just ask for user and write file
if authorization == None:
    try:
        #didn't find a valid authorization, ask for one
        print("No valid authorization token found, please go to:\n    https://www.pushbullet.com/#settings/account\nand create an access token, then paste it here:\n")
        user_input = raw_input('authorization token: ').strip()
        authorization = {'key': user_input}
        print(authorization)
        fid = open(auth_file,'w+')
        fid.write(json.dumps(authorization))
    except :
        import traceback
        print(traceback.format_exc())
        authorization = None
    finally:
        try:
            fid.close()
        except:
            pass

authkey = authorization['key']


#build the json representation of the message and format the curl call
data_send = json.dumps({"type": "note", "title": args.message, "body": args.body})
command = ["curl","--silent","--header", "Authorization: Bearer " + authkey,
    "--header", "Content-Type: application/json",
    "--data-binary", data_send,
    "--request", "POST",
    "https://api.pushbullet.com/v2/pushes"]

# perform the curl call
import subprocess as sp
import sys as sys

try:
    # perform the call to curl
    process = sp.Popen(command, stdout = sp.PIPE, stderr = sp.PIPE)
    out, err = process.communicate()
    # interpret server response
    response = json.loads(out)

    # check for errors (in which case the error_code key is set
    if 'error_code' in response.keys():
        print >> sys.stderr, "Failed with code: [%s]" % response['error_code']
        sys.exit(2)
    else:
        # if error key wasn't present, just exit with curl process error
        print >> sys.stderr, err
        sys.exit(process.returncode)

except SystemExit as e:
    # just catch System Exit and exit again
    sys.exit(e)

except:
    # catch-all
    import traceback
    print(traceback.format_exc())
    sys.exit(1)

