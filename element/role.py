from element.base import *
import pygame
import random
import math
import function

class Role(Base):
    '''主角类'''

    def __init__(self, src=None, attribute=None):       
        self.x = 0  # 元素的X坐标
        self.y = 0  # 元素的Y坐标
        self.speed = 0  # 移动速度像素每秒
        self.yMove = 0  # y轴上的位移分量
        self.jumpState = False  #跳跃状态
        self.jumpMove = 3   #跳跃的位移分量
        self.gravity = 9.8  # 重力加速度
        self.previousTime = 0  # 上一帧自由落体的位置
        self.freeFallerStartTime = None  # 自由落体开始时间
        self.autoControl = False  #自动控制
        self.userControl = False  #用户控制
        super().__init__(src=src, attribute=attribute)

    def initMask(self):
        '''重新初始化mask方法，用于与地图碰撞检测'''
        self.maskDict = {}
        for key, value in self.resource["image"].items():
            mask = pygame.mask.Mask(value.get_size())
            mask.fill() #填充1，表示有值
            self.maskDict[key] = mask

    def __setattr__(self, name, value):
        '''对属性进行赋值时，对xy属性进行检测，使位置能够及时更新'''
        super().__setattr__(name, value)
        if name == "x" and hasattr(self, "rect"):
            self.rect.x = value
        elif name == "y" and hasattr(self, "rect"):
            self.rect.y = value

    def __getattribute__(self, name):
        '''对属性进行取值，检测xy，使其能与rect的值进行同步'''
        if name == "x" and hasattr(self, "rect"):
            if self.rect.x != int(self.__dict__["x"]):
                self.__dict__["x"] = self.rect.x            
        elif name == "y" and hasattr(self, "rect"):
            if self.rect.y != int(self.__dict__["y"]):
                self.__dict__["y"] = self.rect.y
        elif name == "mask":
            self.__dict__["mask"] = self.maskDict[self.animation[self.state]["frame"][self.frameIndex]]
        return super().__getattribute__(name)

    def freeFaller(self,t):
        '''计算元素的自由落体'''
        if self.previousTime == 0:
            self.previousTime = t
            return
        self.yMove += self.gravity * (t - self.previousTime)
        self.y += self.yMove
        self.previousTime = t
        
    def autoControlRole(self, data):
        '''自动控制角色'''

        if self.state == "left":
            self.x -= data["gTime"].intervalTime * self.speed
        elif self.state == "right":
            self.x += data["gTime"].intervalTime * self.speed
        if self.x > 1540:
            self.changeState("left")
        if self.x < 0:
            self.changeState("right")

    def update(self, data):
        super().update(data)
        
        if self.autoControl == True:
            self.autoControlRole(data)
        if self.userControl == True:
            self.move(data)

        self.freeFaller(data["gTime"].time)
        self.mapConstraint(data)   

    def mapConstraint(self, data):
        '''对游戏角色进行地图约束，使其位置符号常理'''
        mapRect = data["screen"].scene.map.rect

        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.bottom > mapRect.height:
            self.rect.bottom = mapRect.height
        if self.rect.right > mapRect.width:
            self.rect.right = mapRect.width


        x = self.rect.x
        y = self.rect.y
        othermask = self.mask
        mask = data["screen"].scene.map.mask
        
        while True:
            dy = mask.overlap_area(othermask, (x, y + 1)) - mask.overlap_area(othermask, (x, y - 1))
            if dy == 0:
                break
            if dy > 0:  #底部碰撞，向上移动
                self.rect.y -= 1
                self.yMove = 0
                self.jumpState = False  #落地后可以取消跳跃状态
            else:
                self.rect.y += 1
                self.yMove = 0
            y = self.rect.y

        while True:
            dx = mask.overlap_area(othermask, (x + 1, y)) - mask.overlap_area(othermask, (x - 1, y))
            if dx == 0:
                break
            if dx > 0:  #右边碰撞，向左移动
                self.rect.x -= 1
                
            else:
                self.rect.x += 1
            x = self.rect.x

    def move(self, data):
        '''主角移动函数'''
        for e in data["event"].event:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_LEFT:
                self.changeState("left")
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_RIGHT:
                self.changeState("right")
            
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_UP:
                self.changeState("up")
            
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_DOWN:
                self.changeState("down")
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                if not self.jumpState: 
                    self.yMove -= self.jumpMove
                    self.jumpState = True
            elif e.type == pygame.KEYUP and e.key == pygame.K_s:
                self.say("我是：" + self.name)
            elif e.type == pygame.KEYUP and e.key == pygame.K_a:
                self.setAlpha(random.randint(0,255))
                
            elif e.type == pygame.KEYUP and e.key == pygame.K_f:
                self.x = 200
                self.y = 200
            
            elif e.type == pygame.KEYUP and e.key == pygame.K_g:
                print(self.mask)
            elif e.type == pygame.KEYUP and e.key == pygame.K_LEFT and self.state == "left":
                self.changeState("stand_left")

            elif e.type == pygame.KEYUP and e.key == pygame.K_RIGHT and self.state == "right":
                self.changeState("stand_right")

            elif e.type == pygame.KEYUP and e.key == pygame.K_UP and self.state == "up":
                self.changeState("stand_left")

            elif e.type == pygame.KEYUP and e.key == pygame.K_DOWN and self.state == "down":
                self.changeState("stand_right")
            # elif e.type == pygame.MOUSEBUTTONDOWN:
            #     print("鼠标按下", e)
            # elif e.type == pygame.MOUSEBUTTONUP:
            #     print("鼠标放开", e)
            # elif e.type == pygame.MOUSEMOTION:
            #     print("鼠标移动", e)

        if self.state == "left":
            self.x -= data["gTime"].intervalTime * self.speed

            # print(data["gTime"].intervalTime * self.speed, self.rect.x, self.x)
        elif self.state == "right":
            self.x += data["gTime"].intervalTime * self.speed

            # print(data["gTime"].intervalTime * self.speed, self.rect.x, self.x)
        elif self.state == "up":
            self.y -= data["gTime"].intervalTime * self.speed

        elif self.state == "down":
            self.y += data["gTime"].intervalTime * self.speed


        
        
