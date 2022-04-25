import os
import requests
#url='http://localhost:3500/'
url="https://facedetection-server.yellowbeach-8b94c1b8.westeurope.azurecontainerapps.io:3500/"
values={ 'id':'photo'}
r=requests.post(url,files={'imageData':open('Bild000.jpg','rb')},data=values)
print("Response: "+r.text)