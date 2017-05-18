#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

#from promosUrllib.parse import promosUrlparse, promosUrlencode
#from promosUrllib.request import promosUrlopen, Request
#from promosUrllib.error import HTTPError

import json
import os
import urllib2
import requests

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    #FIGURES OUT WHAT TO DO
    action = req.get("result").get("action")
    if action == "createPromos":
        speech = createPromos(req)
    elif action == "readPromos":
        speech = readPromos(req)
    elif action == "deletePromos":
        speech = deletePromos(req)
    else:
        speech = "I don't understand you."

    res = {
            "speech": speech,
            "displayText": speech,
            "source": "apiai-user-webhook-sample"
          }

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

#for creating new users in Okta
def createPromos(req):
    speech = "Oops... I don't know how to create promos yet."
    return speech

#for read existing promos
def readPromos(req):
    #getting environment variables
    promosApi = os.environ.get('PROMOS_API')
    clientId = os.environ.get('CLIENT_ID')
    clientSecret = os.environ.get('CLIENT_SECRET')
    authzServer = os.environ.get('AUTHZ_SERVER')
    print("Promos API:")
    print(promosApi)
    promosUrl = promosApi+"/promos"

    result = req.get("result")
    parameters = result.get("parameters")
    #firstName = parameters.get("given-name")
    #lastName = parameters.get("last-name")
    #email = parameters.get("email")
    target = parameters.get("target")

    promosUrl = promosUrl+"/"+target
    querystring = {}
    payload = {}
    headers = {}

    response = requests.get(promosUrl, json=payload, headers=headers, params=querystring)

    print(response.text)
    print('After request')

    #perform the rest api call
    responsecode = response.status_code
    data = response.json()
    print(data)

    for promo in data:
        print("desc: " + promo.description)
        print("code: " + promo.code)

    if responsecode == 200:
        speech = "We a special promo. "+data[0].description+". To get this promo, go to ice.cream.io and enter the code "+ data[0].code
    else:
        speech = "Error "+str(responsecode)

    print("Response:")
    print(speech)
    return speech

#for deleting promos
def deletePromos(req):
    speech = "Oops... I don't know how to reset users yet."
    return speech

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
