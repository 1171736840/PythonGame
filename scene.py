import json
import copy
import pygame
import function
from element.base import *

'''场景模块'''

class Scene(Element):
    '''场景类，统计json配置文件来加载指定场景，场景中有地图，怪物，主角等'''

    def __init__(self, src, data):
        '''通过json文件加载场景'''
        self.screen = data["screen"]    #屏幕对象image
        self.name = ""  # 场景名称
        self.backGroundMusic = ""  # 背景音乐
        self.map = None  # 地图
        self.followElement = None  # 自动跟随元素调整显示位置
        self.image = None
        self.rect = None
        self.area = None  # 绘制的可选区域，None为全部
        self.read(src, data)

    def read(self, src, data):
        '''通过json文件加载场景'''
        print("=====================================")
        print("读取场景配置：" + src)
        with open(src, "rb+") as file:
            self.__dict__.update(json.load(file))  # 把json所有属性值读入到类里面
        print("开始加载场景：" + self.name)
        # 加载场景中的元素
        for i in range(len(self.subElementList)):
            self.subElementList[i] = function.initElement(self.subElementList[i])  # 初始化元素,元素的子元素会自动初始化

        # 获取其它元素
        self.map = self.getElementByName(self.map)
        self.map.image = self.map.image.convert()  # 进行转换，加快绘制速度
        self.followElement = self.getElementByName(self.followElement)  # 自动跟随元素调整显示位置
        
        # 根据map生成底图
        self.rect = self.map.image.get_rect()
        # self.map.area = self.map.image.get_rect()
        # self.map.area.width = self.screen.rect.width
        # self.map.area.height = self.screen.rect.height

        # 加载声音资源
        pygame.mixer.music.load(self.backGroundMusic)  # 加载声音对象
        # pygame.mixer.music.play(loops=-1)  # 循环播放
        # pygame.mixer.music.get_busy()   # 检查音乐流是否正在播放
        # pygame.mixer.music.fadeout(1000)  # 淡出后停止播放音乐

    def draw(self,screen=None,rect=None):
        '''绘制场景'''
        if screen == None:
            screen = self.screen.screen
        if rect == None:
            rect = self.screen.rect
        
        for el in self.subElementList:
            if el == None:
                continue
            el.draw(screen,rect)  #绘制

    def update(self, data):
        for el in self.subElementList:
            if el == None:
                continue
            el.update(data)
        
        self.autoFollowElement(data)  #自动调整屏幕位置

    def autoFollowElement(self, data):
        '''自动跟随元素调整显示位置'''
        self.map.rect.x = self.screen.rect.width / 2 - self.followElement.rect.x
        self.map.rect.y = self.screen.rect.height / 2 - self.followElement.rect.y

        # 控制视角显示在地图内
        if self.map.rect.right < self.screen.rect.right:
            self.map.rect.right = self.screen.rect.right
        if self.map.rect.bottom < self.screen.rect.bottom:
            self.map.rect.bottom = self.screen.rect.bottom
        if self.map.rect.x > self.screen.rect.x:
            self.map.rect.x = self.screen.rect.x
        if self.map.rect.y > self.screen.rect.y:
            self.map.rect.y = self.screen.rect.y
