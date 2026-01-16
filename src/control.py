import pydirectinput
import time

# 设置 PyDirectInput 的一些基本配置
# PAUSE 设置为 0 可以让指令发送得更快，但有些游戏/程序可能需要一点延迟才能识别
pydirectinput.PAUSE = 0.01

def key_down(key: str):
    """
    按下指定按键。
    
    Args:
        key (str): 按键名称，例如 'a', 'enter', 'shift' 等。
    """
    pydirectinput.keyDown(key)

def key_up(key: str):
    """
    松开指定按键。
    
    Args:
        key (str): 按键名称，例如 'a', 'enter', 'shift' 等。
    """
    pydirectinput.keyUp(key)

def press_key(key: str, presses: int = 1, interval: float = 0.0):
    """
    按下并松开指定按键（即点击按键）。
    
    Args:
        key (str): 按键名称。
        presses (int): 点击次数，默认为 1。
        interval (float): 每次点击之间的间隔时间，默认为 0.0。
    """
    pydirectinput.press(key, presses=presses, interval=interval)

def mouse_down(x: int = None, y: int = None, button: str = 'left'):
    """
    按下鼠标按键。
    
    Args:
        x (int, optional): 鼠标按下时的 X 坐标。如果为 None，则在当前位置按下。
        y (int, optional): 鼠标按下时的 Y 坐标。如果为 None，则在当前位置按下。
        button (str): 鼠标按键，可选 'left', 'middle', 'right'。默认为 'left'。
    """
    pydirectinput.mouseDown(x=x, y=y, button=button)

def mouse_up(x: int = None, y: int = None, button: str = 'left'):
    """
    松开鼠标按键。
    
    Args:
        x (int, optional): 鼠标松开时的 X 坐标。如果为 None，则在当前位置松开。
        y (int, optional): 鼠标松开时的 Y 坐标。如果为 None，则在当前位置松开。
        button (str): 鼠标按键，可选 'left', 'middle', 'right'。默认为 'left'。
    """
    pydirectinput.mouseUp(x=x, y=y, button=button)

def click_mouse(x: int = None, y: int = None, clicks: int = 1, interval: float = 0.0, button: str = 'left'):
    """
    点击鼠标。
    
    Args:
        x (int, optional): 点击位置的 X 坐标。
        y (int, optional): 点击位置的 Y 坐标。
        clicks (int): 点击次数，默认为 1。
        interval (float): 点击间隔，默认为 0.0。
        button (str): 鼠标按键，'left', 'middle', 'right'。
    """
    pydirectinput.click(x=x, y=y, clicks=clicks, interval=interval, button=button)

def move_mouse(x: int, y: int, duration: float = 0.0):
    """
    移动鼠标到绝对坐标 (x, y)。
    
    Args:
        x (int): 目标 X 坐标。
        y (int): 目标 Y 坐标。
        duration (float): 移动耗时，默认为 0.0（瞬间移动）。
    """
    pydirectinput.moveTo(x, y, duration=duration)

def move_mouse_relative(x_offset: int, y_offset: int, duration: float = 0.0):
    """
    相对当前位置移动鼠标。
    
    Args:
        x_offset (int): X 轴偏移量。
        y_offset (int): Y 轴偏移量。
        duration (float): 移动耗时。
    """
    pydirectinput.move(x_offset, y_offset, duration=duration)

if __name__ == "__main__":
    # 简单的测试代码
    print("PyDirectInput 封装库已加载。")
    # 可以在这里添加测试调用，例如：
    # move_mouse(500, 500)
    # press_key('a')
