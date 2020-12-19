from flask import Flask, jsonify, request, render_template, redirect
import os
import subprocess, base64
import cv2
from PIL import Image
from classification.classification import predict

app = Flask(__name__)

app.config["IMAGE_UPLOADS"] = "/home/chetan/CyberLabs/alzheimer/alzheimer/web_app_with_ml_backend/input_imgs"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG"]
app.config["IMAGE_HEATMAP"] = "/home/chetan/CyberLabs/alzheimer/alzheimer/web_app_with_ml_backend/heat_map"


def image_2_heatmap(img_path, mask_path):
    print("img_path", img_path)
    print("mask_path", mask_path)
    img = cv2.imread(str(img_path), 0)
    img = cv2.resize(img, (208, 176), interpolation = cv2.INTER_CUBIC)
    heatmap=  cv2.imread(str(mask_path), 0)
    heatmap = cv2.resize(heatmap, (208, 176), interpolation = cv2.INTER_CUBIC)
    img = cv2.applyColorMap(img, cv2.COLORMAP_BONE)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_PINK)
    image = 0.6*img+0.4*heatmap
    return image


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
            name, ext = filename.split(".")
            
            if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
                os.chdir('ml_backend')
                subprocess.Popen(f'python3 api.py --file ../input_imgs/{filename}', shell=True)
                os.chdir('../') 
                img = image_2_heatmap(f'input_imgs/{name}.{ext}', f'output_imgs/{name}_predicted.{ext}')
                print(os.getcwd()+f'heatmap/{name}_map.{ext}')
                cv2.imwrite(os.path.join(app.config["IMAGE_HEATMAP"], f'{name}_map.{ext}'), img)
                with open(f'heat_map/{name}_map.{ext}', 'rb') as out_raw:
                    out_img64 = base64.b64encode(out_raw.read())
                out_img64 = out_img64.decode("utf-8")
                prediction = predict(f'input_imgs/{filename}', 'classification/saved_weight/current_checkpoint.pt')
                print(prediction)
                return render_template('upload_img.htm', predicted = True, imgData = out_img64, supplied_text = f'{prediction}')
            else:
                return "NON SUPPORTED FILE TYPE"
            return redirect(request.url)
    return render_template('upload_img.htm', predicted = False)

if __name__ == '__main__':
    app.run(debug=True)

