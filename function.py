import importlib
from cv2 import cv2
import os
import sys
import time
import math
import numpy
import pygame

from element.base import Base

# 定义全局变量
fontDict = {}  # 字体字典


def gameExit(data):
    '''退出游戏'''
    print("=====================================\n执行退出函数")
    for fun in data["exitFunction"]:
        fun(data)

    print("退出游戏")
    sys.exit()  # 使用系统模块退出游戏


def update(data):
    '''更新每一帧'''
    for fun in data["updateFunction"]:
        fun(data)


def initModule(modulePath, data):
    '''初始化各个自定义模块，如背包模块，任务模块'''
    print("=====================================")
    for root, dirs, files in os.walk(modulePath):
        # root当前目录路径 dirs当前路径下所有子目录 files当前路径下所有非目录子文件
        for file in files:
            if file[-8:] == "_main.py":
                moduleName = root.replace("\\", ".") + "." + file[:-3]
                try:
                    module = importlib.import_module('.', moduleName)  # 加载指定模块
                    # 如果模块中有initModule函数存在
                    if hasattr(module, "initModule") or type(module.initModule) == type(type):
                        module.initModule(data)  # 调用初始化函数
                        print("模块初始化成功：" + moduleName)
                    else:
                        print("未找到模块初始化函数'initModule'：" + moduleName)
                except:
                    print("模块初始化失败：" + moduleName)


def initElement(el):
    '''初始化场景里面的元素'''
    moduleName = el["class"][:el["class"].rfind(".")]  # 获取py模块名称
    className = el["class"][el["class"].rfind(".") + 1:]  # 获取类名
    jsonSrc = el["json"]  # 获取配置文件路径
    print("加载元素：" + moduleName + "." + className + " 配置文件：" + jsonSrc)
    module = importlib.import_module('.', moduleName)  # 加载指定模块
    Entity = getattr(module, className)  # 在模块中获得指定类
    entity = Entity(src=jsonSrc, attribute=el["attribute"])  # 实列化类
    # print(vars(entity))
    return entity


def updateAttribute(obj, attrDict):
    '''根据attrDict的值更新obj的属性'''
    for key, value in attrDict.items():
        if hasattr(obj, key):
            setattr(obj, key, value) 
    return obj


def limitFPS(data):

    # time.sleep(0.1)
    # return
    '''限制FPS'''
    limitFPS = data["setting"].limitFPS  # 获取限制的最大FPS
    thisFrameTime = time.clock()  # 获取当前时间，作为当前帧的生成时间

    # if limitFPS > 0:
    #     lastFrameTime = data["lastFrameTime"]  # 获取上一帧的生成时间
    #     maxOutTime = 1 / limitFPS  # 根据最大FPS计算最大延迟时间，单位秒
    #     actualOutTime = thisFrameTime - lastFrameTime  # 实际耗时，单位秒
    #     print(actualOutTime, int(1 / actualOutTime), maxOutTime - actualOutTime, thisFrameTime,end=" ")
    #     if actualOutTime < maxOutTime:
    #         time.sleep(maxOutTime - actualOutTime)  # 进行延迟操作
    #         print("延迟")
    #     else:
    #         print("")
    if "lastFrameTime" in data:
        # 计算耗时，毫秒
        c = int((thisFrameTime - data["lastFrameTime"]) * 100000) / 100
        if c > 0:
            # print(c, int(1000 / c))  # 输出耗时及帧数
            text = "耗时:" + str(c) + "ms FPS:" + str(int(1000 / c))
            fontImage, fontRect = drawText(text, textColor=(
                0, 255, 0), bgColor=(0, 0, 0), x=0, y=0)
            # fontImage.set_alpha(128)
            image = Base(image=fontImage, rect=fontRect)
            # image.setAlpha(128)
            data["screen"].tempElementList.append(image)
    data["lastFrameTime"] = thisFrameTime  # 记录时间，单位秒

def showText(text, data, x=0, y=0):
    '''显示一段文字在屏幕上'''
    fontImage, fontRect = drawText(text, textColor=(0, 255, 0), bgColor=(0, 0, 0), x=x, y=y)
    image = Base(image=fontImage, rect=fontRect)
    data["screen"].tempElementList.append(image)

