#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
@author: Miles
@software: PyCharm
@file: cv_test3.py
@time: 2022/2/28 20:41
"""

import argparse
import cv2 as cv
import numpy as np
import imutils
# import myutils
from imutils import contours

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--img', required=True,
                help='path to input image')
ap.add_argument('-t', '--temp', required=True,
                help='path to template OCR-A image')
args = vars(ap.parse_args())

temp = cv.imread(args['temp'])

ref_origin = cv.resize(temp, (474, 66), interpolation=cv.INTER_AREA)

cv.imshow('temp', ref_origin)

ref = ref_origin.copy()

# 获取图像形状 返 行数值 列数值
h, w, _ = ref_origin.shape

ref = cv.cvtColor(ref, cv.COLOR_BGR2GRAY)
cv.imshow('gray1', ref)

ref = cv.threshold(ref, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]
cv.imshow('thresh', ref)

kernel = cv.getStructuringElement(cv.MORPH_RECT, (15, 1))

close = cv.morphologyEx(ref, cv.MORPH_CLOSE, kernel, iterations=2)


# ref_cnt = cv.findContours(ref.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
ref_cnt, hierarchy = cv.findContours(ref.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

cv.drawContours(ref_origin, ref_cnt, -1, (0, 0, 255), 2)
cv.imshow('GR', ref_origin)

ref_cnt = contours.sort_contours(ref_cnt, method='left-to-right')[0]
digits = {}

for (i, c) in enumerate(ref_cnt):
    (x, y, w, h) = cv.boundingRect(c)
    # cv.rectangle(ref_origin, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # roi = 255 - ref[y:y + h, x:x + w]
    roi = ref[y:y + h, x:x + w]
    roi = cv.resize(roi, (57, 88))

    digits[i] = roi

# cv.imshow('tt', digits[8])
#
#     # print(digits[i])
#     # print('-----------------')
#
#
# cv.imshow('ref and digits', ref_origin)
#
# for c in cnt:
#     x, y, w, h = cv.boundingRect(c)
#     ro = 255 - original[y:y + h, x:x + w]
#     cv.rectangle(temp, (x, y), (x + w, y + h), (36, 255, 12), 2)
#
#     break
#
# cv.imshow('close', close)
# cv.imshow('img', temp_1)
# cv.imshow('ro', digits[i])

# ---------------------------------------------------------------------------

rect_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (9, 3))
sq_kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))

# rect_kernel = cv.getStructuringElement(cv.MORPH_RECT, (9, 3))
# sq_kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))


origin = cv.imread(args["img"])
origin = imutils.resize(origin, width=600)

cv.imshow('origin', origin)

origin_frame = origin[3:39, 149:222]

image = origin_frame.copy()

gray_2 = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
cv.imshow("gray2", gray_2)

tophat = cv.morphologyEx(gray_2, cv.MORPH_TOPHAT, rect_kernel)
cv.imshow("tophat", tophat)

grad_x = cv.Sobel(tophat, ddepth=cv.CV_32F, dx=1, dy=0, ksize=-1)
grad_x = np.absolute(grad_x)
(min_val, max_val) = (np.min(grad_x), np.max(grad_x))

grad_x = (255 * ((grad_x - min_val) / (max_val - min_val)))
grad_x = grad_x.astype("uint8")
cv.imshow("gradient", grad_x)

grad_x = cv.morphologyEx(grad_x, cv.MORPH_CLOSE, rect_kernel)
cv.imshow("morphologyEx", grad_x)
thresh = cv.threshold(grad_x, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)[1]
cv.imshow("thresh1", thresh)

thresh = cv.morphologyEx(thresh, cv.MORPH_CLOSE, sq_kernel)
cv.imshow("thresh2", thresh)

cnt = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
cnt = imutils.grab_contours(cnt)
locs = []

for (i, c) in enumerate(cnt):
    (x, y, w, h) = cv.boundingRect(c)
    ar = w / float(h)

    print((x, y, w, h))
    print(ar)

    # if 1.75 < ar < 1.85:
    #     if (30 < w < 40) and (18 < h < 22):
    # if 1.75 < ar < 3.0:
    #     if (w == 59) and (h == 20):
    #         locs.append((x, y, w, h))
    #         cv.rectangle(origin, (x, y), (x + w, y + h), (255, 0, 0), -1)
    if h > 17:
        locs.append((x, y, w, h))
        cv.rectangle(origin_frame, (x, y), (x + w, y + h), (255, 0, 0), -1)

rows, cols = origin_frame.shape[:2]
roi = origin[:rows, :cols]
img2gray = cv.cvtColor(origin_frame, cv.COLOR_BGR2GRAY)
ret, mask = cv.threshold(img2gray, 10, 255, cv.THRESH_BINARY)
mask_inv = cv.bitwise_not(mask)
img1_bg = cv.bitwise_and(roi, roi, mask=mask_inv)
dst = cv.add(img1_bg, origin_frame)
origin[3:rows + 3, 149:cols + 149] = dst

cv.imshow("contours filter", origin)

locs = sorted(locs, key=lambda x: x[0])
output = []

for (i, (gx, gy, gw, gh)) in enumerate(locs):
    group_output = []

    group = gray_2[gy - 2:gy + gh + 2, gx - 2:gx + gw + 2]
    group = cv.resize(group, (126, 70), interpolation=cv.INTER_AREA)
    cv.imshow("group", group)

    group = cv.threshold(group, 0, 255, cv.THRESH_TOZERO | cv.THRESH_OTSU)[1]
    cv.imshow('group2', group)

    digit_cnt = cv.findContours(group.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    digit_cnt = imutils.grab_contours(digit_cnt)
    digit_cnt = contours.sort_contours(digit_cnt, method="left-to-right")[0]

    # digit_cnt, hierarchy = cv.findContours(group.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # digit_cnt = contours.sort_contours(digit_cnt, method="left-to-right")[0]

    max_cnt = list(filter(lambda s: cv.contourArea(s) >= 100, digit_cnt))

    for c in max_cnt:
    # for c in digit_cnt:
        (x, y, w, h) = cv.boundingRect(c)
        roi = group[y:y + h, x:x + w]
        roi = cv.resize(roi, (57, 88))

        scores = []

        for (digit, digitROI) in digits.items():
            result = cv.matchTemplate(roi, digitROI, cv.TM_CCOEFF)

            # min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            # scores.append(max_val)

            (_, max_score, _, _) = cv.minMaxLoc(result)
            scores.append(max_score)
#
        # print('scores: ', scores)
        print(scores)
        group_output.append(str(np.argmax(scores)))

    # print(len(group_output))

    print(group_output)

    cv.rectangle(image, (gx - 5, gy - 5), (gx + gw, gy + gh + 5), (0, 0, 255), 1)
    cv.putText(origin, ''.join(group_output), (gx + 145, gy + 50), cv.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
    # cv.putText(image, ''.join(group_output), (gx -10, gy + 10), cv.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)

    output.extend(group_output)

rows, cols = image.shape[:2]
roi = origin[:rows, :cols]
img2gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
ret, mask = cv.threshold(img2gray, 0, 255, cv.THRESH_BINARY)
mask_inv = cv.bitwise_not(mask)
img1_bg = cv.bitwise_and(roi, roi, mask=mask_inv)
dst = cv.add(img1_bg, image)
origin[3:rows + 3, 149:cols + 149] = dst

print('Diamond Value #: {}'.format(''.join(output)))
cv.imshow('im', origin)

##  -----------------------------------------------------------------------------------------

# img1 = origin
# img2 = origin_frame
#
# rows, cols = img2.shape[:2]
# roi = img1[:rows, :cols]
#
# img2gray = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
# ret, mask = cv.threshold(img2gray, 10, 255, cv.THRESH_BINARY)
# mask_inv = cv.bitwise_not(mask)
#
# img1_bg = cv.bitwise_and(roi, roi, mask=mask_inv)
# dst = cv.add(img1_bg, img2)
# img1[3:rows + 3, 149:cols + 149] = dst
#
# cv.imshow('px', img1)

##  -----------------------------------------------------------------------------------------

# words = []
# word_images = []
#
# for item in digit_cnt:
#     word = []
#     rect = cv.boundingRect(item)
#     x = rect[0]
#     y = rect[1]
#     weight = rect[2]
#     height = rect[3]
#     word.append(x)
#     word.append(y)
#     word.append(weight)
#     word.append(height)
#     words.append(word)
#
# words = sorted(words, key=lambda s:s[0], reverse=False)
# i = 0
#
# for word in words:
#     if (word[3] > (word[2] * 1.5)) and (word[3] < (word[2] * 3.5)) and (word[2] > 25):
#         i = i + 1
#         splite_image = image[word[1]:word[1] + word[3], word[0]:word[0] + word[2]]
#         word_images.append(splite_image)
#         print(i)
# del words[1]
# print(words)

##  -----------------------------------------------------------------------------------------

cv.waitKey(0)
