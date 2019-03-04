from element.base import *
from element.role import *
import pygame
import function

class TreasureBox(Role):
    '''宝箱类'''
    def __init__(self, src=None, attribute=None, image=None, rect=None):
        # self.openObj =  
        # super().__init__(src=src, attribute=attribute, image=image, rect=rect)
        super().__init__(src=src, attribute=attribute)

    def onReady(self, data):
        super().onReady(data)
    
    def update(self, data):
        super().update(data)
        leadList = data["screen"].scene.getElementListByName("主角")
        i = self.rect.collidelist(leadList)
        if i > -1:
            function.showText("按E键打开宝箱", data, y=300)
            for e in data["event"].event:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_e:
                    self.remove()
                
        
