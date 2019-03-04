import sys
import traceback

class Screen():
    '''屏幕类用来管理绘制屏幕图像'''

    def __init__(self, setting, pygame):
        '''初始化'''
        self.pygame = pygame
        if setting.fullScreenDisplay:
            # pygame.HWSURFACE  #硬件加速，#仅全屏模式
            # pygame.DOUBLEBUF  #双缓冲
            # pygame.FULLSCREEN #全屏显示
            self.screen = pygame.display.set_mode(
                (setting.screenWidth, setting.screenHeight), pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)  # 创建屏幕,表示全屏
        else:
            self.screen = pygame.display.set_mode((setting.screenWidth, setting.screenHeight),pygame.DOUBLEBUF)
        self.rect = self.screen.get_rect()
        self.elementList = []  # 要绘制在屏幕上的元素
        self.tempElementList = []  # 要临时绘制在屏幕上的元素
        self.scene = None  # 场景
        pygame.display.set_caption(setting.screenTitle)  # 设置屏幕标题

    def update(self, data):
        '''更新屏幕内容'''
        elementList = [self.scene]
        elementList.extend(self.elementList)
        elementList.extend(self.tempElementList)
        for element in elementList:
            # try:
            #     if element == None:
            #         continue
            element.update(data)
            # except Exception as e:
            #     e.print_stack()
            #     print(e)
            #     print("更新失败，跳过")

    def draw(self):
        # self.scene.draw()   #绘制场景
        elementList = [self.scene]
        elementList.extend(self.elementList)
        elementList.extend(self.tempElementList)
        
        for element in elementList:
            # try:
            #     # print(element.rect)
            if element == None:
                continue
            element.draw(self.screen,self.rect)  #绘制
            #     # self.screen.blit(element.image, element.rect)  # 绘制
            # except Exception as e:
            #     traceback.print_stack()
            #     print(e)
            #     print("绘制错误，跳过")

        # self.pygame.display.flip()  # 更新显示
        self.pygame.display.update()  # 更新显示

        self.tempElementList = []  #清空临时元素列表



