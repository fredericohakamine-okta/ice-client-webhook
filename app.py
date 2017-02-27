#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

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

    action = req.get("result").get("action")
    if action == "addUser":
        res = addUser(req)
    elif action == "modUser":
        res = modUser(req)
    elif action == "resetUser":
        res = resetUser(req)
    else:
        return {}

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def addUser(req):
    baseurl = "https://oktaice612-admin.oktapreview.com"
    key = "00KKwYAyt72aImR9sU-JOMAJuB3VULUFXMD4BzC32f"
    url = baseurl+"/api/v1/users?activate=false";

    result = req.get("result")
    parameters = result.get("parameters")
    firstName = parameters.get("given-name")
    lastName = parameters.get("last-name")
    email = parameters.get("email")

    # user data
    payload = "{'profile': { 'firstName': '"+firstName+"', 'lastName': '"+lastName+"', 'email': '"+email+"', 'login': '"+email+"'}}"
    data = json.dumps(payload);

    #header
    headers = { 'accept': "application/json", 'content-type': "application/json", 'authorization': "SSWS "+key }

    print('Before request')
    print('headers')
    print(headers)
    print('payload')
    print(data)
    print('URL')
    print(url)
    #request
    req = urllib2.Request(url, data, headers)
    print('After request')

    #perform the rest api call
    result = urlopen(req)
    result2 = result.read()
    responsecode = result.getcode()
    data = json.loads(result2)
    print(data)

    if responsecode == 200:
        speech = "User created"
    else:
        speech = "Error "+responsecode

    # print(json.dumps(item, indent=4))
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-user-webhook-sample"
    }

def modUser(req):
    #define what to do based on the action parameter
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    #perform the rest api call
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res

def resetUser(req):
    #define what to do based on the action parameter
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    #perform the rest api call
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res

def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    #placeholder for variables
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
