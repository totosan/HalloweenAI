from flask import Flask, redirect, render_template
import os
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

@app.route("/deleteall")
def delete():
    rr.deleteAll()
    return render_template("index.html",)