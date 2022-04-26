from cv2 import cv2
import numpy as np
import tensorflow as tf

def prediction(img, model):
    NUMBERS = '345678'
    LETTERS = 'bcdefghkmnprwxy'
    labels = np.array(list(NUMBERS + LETTERS))
    
    img_list = preprocess(img)
    pred_labels = labels[np.argmax(model.predict(img_list), axis=1)]
    prediction = ''.join(pred_labels)
    
    return prediction

def preprocess(img):
    img_list = []
    
    # clip dark pixels to 0
    img = np.where(img < 240, 0, img)
    
    # straighten italic letters
    pts1 = np.float32([[11, 0],[135, 0],[0, 48],[124,48]])
    pts2 = np.float32([[0,0],[135, 0],[0,48],[135,48]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    img = cv2.warpPerspective(img, M ,(200, 50))
    
    # only letters are left after transformation
    # find boundary
    left_bound = 0
    right_bound = img.shape[1]

    for i in range(200):
        if img[:,i].max() > 150:
            left_bound = i
            break
    
    for i in range(200)[::-1]:
        if img[:,i].max() > 150:
            right_bound = i
            break     
            
    # crop boundary
    img = img[:, left_bound:right_bound+1]
    
    cols = [0]*7
    cols[6] = img.shape[1]
    
    # take right 3 numbers with 20 px
    for i in range(3):
        cols[5-i] = img.shape[1] - (i+1)*20

    # split remaining letters into 3 segments
    for i in range(2):
        cols[i+1] = (i+1)*((img.shape[1]-60)//3)

    for i in range(6):
        img_cropped = img[:, cols[i]:cols[i+1]]
        
        # resize to 50x30 px
        width = 30
        height = img_cropped.shape[0] # keep original height
        dim = (width, height)
        img_cropped = cv2.resize(img_cropped, dim, interpolation = cv2.INTER_AREA)
        
        # normalize to 0-1
        img_cropped = img_cropped/255

        # convert to float32
        img_cropped = img_cropped.astype(np.float32)
        
        img_list.append(img_cropped)
    
    img_list = np.asarray(img_list)
    img_list = np.expand_dims(img_list, axis=3)
    
    return img_list