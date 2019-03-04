import pygame
import function
from setting import Setting
from screen import Screen
from event import Event
from scene import Scene
from gTime import GTime


def init():
    '''进行初始化操作'''
    pygame.init()  # 模块初始化
    setting = Setting()  # 实例化设置对象
    screen = Screen(setting, pygame)  # 创建屏幕对象
    event = Event(setting)  # 事件对象
    gTime = GTime()  # 游戏中的时间类
    return screen, setting, event, gTime

def main():
    '''入口主函数'''
    screen, setting, event, gTime = init()
    data = {"screen": screen, "setting": setting, "event": event,
            "function": function, "pygame": pygame, "exitFunction": [],
            "updateFunction": [], "gTime": gTime}

    function.initModule(setting.modulePath, data)  # 初始化各个自定义模块，如背包模块，任务模块
    screen.scene = Scene("resource/scene/长安城.json", data)  # 初始化场景
    screen.scene.onReady(data)
    print("=====================================")
    while True:
        gTime.update(data)  # 更新帧的时间
        event.update(data)  # 更新事件
        screen.update(data)  # 更新所有元素
        function.update(data)  # 更新注册的每个模块
        screen.draw()    # 绘制游戏画面
        function.limitFPS(data)  # 进行限制FPS

main()


    