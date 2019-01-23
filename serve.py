from flask import Flask, flash, redirect, request, send_from_directory, url_for, jsonify
from werkzeug.utils import secure_filename
import base64
import json
from subprocess import call
import os

import numpy as np
import cv2

from generate_dataset import CharRecognition
from ocr import predict

# define server app and model
app = Flask(__name__)

form_path = os.path.join('form_to_predict')
grade_alfabet = os.path.join(form_path, 'grade_alfabet')
grade_number = os.path.join(form_path, 'grade_number')

if not os.path.exists(grade_alfabet):
    os.makedirs(grade_alfabet)
if not os.path.exists(grade_number):
    os.makedirs(grade_number)

# Serving index.html from WebApp folder
@app.route('/')
def Root():
    return send_from_directory('WebApp', 'index.html')

# Serving Static files
@app.route('/<path:path>')
def send_js(path):
    return send_from_directory('WebApp', path)

@app.route('/form_to_predict/<path:path>')
def send_imgs(path):
    return send_from_directory('form_to_predict', path)

# Upload image and call extraction and prediction functions
@app.route('/predict', methods=['POST'])
def upload():
    ''' uploads image and call predict for it.'''
    if request.method == 'POST':
        # Save Image as file
        filename = 'formToPredict.jpg'
        destination = os.path.join(form_path, filename)
        for file in request.files.getlist("file"):
            file.save(destination)
        
        extractImagesFromForm()
        out = predict()
        return jsonify(out)

def extractImagesFromForm():
    alfa_c = 0
    num_c = 0
    form_to_extract = os.path.join(form_path, 'formToPredict.jpg')
    try:
        CharRecognition_object = CharRecognition(form_to_extract)
        image, detected_eyes = CharRecognition_object.detect_eyes(CharRecognition_object.strighted_image)
        image_rows = CharRecognition_object.get_rows(image, detected_eyes)
        # print(form)
        # print(len(detected_eyes))
        # print(len(test_img))
        for row in image_rows:
            cv2.imwrite(grade_alfabet + '/' + str(alfa_c) + '.jpg', CharRecognition_object.get_grade_alfabet(row))
            for char in CharRecognition_object.get_grade_number(row):
                cv2.imwrite(grade_number + '/' + str(num_c) + '.jpg', char)
                num_c += 1
            alfa_c += 1  
    except:
        print('image type error !!')
        return -1

    print(alfa_c, num_c)



# # end-point to get the last image sent to predict
# @app.route('/imagetopredict')
# def uploaded_file():
#     # images sent overwrite each other so there is only one image to get
#     return send_from_directory('uploads/', 'imageToPredict.jpg')



# # End-point to predict again last uploded image
# @app.route('/predictagain')
# def predict_again():
#     f = predict('uploads/imageToPredict.jpg')
#     return f


# RUN THE SERVER THING
if __name__ == '__main__':
    app.secret_key = 'abcakjlc-b@weubi_2b3!2@'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', port=8080)
