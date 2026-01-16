# 时隙 (Time-Lapse)

**时隙 (Time-Lapse)** 是一个基于 Python 的自动化脚本工具，通过 `pydirectinput` 实现对键盘和鼠标的高级控制。它支持多时间轴并行运行、按键触发、窗口过滤以及管理员权限自动提升。

## 主要功能

- **多时间轴并行**：支持同时定义并运行多个独立的操作序列。
- **按键触发**：可以为每个时间轴设置独立的物理按键触发器（如 F1, F2 等）。
- **窗口过滤**：支持指定目标窗口，只有当指定程序处于前台时脚本才会生效。
- **管理员提权**：配置文件可选开启管理员模式，以支持在高权限应用（如部分游戏）中进行输入模拟。
- **外置按键映射**：按键码字典独立存放，方便用户自行扩展和维护。

## 快速开始

### 1. 安装依赖

确保你已经安装了 Python 3.6+ 环境，并安装必要的库：

```bash
pip install pydirectinput
```

### 2. 运行程序

使用根目录下的 `run.py` 启动程序，并传入你的配置文件路径：

```bash
python run.py config.ini
```

## 配置文件说明 (`.ini` / `.txt`)

配置文件采用类似 INI 的格式，支持多个 `[Timeline]` 块。

### 全局设置
- `RequireAdmin = True`：如果设置为 True，程序启动时会请求管理员权限。

### 时间轴设置
- `[Timeline: 备注名]`：定义一个新时间轴。
- `Trigger`: 触发按键（参考 `src/key_mapping.py` 中的定义）。
- `Target`: 目标窗口标题关键词。设置为 `ALL` 或不设置则全域生效。
- `Remark`: 脚本功能的简要说明。

### 动作指令
格式：`时间(毫秒) 指令 参数...`

| 指令 | 描述 | 示例 |
| :--- | :--- | :--- |
| `key_down` | 按下按键 | `0 key_down w` |
| `key_up` | 松开按键 | `2000 key_up w` (2秒后松开) |
| `press_key` | 点击按键 | `500 press_key f` |
| `click_mouse` | 点击鼠标 | `0 click_mouse left` |
| `mouse_down` | 按下鼠标 | `0 mouse_down right` |
| `mouse_up` | 松开鼠标 | `1 mouse_up right` |
| `move_mouse` | 移动至坐标 | `0 move_mouse 1920 1080` |
| `move_mouse_relative` | 相对移动 | `0 move_mouse_relative 100 0` |

### 示例配置

```ini
RequireAdmin = True

[Timeline: 自动奔跑]
Trigger: f1
Target: ALL
Remark: 按下F1开始自动奔跑
0 key_down w
5 key_up w

[Timeline: 记事本测试]
Trigger: f2
Target: 记事本
Remark: 只有在记事本在前台时才有效
0 press_key h
0.1 press_key e
0.2 press_key l
0.3 press_key l
0.4 press_key o
```

## 项目结构

- `run.py`: 项目启动入口。
- `src/control.py`: 核心逻辑实现（解析配置、按键监听、时间轴调度）。
- `src/key_mapping.py`: Windows 虚拟键码映射表。
