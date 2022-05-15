from flask import Flask, jsonify, redirect, render_template, Response
import os, json
import readRedis as rr

app = Flask(__name__)

picFolder = os.path.join('static', 'pics')

app.config['UPLOAD_FOLDER'] = picFolder

@app.route("/")
def index():
    rr.readImges()
    
    imageList = os.listdir('./static/pics')
    imagelist = ['pics/' + image for image in imageList]
    return render_template("index.html", imagelist=imagelist)

@app.route("/images")
def images():
    rr.readImges()
    imageList = os.listdir('./static/pics')
    imagelist = ['pics/' + image for image in imageList]
    response = Response(json.dumps(imagelist), mimetype='application/json', headers={'Access-Control-Allow-Origin': '*'})
    return response
    
@app.route("/deleteall")
def delete():
    rr.deleteAll()
    return render_template("index.html",)