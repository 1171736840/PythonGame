import pygame
import function
from element.base import *

image = None
g = None

def initModule(data):
    '''游戏初始化完成时，用于初始化各个模块的函数，用于绑定事件'''
    print("初始化模块函数，用于绑定事件")
    data["updateFunction"].append(update)  # 绑定事件
    data["exitFunction"].append(gameExit)  # 绑定事件
    global image

    text = "测试字符串"
    fontImage, fontRect = function.drawText(text, textColor=(0, 255, 0), bgColor=(0, 0, 0), x=200, y=200)
    # fontImage.set_alpha(128)
    image = Base(image=fontImage, rect=fontRect)
    # image.setAlpha(128)
    #高斯模糊相关测试
    print(image.rect)


def update(data):
    global image, g

    data["screen"].tempElementList.append(image)
    # alpha = int(data["gTime"].time * 10) * 4
    # if alpha > 255:
    #     alpha = 255 - (int(data["gTime"].time * 10) * 4 - 255)
        
    for e in data["event"].event:
        if e.type == pygame.KEYDOWN and e.key == pygame.K_q:
            image.setAlpha(128)
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_w:
            image.setAlpha(255)
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_m:
            if g == None:
                screen = data["screen"]
                width = screen.rect.width
                height = 150
                x = 0
                y = screen.rect.height - height
                g = GaussianBlur(width, height, left=x, top=y)

                screen.scene.appendElement(g)
            else:
                g.remove()
                g = None

        elif e.type == pygame.KEYDOWN and e.key == pygame.K_j:
            if g != None:
                g.r += 1
            print(g.r)
        
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_k:
            if g != None:
                g.r -= 1
                if g.r < 1:
                    g.r = 1
                print(g.r)

        # elif e.type == pygame.KEYDOWN and e.key == pygame.K_u:
        #     g.kernelSize = (g.kernelSize[0] + 2, g.kernelSize[1] + 2)
        #     print(g.kernelSize)
        # elif e.type == pygame.KEYDOWN and e.key == pygame.K_i:
        #     g.kernelSize = (g.kernelSize[0] - 2, g.kernelSize[1] - 2)
        #     print(g.kernelSize)
    


def gameExit(data):
    '''游戏退出时调用的函数'''
    print("游戏退出时调用的函数")
