import os
import requests
#url='http://localhost:3500/'
url="https://facedetection-server.thankfulmoss-5686afa8.westeurope.azurecontainerapps.io"
values={ 'id':'photo'}
r=requests.post(url,files={'imageData':open('Bild000.jpg','rb')},data=values)
print("Response: "+r.text)