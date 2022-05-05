from flask import Flask, render_template
import os

app = Flask(__name__)

picFolder = os.path.join('static', 'pics')

app.config['UPLOAD_FOLDER'] = picFolder


@app.route("/")
def index():
    imageList = os.listdir('static/pics')
    imagelist = ['pics/' + image for image in imageList]
    return render_template("index.html", imagelist=imagelist)


app.run()