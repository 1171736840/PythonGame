import time


class GTime():
    '''游戏中的时间类，用于获取每一帧的时间间隔，当前时间等等'''

    def __init__(self):
        '''初始化'''
        self.intervalTime = 0  # 与上一帧的间隔时间
        self.time = time.clock()  # 当前时间
        self.lastFrameTime = 0  # 上一帧时间

    def update(self, data):
        self.lastFrameTime = self.time
        self.time = time.clock()
        self.intervalTime = self.time - self.lastFrameTime
