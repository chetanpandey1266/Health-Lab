from flask import Flask, jsonify, request, render_template, redirect
import os

app = Flask(__name__)

app.config["IMAGE_UPLOADS"] = "/home/chetan/Coding/Python/flask/"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG"]

#route to upload image

@app.route('/')
def home():
    return redirect('/upload-image')

@app.route('/<link>')
def notfound(link):
    if(link != 'upload-image'):
        return '404 NOT FOUND'
    else:
        return redirect('/upload-image')

@app.route('/upload-image', methods=['GET', 'POST'])
def upload_img():
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            if(image.filename == ''):
                return "NO FILE UPLOADED"
            filename =image.filename
            ext = filename.rsplit(".", 1)[1]
            if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
                # here we can run our api function
                # aur iske neeche hi render kra denge output
            else:
                return "NON SUPPORTED FILE TYPE"
            return redirect(request.url)
    return render_template('upload_img.htm')

