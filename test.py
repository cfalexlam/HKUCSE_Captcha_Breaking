"""
CHARACTERS = "345678bcdefghkmnprwxy"

from tensorflow.keras.models import load_model
model = load_model("./model/bestmodel.h5")


from PIL import Image
import numpy as np
prediction = model.predict(np.stack([np.array(Image.open("./captcha/data/2999.jpg"))/255.0]))

answer = ""
for predict in prediction:
        answer += CHARACTERS[np.argmax(predict[0])]

print(answer)
"""

import sys
from PIL import Image
from PIL import ImageFilter

def prepare_image(img):
    """Transform image to greyscale and blur it"""
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    if 'L' != img.mode:
        img = img.convert('L')
    return img

def remove_noise(img, pass_factor):
    for column in range(img.size[0]):
        for line in range(img.size[1]):
            value = remove_noise_by_pixel(img, column, line, pass_factor)
            img.putpixel((column, line), value)
    return img

def remove_noise_by_pixel(img, column, line, pass_factor):
    if img.getpixel((column, line)) < pass_factor:
        return (0)
    return (255)


if __name__=="__main__":
    input_image = "captcha/1_mod.jpg"
    output_image = "out_1.jpg"
    pass_factor = 100

    img = Image.open(input_image)
    img = prepare_image(img)
    img = remove_noise(img, pass_factor)
    img.save(output_image)