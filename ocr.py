from fastai.imports import *
from fastai.transforms import *
from fastai.conv_learner import *
from fastai.model import *
from fastai.dataset import *
from fastai.sgdr import *
from fastai.plots import *

import os

# model path and input size 
model_path = "form_to_predict"
sz         = 100

# cuda and cudnn available check
# print('torch.cuda.is_available : ', torch.cuda.is_available())
# print('torch.backends.cudnn.enabled : ', torch.backends.cudnn.enabled)


# load model
arch         = resnet34
data         = ImageClassifierData.from_paths(model_path, tfms=tfms_from_model(arch, sz))
learn        = ConvLearner.pretrained(arch, data, precompute=False)
learn.load('224_model_all')

# learn.summary()

def predict():
  # predict on single image
  predictions = []
  images = [os.path.splitext(name)[0] for name in os.listdir(os.path.join(model_path, 'grade_number'))]
  images.sort(key=int)
  for image in images:
    image_path = os.path.join(model_path, 'grade_number', f'{image}.jpg')
    Image.open(image_path).resize((100, 100))
    # Method 2 fastai for prediction
    trn_tfms, val_tfms = tfms_from_model(arch, sz)
    im = val_tfms(open_image(image_path)) # open_image() returns numpy.ndarray
    preds = learn.predict_array(im[None])
    predictions.append(learn.data.classes[np.argmax(preds)])
  return predictions



