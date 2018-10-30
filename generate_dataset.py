import os
import cv2
import math
import numpy as np
from pprint import pprint
from operator import itemgetter
from tqdm import tqdm

class CharRecognition:

    def __init__(self, path):
        self.image = cv2.imread(path)
        self.strighted_image = self.set_image_horizontal(self.image)

    def detect_eyes(self, image):
        image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(image_gray, (7, 7), 0)
        blur = cv2.GaussianBlur(blur, (3, 3), 0)
        kernel = np.ones((5,5),np.uint8)
        closing = cv2.morphologyEx(blur, cv2.MORPH_CLOSE, kernel)
        ret,thresh = cv2.threshold(closing,227,255,cv2.THRESH_BINARY)
        self.detected_eyes = []
        _, contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) == 4:
                screenCnt = approx
                if cv2.contourArea(cnt) > 3500.0 and cv2.contourArea(cnt) < 4300.0:
                    [x, y, w, h] = cv2.boundingRect(cnt)
                    self.detected_eyes.append(cnt)
                    cv2.drawContours(image, [cnt], 0, (0, 0, 255), 3)
                    # cv2.putText(image, str(cv2.contourArea(cnt)), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 2)
        (self.detected_eyes, boundingBoxes) = self.sort_contours(self.detected_eyes)
        return image, self.detected_eyes

    def get_rows(self, image, detected_eyes):
        cropped = []
        for cnt2, cnt1 in zip(*[iter(detected_eyes)]*2):
            if cv2.boundingRect(cnt1)[0] < cv2.boundingRect(cnt2)[0]:
                [x1, y1, w1, h1] = cv2.boundingRect(cnt1)
                [x2, y2, w2, h2] = cv2.boundingRect(cnt2)
            else:
                [x1, y1, w1, h1] = cv2.boundingRect(cnt2)
                [x2, y2, w2, h2] = cv2.boundingRect(cnt1)
            cropped.append(image[y1 -50:y2 + 90, x1:x2+w2])
        return cropped
            # cv2.imwrite('cropped_area/area_' + str(c) + '.jpg', cropped)

    def get_lines_mask(self, binary):
        """ uses binary mask and returns lines mask """

        binary = binary.astype(np.uint8)

        binary = cv2.morphologyEx(binary, cv2.MORPH_DILATE, np.ones((2, 2), np.uint8), iterations=2)
        horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, np.ones((1, 60), np.uint8), iterations=1)
        vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, np.ones((60, 1), np.uint8), iterations=1)
        combined = horizontal | vertical
        
        segmented = cv2.morphologyEx(combined, cv2.MORPH_DILATE, np.ones((2, 2), np.uint8), iterations=2)
        # segmented = cv2.morphologyEx(segmented, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8), iterations=2)

        # filter small contours
        _,contours, _ = cv2.findContours(segmented, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.ones(segmented.shape[:2], dtype=np.uint8) * 255
        for contour in contours:
            _, _, w, h = cv2.boundingRect(contour)
            if w < 300 and h < 300:
                cv2.drawContours(mask, [contour], -1, 0, -1)

        filtered = cv2.bitwise_and(segmented, segmented, mask=mask)

        return np.bitwise_not(filtered * 255) > 0

    def get_grade_alfabet(self, image):
        image = cv2.resize(image, (2225, 140))
        return image[:, 125:800]

    def get_grade_number(self, image):
        image = cv2.resize(image, (2225, 140))
        coords = [(840, 950), (950, 1060), (1060, 1170), (1205, 1320), (1315, 1430)]
        cropped = []
        for i in coords:
            cropped.append(image[:, i[0]:i[1]])
        return cropped

    def set_image_horizontal(self, image):
        # calculate image rotated angle
        img_edges = cv2.Canny(image, 100, 100, apertureSize=3)
        lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0,
                                100, minLineLength=100, maxLineGap=5)
        angles = []
        for x1, y1, x2, y2 in lines[0]:
            # cv2.line(img_before, (x1, y1), (x2, y2), (255, 0, 0), 3)
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            angles.append(angle)
        median_angle = np.median(angles)
        if median_angle > 45 or median_angle < -45:
            median_angle = 90 + median_angle
        # rotate image by madian_angle detected
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, median_angle, 1.0)
        strighted_image = cv2.warpAffine(
            image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
        # set image to horizontal
        return strighted_image

    def get_contour(self, image, x, y, x_max, y_max, area_tresh, height_tresh, _list):
            # image = image[y:y_max, x:x_max]
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(image, (5, 5), 0)
        image = cv2.adaptiveThreshold(blur, 255, 1, 1, 31, 12)
        _, contours, _ = cv2.findContours(
            thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv2.contourArea(cnt) > area_tresh:
                [x, y, w, h] = cv2.boundingRect(cnt)
                if h > height_tresh:
                    _list.append([x, y, w, h])
                    roi = thresh[y:y+h, x:x+w]
                    roismall = cv2.resize(roi, (10, 10))
        return _list, image

    def sort_contours(self, cnts, method="top-to-bottom"):
        # initialize the reverse flag and sort index
        reverse = False
        i = 0
        # handle if we need to sort in reverse
        if method == "right-to-left" or method == "bottom-to-top":
            reverse = True
        # handle if we are sorting against the y-coordinate rather than
        # the x-coordinate of the bounding box
        if method == "top-to-bottom" or method == "bottom-to-top":
            i = 1
        # construct the list of bounding boxes and sort them from top to
        # bottom
        boundingBoxes = [cv2.boundingRect(c) for c in cnts]
        (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key=lambda b:b[1][i], reverse=reverse))
        # return the list of sorted contours and bounding boxes
        return (cnts, boundingBoxes)


if __name__ == "__main__":

    forms_path = os.path.join('Forms')
    grade_alfabet = os.path.join('grade_alfabet')
    grade_number = os.path.join('grade_number')
    password = os.path.join('password')
    # from_py_py = os.path.join('from_py_py')
    # till_py_py = os.path.join('till_py_py')

    if not os.path.exists(grade_alfabet):
        os.makedirs(grade_alfabet)
    if not os.path.exists(grade_number):
        os.makedirs(grade_number)
    if not os.path.exists(password):
        os.makedirs(password)

    forms = []
    for sub_folder in os.listdir(forms_path):
        for img in os.listdir(os.path.join(forms_path, sub_folder)):
            forms.append(os.path.join(forms_path, sub_folder, img))
    # forms = [os.path.join(forms_path, sub_folder, img) for img in os.listdir(os.path.join(forms_path, sub_folder)) for sub_folder in os.listdir(forms_path)]
    
    alfa_c = 0
    num_c = 0
    for form in tqdm(forms):
        if form.split('.')[1] == 'jpg':
            CharRecognition_object = CharRecognition(form)
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
