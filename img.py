import numpy as np
import cv2
from PIL import Image

def convert_to_bw(img_path):
    #trim black border, image becomes 48*198
    original_image = cv2.imread(img_path, 0)
    nz = np.nonzero(original_image)  # Indices of all nonzero elements
    original_image = original_image[nz[0].min():nz[0].max()+1,
                    nz[1].min():nz[1].max()+1]

    original_image = np.delete(original_image, np.s_[155: 198], 1)
    original_image = np.delete(original_image, np.s_[0: 20], 1)

    ret, original_image  = cv2.threshold(original_image, 220, 255, cv2.THRESH_BINARY)
    
    original_image = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)

    pts1 = np.float32([[11, 0],[135, 0],[0, 48],[124,48]])  #(0, 13), (0, 134), (47, 0), (47, 121)
    pts2 = np.float32([[0,0],[135, 0],[0,48],[135,48]]) # (0, 0), (0, 134), (47, 0), (47, 134)

    M = cv2.getPerspectiveTransform(pts1, pts2)

    original_image = cv2.warpPerspective(original_image, M ,(135, 48))

    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    return original_image/255.0


if __name__ == "__main__":
    
    img1 = convert_to_bw("captcha/1.jpg") * 255.0
    img2 = convert_to_bw("captcha/2.jpg") * 255.0
    img3 = convert_to_bw("captcha/3.jpg") * 255.0

    #kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,6))
    #morph_img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    cv2.imwrite("try1.jpg", img1)
    cv2.imwrite("try2.jpg", img2)
    cv2.imwrite("try3.jpg", img3)

