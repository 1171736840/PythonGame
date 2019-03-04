import json
import time

import pygame

import function

class Element():
    '''元素类'''
    def __init__(self):
        self.parentElement = None  # 父元素
        self.subElementList = []  # 子元素列表
        self.index = 0  # 权重，在同级元素中数值越大后更新，同时也显示在页面最前面

    def onReady(self, data):
        '''当场景初始化完毕，开始update前调用'''
        for el in self.subElementList:
            el.onReady(data)

    def getElementByName(self, name):
        '''递归子元素，寻找第一个指定name值的子元素'''
        for el in self.subElementList:
            if el.name == name:
                return el
        # 遍历元素的子元素查找指定元素
        for el in self.subElementList:
            tempEl = el.getElementByName(name)
            if tempEl != None:
                return tempEl

        return None
    def getElementListByName(self, name, elementList=None):
        if elementList == None:
            elementList = []
        '''递归子元素，寻找name为指定值的子元素，并生成列表'''
        for el in self.subElementList:
            if el.name == name:
                elementList.append(el)
        # 遍历元素的子元素查找指定元素
        for el in self.subElementList:
            el.getElementListByName(name,elementList)
        
        return elementList

    def appendElement(self, element):
        '''删除子元素'''
        element.parentElement = self
        self.subElementList.append(element)
        self.sortElementList()

    def removeElement(self, element):
        '''删除子元素'''
        element.parentElement = None
        self.subElementList.remove(element)
    
    def remove(self):
        '''从父元素中删除自己，成功返回True'''
        if self.parentElement != None:
            self.parentElement.removeElement(self)
            return True
        else:
            return False

    def sortElementList(self):
        '''根据元素的index值调整元素位置，值越大越靠后'''
        self.subElementList.sort(key=lambda el: el.index)

    def setIndex(self, index):
        '''调整元素的index值'''
        self.index = index
        if self.parentElement != None:
            self.parentElement.sortElementList()
    


