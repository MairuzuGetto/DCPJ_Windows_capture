#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
@author: Miles
@software: PyCharm
@file: env.py
@time: 2022/2/20 11:49
"""

import win32gui
from wincap import WindowCapture
import json


cap_name = 'Destiny Child'


win_cap = WindowCapture(cap_name)

screenshot = win_cap.get_screenshot()

hwnd = win32gui.FindWindow(None, cap_name)


with open('test.json', encoding='utf-8') as data_json:
    read_content = json.load(data_json)
