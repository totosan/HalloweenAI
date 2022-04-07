from crypt import methods
from distutils.log import debug
import os
import requests
from flask import Flask, request
import json
from dapr.clients import DaprClient

daprPort = os.getenv("DAPR_HTTP_PORT") 
daprGRPCPort = os.getenv("DAPR_GRPC_PORT")
stateStoreName = "statestore"
stateUrl = f"http://localhost:{daprPort}/v1.0/state/{stateStoreName}"

app=Flask(__name__)

def sendToStateStore(id):
    message = [{"id":f"{id}", "status":"received"}]
    print(f"sending FaceId to storage: {stateUrl}")
    with DaprClient() as d:
        # Save state
        d.save_state(store_name="statestore", key="faceId", value=id)

@app.route("/", methods=['POST','GET'])
def faceCallApi():
    if request.method == 'GET':
        return "Hello, please use POST\n"
    print(request.data)
    reqJson = json.loads(request.data)
    id=reqJson["id"]
    print(f"{id} empfangen")
    sendToStateStore(id)
    return f"This was {id}\n"

app.run(host="0.0.0.0",port=3500)    