class Base(Element):
    '''基础元素类，游戏角色等一些类的基础类'''

    def __init__(self, src=None, attribute=None, image=None, rect=None):
        '''初始化，传入的attribute是个dict，是传入的属性值'''
        super().__init__()
        self.name = ""
        self.image = None  # pygame的image对象
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.area = None  # 绘制的可选区域，None为全部
        self.resource = {"image": {}, "sound": {}}  # 这个类的所有资源文件
        self.sound = {}  # 声音资源
        self.state = ""  # 状态left right up dwon none
        self.animation = {}  # 动画
        self.frameIndex = 0  # 当前动画的帧
        self.alpha = None  # 元素的通明度0-255，None表示禁用
        self.alphaDict = {}  # 保存所有图像的alphaList，用于再次计算alpha值
        self.lastFrameTime = None  # 取时间
        self.mask = None  #遮罩，用于碰撞检测
        self.maskColorKey = None  #遮罩通明键
        self.maskAlphaThreshold = None  #为alpha的阈值，低于阈值则视为透明
        
        if src != None:
            self.readByJson(src, attribute)  # 从json配置文件中加载资源
        if image != None:
            self.readByImage(image, rect=rect, attribute=attribute)  # 通过图片生成Base对象
        
        self.initMask()   #初始化mask，用于碰撞检测
    

    def readByImage(self, image, rect=None, attribute=None):
        '''根据image图片初始化对象'''
        self.state = "default"
        self.resource = {"image": {"defaultImage": image}}
        self.animation = {"default": {"frame": ["defaultImage"], "interval": 0}}
        if rect == None:
            self.rect = image.get_rect()
        else:
            self.rect = rect
        
        if attribute != None:
            self.__dict__.update(attribute)  # 将传入的属性加载到类里

        self.fristFrame()

    def readByJson(self, src, attribute=None):
        '''根据json文件从硬盘加载素材'''
        with open(src, "rb+") as file:
            self.__dict__.update(json.load(file))  # 把json所有属性值读入到类里面

        if attribute != None:
            self.__dict__.update(attribute)  # 将传入的属性加载到类里
        
        if type(self.rect) != pygame.Rect:
            rect = pygame.Rect(0, 0, 0, 0)
            self.rect = function.updateAttribute(rect, self.rect)   #更新rect的值
            
        # 加载图片资源文件
        path = src[:src.rfind("/")] + "/"

        if "image" in self.resource:
            for key, value in self.resource["image"].items():
                self.resource["image"][key] = pygame.image.load(
                    path + value)

        self.fristFrame()  # 初始帧时间，保证第一次会更新

        # 加载声音资源文件
        if "sound" in self.resource:
            for key, value in self.resource["sound"].items():
                self.resource["sound"][key] = pygame.mixer.Sound(
                    file=path + value)

        # 初始化子元素
        for i in range(len(self.subElementList)):
            self.subElementList[i] = function.initElement(
                self.subElementList[i])  # 加载元素
            self.subElementList[i].parentElement = self  # 置父元素

        self.sortElementList()  # 对列表进行的index值进行排序

    def update(self, data):
        '''更新状态'''
        self.updateFrame(data)
        self.updateElement(data)

    def updateElement(self, data):
        '''更新子元素'''
        for el in self.subElementList:
            if el == None:
                continue
            el.update(data)

    def changeState(self, state):
        '''修改状态'''
        self.state = state
        self.fristFrame()
        self.playSound(state)  # 播放对应的声音文件

    def updateFrame(self, data):
        '''更新帧'''
        interval = self.animation[self.state]["interval"]  # 获取当前动画的帧间隔
        if interval <= 0:
            return None  # 帧间隔小于0则不更新帧
        frame = self.animation[self.state]["frame"]

        t = data["gTime"].time  # 取时间
        if t - self.lastFrameTime > interval:
            # 切换下一帧
            self.frameIndex += 1  # 当前帧数加1
            if self.frameIndex >= len(frame):
                self.frameIndex = 0  # 播放完了切换到第一帧

            self.image = self.resource["image"][frame[self.frameIndex]]
            # self.rect = self.image.get_rect()
            rect = self.image.get_rect()
            self.rect.width = rect.width
            self.rect.height = rect.height

            self.lastFrameTime = t  # 保存当前帧的创建时间

    def fristFrame(self):
        '''生成第一帧'''
        frame = self.animation[self.state]["frame"]
        self.frameIndex = 0
        self.image = self.resource["image"][frame[self.frameIndex]]
        rect = self.image.get_rect()
        self.rect.width = rect.width
        self.rect.height = rect.height
        self.lastFrameTime = time.clock()  # 保存当前帧的创建时间

    def initMask(self):
        '''智能的加载Mask，用于碰撞检测'''
        if type(self.mask) == type(""):
            image = pygame.image.load(self.mask)
        elif self.mask == None:
            image = self.image
        
        self.mask = function.getImageMask(image, self.maskColorKey, self.maskAlphaThreshold)
        # print(self.name,self.mask)

    def playSound(self, soundName):
        '''播放指定声音'''
        if soundName in self.sound:  # 如果状态对应的声音存在则播放
            self.stopAllSound()  # 停止播放所有声音
            # self.resource["sound"][self.sound[soundName]].play()

    def stopAllSound(self):
        '''停止播放所有声音'''
        for key, value in self.resource["sound"].items():
            value.stop()

    def draw(self, image, parentDrawRect):
        '''将元素图像绘制在指定地方'''
        tempRect = self.rect.copy()
        tempRect.x += parentDrawRect.x
        tempRect.y += parentDrawRect.y
        image.blit(self.image, tempRect)

        for element in self.subElementList:
            element.draw(image, tempRect)

    def getDrawRect(self):
        '''获取绘制时的rect的复制对象'''
        if self.parentElement == None:
            return self.rect.copy()

        tempRect = self.parentElement.getDrawRect()
        tempRect.x += parentDrawRect.x
        tempRect.y += parentDrawRect.y
        return tempRect

    def setAlpha(self, alpha,fill=False):
        '''设置元素的透明度，0-255，None表示禁用'''

        for key, image in self.resource["image"].items():
            if key in self.alphaDict:
                alphaList = self.alphaDict[key]
            else:
                alphaList = None
            res = function.setAlpha(image, alpha, alphaList=alphaList, fill=fill)
            self.alphaDict[key] = res["alphaList"]

        self.alpha = res["alpha"]
        # print(alpha)

    def say(self, word):
        '''说出一段话并显示在屏幕上面'''
        for i in range(1):
            bubble = Bubble(word)
            bubble.rect.x = self.rect.width
            bubble.rect.bottom = len(
                self.subElementList) * (bubble.rect.height - 20)
            bubble.setTimeClose(3)
            bubble.index = len(self.subElementList)
            bubble.setAlpha(128)
            self.appendElement(bubble)
        print("{0}说：“{1}” x{2} y{3} w{4} h{5}".format(self.name, word,
                                                      bubble.rect.x, bubble.rect.y, bubble.rect.width, bubble.rect.height))


