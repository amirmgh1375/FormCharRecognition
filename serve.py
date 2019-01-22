from flask import Flask, flash, redirect, request, send_from_directory, url_for
from werkzeug.utils import secure_filename
import base64
import json
from subprocess import call
import os

import numpy as np
import cv2

from generate_dataset import CharRecognition

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
        
        return "ko"

def extractImagesFromForm():
    alfa_c = 0
    num_c = 0
    form_to_extract = os.path.join(form_path, 'form.jpg')
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

    print(alfa_c, num_c)





'''TODO: Use image without saving in disk'''
# def data_uri_to_cv2_img(encoded_data):
#     # encoded_data = uri.split(',')[1]
#     imgdata = base64.b64decode(encoded_data)
#     # nparr = np.fromstring(imgdata, np.uint8)
#     nparr = np.asarray(imgdata, dtype=np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     print(type(img))
#     cv2.imshow('image', img)
#     # return img


labels = ['Architect Campus', 'Buffet',
              'Computer Campus', 'Culture house', 'Field', 'Self']

# End-point to predict last uploded image
def predict(imgaddr):
    ''' predicts the last uploaded image an returns a string at last containing classes probability.'''
    global model
    img = cv2.imread(imgaddr)
    h, w, c = img.shape
    if w > h: # rotate image if it's in wrong orientation
      # rotation is done by ImageMagick so it sohuld be installed
      call(['mogrify', '-rotate', '90', 'uploads/imageToPredict.jpg'])
    img = image.load_img(imgaddr, target_size=(108, 192))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    if not model:
        print('------- loading model')
        model = load_model('PF-50-fixed 24-3-97.h5')
    features = model.predict(x)
    predicts = []
    for i, p in enumerate(features[0]):
        item = '%s Probability: %f' % (labels[i], p)
        predicts.append(item)
    predicts_string = '\n'.join(predicts)
    return predicts_string



# end-point to get the last image sent to predict
@app.route('/imagetopredict')
def uploaded_file():
    # images sent overwrite each other so there is only one image to get
    return send_from_directory('uploads/', 'imageToPredict.jpg')



# End-point to predict again last uploded image
@app.route('/predictagain')
def predict_again():
    f = predict('uploads/imageToPredict.jpg')
    return f


# RUN THE SERVER THING
if __name__ == '__main__':
    app.secret_key = 'abcakjlc-b@weubi_2b3!2@'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', port=8080)
