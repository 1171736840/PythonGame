
class Event():
    '''事件对象'''

    def __init__(self, setting):
        '''初始化事件对象'''
        self.event = None

    def update(self, data):
        '''更新事件'''
        pygame = data["pygame"]
        self.event = pygame.event.get()

        for e in self.event:
            if e.type == pygame.QUIT:  # 窗口关闭事件
                data["function"].gameExit(data)
            elif e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE: #ESC键退出
                data["function"].gameExit(data)
