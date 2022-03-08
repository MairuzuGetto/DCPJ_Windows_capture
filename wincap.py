#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
@author: Miles
@software: PyCharm
@file: win_cap.py
@time: 2022/2/11 22:17
"""


import numpy as np
import win32gui
import win32ui
import win32con


class WindowCapture:

    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    def __init__(self, window_name=None):
        # 捕捉句柄 判断
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception('Window not found: {}'.format(window_name))

        # 获取窗口大小, 捕捉左,上,右,下
        # 左[0],上[1],右[2],下[3]
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # 截取窗口裁剪
        # 边框,标题栏像素
        border_pixels = 8
        titlebar_pixels = 30
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # 实际屏幕位置
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    def get_screenshot(self):

        # 获取窗口图像数据
        wdc = win32gui.GetWindowDC(self.hwnd)
        dc_obj = win32ui.CreateDCFromHandle(wdc)
        cdc = dc_obj.CreateCompatibleDC()
        data_bit_map = win32ui.CreateBitmap()
        data_bit_map.CreateCompatibleBitmap(dc_obj, self.w, self.h)
        cdc.SelectObject(data_bit_map)
        cdc.BitBlt((0, 0), (self.w, self.h), dc_obj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # 数据转成OpenCV可读取
        # data_bit_map.SaveBitmapFile(cdc, 'debug.png')
        signed_ints_array = data_bit_map.GetBitmapBits(True)
        img = np.fromstring(signed_ints_array, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        dc_obj.DeleteDC()
        cdc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wdc)
        win32gui.DeleteObject(data_bit_map.GetHandle())

        # 删除Alpha通道
        img = img[..., :3]
        # 制作图像
        img = np.ascontiguousarray(img)

        return img

    @staticmethod
    def list_window_names():
        def win_enum_handler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(win_enum_handler, None)


    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)