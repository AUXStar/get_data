#!/usr/bin/env python
# coding=utf-8
###
 # @FilePath     : /douyin/mouse/show.py
 # @Author       : njzy 48835121@qq.com
 # @Date         : 2024-06-30 13:09:04
 # @LastEditors  : njzy 48835121@qq.com
 # @LastEditTime : 2024-08-01 15:43:34
###


import matplotlib.pyplot as plt
import torch
import time
import random

a = time.time()
from mouse import rel_mouse

print((time.time() - a))
a = time.time()
for s in range(100):
    a, b = (
        random.randint(60, 100) * (-1, 1)[random.randint(0, 1)],
        random.randint(60, 100) * (-1, 1)[random.randint(0, 1)],
    )
    output = rel_mouse(a, b)
    points = torch.tensor(output)
    # print(output)
    x = points[:, 0].tolist()
    y = points[:, 1].tolist()
    # plt.xlim((0, 100))
    # plt.ylim((0, 100))
    plt.subplot(5, 20, s + 1)
    plt.plot(x, y)
print((time.time() - a))
plt.show()