class Map(Base):
    '''游戏地图类'''
    def sortElementList(self):
        '''重写父类方法，用rect.bottom代替index进行排序'''
        self.subElementList.sort(
            key=lambda el: el.rect.bottom)  # 按照底边位置升序排列所有元素

    def update(self, data):
        '''根据游戏场景中的位置来计算显示的前后位置'''
        self.sortElementList()
        super().update(data)


class Bubble(Base):
    '''气泡类，类似于悬浮窗提示,可以自动销毁'''

    def __init__(self, word, closeTime=0, textColor=(255, 0, 0), bgColor=(0, 0, 0, 128), borderColor=(0, 0, 255), borderWidth=2):
        self.word = word
        self.name = word
        self.closeTime = 0
        fontImage, fontRect = function.drawText(word, textColor=(255, 0, 0))
        image = pygame.Surface((fontRect.width + borderWidth*2,
                                fontRect.height + borderWidth*2), flags=pygame.SRCALPHA)
        rect = image.get_rect()
        image.fill(bgColor)
        fontRect.x = borderWidth
        fontRect.y = borderWidth
        image.blit(fontImage, fontRect)

        if borderWidth > 0:
            tempRect = rect.copy()
            tempRect.x -= 1
            tempRect.y -= 1
            tempRect.width += 1
            tempRect.height += 1
            pygame.draw.rect(image, borderColor, tempRect,
                             borderWidth * 2)  # 绘制边框
        super().__init__(image=image, rect=rect)

    def setTimeClose(self, s):
        '''设置一段时间后销毁，单位秒'''
        self.createTime = time.clock()
        self.closeTime = s

    def update(self, data):
        if self.closeTime > 0 and data["gTime"].time - self.createTime > self.closeTime:
            self.parentElement.removeElement(self)
            return

        super().update(data)


class GaussianBlur(Base):
    '''高斯模糊背景类'''

    def __init__(self, width, height, left=0, top=0, color=(0, 0, 0), r=3, alpha=128):
        
        '''r高斯模糊半径'''
        image = function.createImage(width, height, color)
        super().__init__(image=image)
        self.setAlpha(alpha,fill=True)
        self.rect = pygame.Rect(left, top, width, height)
        self.r = r  # 模糊半径

    def draw(self, image, parentDrawRect):
        '''将元素图像绘制在指定地方'''
        tempRect = self.rect.copy()
        tempRect.x += parentDrawRect.x
        tempRect.y += parentDrawRect.y

        function.blur(image, tempRect, r=self.r)
        image.blit(self.image, tempRect)
        # 绘制子元素
        for element in self.subElementList:
            element.draw(image, tempRect)