def drawText(text, image=None, font=None, fontName="font/wryh.ttf", size=24, textColor=(255, 255, 255), bgColor=None, x=0, y=0):
    '''将一行文本绘制在image上font和fontName可传入任意一个，背景默认为透明'''

    if font == None:
        global fontDict
        if fontName not in fontDict:
            font = pygame.font.Font(fontName, size)  # 字体对象为空则创建字体对象
            fontDict[fontName] = font  # 将字体保存到字典中，方便下次使用
            print("生成字体对象：" + fontName)
        else:
            font = fontDict[fontName]

    fontImage = font.render(text, True, textColor, bgColor)  # 根据文本生成图片
    fontRect = fontImage.get_rect()  # 获取矩形对象
    fontRect.x = x
    fontRect.y = y
    if image != None:
        image.blit(fontImage, fontRect)  # 将文本图片绘制在指定image上
    return fontImage, fontRect


def isGlobalAlpha(image):
    '''判断是否使用了全局alpha通道'''
    return image.get_flags() == pygame.SRCALPHA and (image.get_alpha() == None or image.get_alpha() == 255)


def setAlpha(image, alpha, alphaList=None, fill=False):
    '''设置元素的透明度，0-255，None表示禁用,alphaList按每个像素的alpha百分比计算，长度为0则自动创建alphaList'''
    arr = None
    if alpha > 255:
        alpha = 255
    elif alpha < 0:
        alpha = 0

    if isGlobalAlpha(image):
        '''表示原本就有alpha通道'''
        arr = pygame.surfarray.pixels_alpha(image)
        if fill:
            arr[:, :] = alpha  # 指定对所有像素填充固定的alpha值
        else:
            if type(alphaList) != numpy.ndarray:
                # 创建float类型的副本，防止计算是类型不统一报错
                alphaList = arr.astype(numpy.float)

            tempArr = alphaList.copy()  # 再次创建副本，防止污染原始数据
            tempArr[:, :] *= alpha / 255  # 根据百分比计算每个alpha像素的值
            arr[:, :] = tempArr  # 对所有像素alpha进行复制，类型会自动转换

    else:
        '''表示使用的是全局alpha'''
        if alpha == 255:
            alpha = None
        image.set_alpha(alpha)

    return {
        "alpha": alpha,
        "alphaList": alphaList,
        "newAlphaList": arr
    }


def blur(image, rect, r=3, kernelSize=(0, 0)):
    '''对图像指定区域进行处理，r为模糊半径，r为4在某些边缘会出现颜色bug
        flag:0高斯模糊，1均值模糊，2中值模糊，3双边模糊'''
    arr = pygame.surfarray.pixels3d(image)[rect.x:rect.x + rect.width, rect.y:rect.y + rect.height]
    arr[:, :, :] = cv2.GaussianBlur(src=arr,ksize=kernelSize, sigmaX=r)  # 高斯模糊
    # pass
    # if flag == 0:
    #     arr[:, :, :] = cv2.GaussianBlur(arr, kernelSize, r)  # 高斯模糊
    # elis flag == 1:
    #     arr[:, :, :] = cv2.blur(arr, kernelSize)  # 均值模糊
    # elis flag == 2:
    #     arr[:, :, :] = cv2.medianBlur(arr, r)  # 中值模糊
    # elis flag == 3:
    #     arr[:, :, :] = cv2.bilateralFilter(arr, 9, 75, 75)    # 双边模糊

def createImage(width, height, color):
    '''创建image'''
    #判断是否有alpha通道
    if len(color) == 4:
        flags = pygame.SRCALPHA
    else:
        flags = 0
    image = pygame.Surface((width, height), flags=flags)
    image.fill(color)
    return image
    

def freeFaller(t):
    '''计算自由落体'''
    return 0.5*9.8*math.pow(t, 2)

def showMask(mask):
    '''把mask遮罩转换成image图片，方便显示'''
    width, height = mask.get_size()
    print("宽度{0}，高度{1}".format(width,height))
    arr = numpy.zeros(( height,width))
    for x in range(width):
        for y in range(height):
            arr[y, x] = mask.get_at((x, y))

    cv2.imshow("Image"+str(time.clock()), arr)
    
def getImageMask(image, colorKey=None,alphaThreshold=None):
    '''获取image的遮罩，用于碰撞检测,alphaThreshold为alpha的阈值，低于阈值则视为通明'''
    mask = None
    if colorKey != None:
        image = image.copy()
        image.set_colorkey(colorKey)
        mask = pygame.mask.from_surface(image, 1)
    elif alphaThreshold != None:
        mask = pygame.mask.from_surface(image, alphaThreshold)
    
    return mask
    
