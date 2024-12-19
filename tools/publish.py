import requests
import json


with open("script.js", "r") as file:
    contents = file.read()
with open('config.json') as f:
  config = json.load(f)


url = 'https://script.google.com/macros/s/'+config["deploymentId"]+'/exec'
myobj = {
    'post': '5777243347759718755'
    ,'blog':'2088387750640558372'
    ,'content':"<pre>"+contents+"</pre>"
    , 'mode':'update-post'
    ,'debug': 'true'
}

x = requests.post(url, json = myobj)

print(x.text)