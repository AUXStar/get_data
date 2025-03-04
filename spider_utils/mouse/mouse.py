#!/usr/bin/env python
# coding=utf-8
###
# @FilePath     : /douyin/mouse/mouse.py
# @Author       : njzy 48835121@qq.com
# @Date         : 2024-06-30 21:15:09
# @LastEditors  : njzy 48835121@qq.com
# @LastEditTime : 2024-08-05 16:11:59
###

from cv2 import dnn
import numpy as np
import random
from ..dirs import file_dir
net = dnn.readNetFromONNX(file_dir(__file__,"mouse.onnx"))


def rand(x):
    x[0] += random.randint(-100, 100) / 10
    x[1] += random.randint(-100, 100) / 10
    # print(x)
    return x


def rel_mouse(x, y):
    x1, y1 = rand([x, y])
    matblob = np.array([[x1, y1]])
    net.setInput(matblob)
    output = net.forward()[0]
    output = [[0, 0], *output, [x, y]]
    output = map(rand, output)
    output = np.array([[0, 0], *output, [x, y]])
    return output


def abs_mouse(fx, fy, tx, ty):
    return rel_mouse(tx - fx, ty - fy) + (fx, fy)
