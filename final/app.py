from flask import Flask, jsonify, request, render_template, redirect
import os
import subprocess, base64


app = Flask(__name__)

app.config["IMAGE_UPLOADS"] = "/home/chetan/CyberLabs/alzheimer/flask_backend/input_imgs/"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG"]

#route to upload image

@app.route('/')
def home():
    return render_template('index.html')

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
                os.chdir('ml_backend')
                subprocess.Popen(f'python3 api.py --file ../input_imgs/{filename}', shell=True)
                os.chdir('../')
                out_img64 = base64.b64encode(out_raw.read())
                return render_template('upload_img.htm', predicted = True, imgData = out_img64, supplied_text = 'Hello')
            else:
                return "NON SUPPORTED FILE TYPE"
            return redirect(request.url)
    return render_template('upload_img.htm', predicted = False)

if __name__ == '__main__':
    app.run(debug=True)

