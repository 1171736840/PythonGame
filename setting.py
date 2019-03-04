class Setting():
    '''游戏所有设置'''

    def __init__(self):
        '''初始化'''
        self.screenTitle = "游戏"
        self.screenWidth = 1366
        self.screenHeight = 768
        self.fullScreenDisplay = False#全屏显示
        # self.backgroundColor = (0, 0, 0)
        self.modulePath = "module"  # 要导入的模块路径列表，不要带.py后缀，用“.”表示“/”，如背包模块，任务模块
        self.limitFPS = 10  #要限制的最大FPS，0为不限制
        
