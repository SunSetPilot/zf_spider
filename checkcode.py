from keras.models import load_model
from PIL import Image
import numpy as np
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"]='3'

boxs = [(5, 1, 17, 21), (17, 1, 29, 21), (29, 1, 41, 21), (41, 1, 53, 21)]
dic_ = {0: 'r', 1: 'u', 2: '9', 3: '0', 4: '7', 5: 'i', 6: 'n', 7: 'g', 8: '6', 9: 'z', 10: '1', 11: '8', 12: 't',
        13: 's', 14: 'a', 15: 'f', 16: 'o', 17: 'h', 18: 'm', 19: 'j', 20: 'c', 21: 'd', 22: 'v', 23: 'q', 24: '4',
        25: 'x', 26: '3', 27: 'e', 28: 'b', 29: 'k', 30: 'l', 31: '2', 32: 'y', 33: '5', 34: 'p', 35: 'w'}
app = load_model('net.h5')


def verify(filename):
    img = Image.open(filename).convert('L').convert('1')
    code = ''
    for x in range(len(boxs)):
        aaa = []
        roi = img.crop(boxs[x])
        roi = np.array(roi)
        aaa.append([roi])
        aaa = np.array(aaa)
        aaa = app.predict(aaa)
        code += dic_[np.argmax(aaa)]
    return code
