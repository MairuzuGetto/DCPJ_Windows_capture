#!/usr/bin/env python
# -*- coding=utf-8 -*-


## 导入模块
import numpy as np
import win32gui
import win32ui
import win32con


## WindowCapture类别
class WindowCapture:

    
    ## 宣告变数
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0
    
    
    ## 定义类别变数初始化, "__" 开头函数为私有, 不得外部使用与访问
    ## __init__ 必须使用 类别(class)
    ## self 类别(class)下 引用变数 需带上self 例: self.hwnd
    ## window_name 变量 未输入 默认 None
    def __init__(self, window_name=None):
        
        ## 捕捉句柄 判断
        if window_name is None:
            
            ## 判断句柄参数为 None 返回 桌面窗口的句柄(显示整个屏幕)
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            
            ## 判断句柄参数有值
            ## FindWindow 两个参数 第一个通常为None即可, 第二个视窗标题名
            self.hwnd = win32gui.FindWindow(None, window_name)
            
            ## 判断视窗查无标题名, 则显示未找到
            if not self.hwnd:
                raise Exception('Window not found: {}'.format(window_name))
        
        ## GetWindowRect 函数 返回 指定的窗口边框矩形尺寸
        ## 获取窗口大小, 捕捉左, 上, 右, 下
        ## 左[0], 上[1], 右[2], 下[3]
        window_rect = win32gui.GetWindowRect(self.hwnd)
        
        ## 窗口宽为 右半边 减 左半边
        self.w = window_rect[2] - window_rect[0]
        
        ## 窗口高为 下半部 减 上半部
        self.h = window_rect[3] - window_rect[1]

        ## 截取窗口裁剪
        ## 边框, 标题栏像素
        ## border_pixels 为左, 右, 下的距离为8
        ## titlebar_pixels 为上 含整个标题栏 距离为30
        border_pixels = 8
        titlebar_pixels = 30
        
        
        ## 最终窗口宽 为 宽 减 左右边溢出的区域
        self.w = self.w - (border_pixels * 2)
        
        ## 最终窗口高 为 高 减 标题栏与下方溢出的区域
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        ## 实际屏幕位置
        # self.offset_x = window_rect[0] + self.cropped_x
        # self.offset_y = window_rect[1] + self.cropped_y
        
        
    ## 截取即时窗口画面
    def get_screenshot(self):

        ## 获取窗口图像数据
        ## 获取整个窗口的DC 处理
        wdc = win32gui.GetWindowDC(self.hwnd)
        
        dc_obj = win32ui.CreateDCFromHandle(wdc)
        cdc = dc_obj.CreateCompatibleDC()
        
        ## 保存位图 处理
        data_bit_map = win32ui.CreateBitmap()
        data_bit_map.CreateCompatibleBitmap(dc_obj, self.w, self.h)
        cdc.SelectObject(data_bit_map)
        
        ## 将像素进行区域转换
        ## 将矩形区域拷贝到目标区域
        cdc.BitBlt((0, 0), (self.w, self.h), dc_obj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        ## 数据转成OpenCV可读取
        signed_ints_array = data_bit_map.GetBitmapBits(True)
        img = np.fromstring(signed_ints_array, dtype='uint8')
        img.shape = (self.h, self.w, 4)
        
        ## 清除 释放记忆体
        dc_obj.DeleteDC()
        cdc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wdc)
        win32gui.DeleteObject(data_bit_map.GetHandle())

        ## 删除Alpha通道
        img = img[..., :3]
        # 制作图像
        img = np.ascontiguousarray(img)

        return img
