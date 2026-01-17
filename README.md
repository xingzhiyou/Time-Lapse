# 时隙 (Time-Lapse)

**时隙 (Time-Lapse)** 是一个基于 Python 的自动化脚本工具，通过 `pydirectinput` 实现对键盘和鼠标的高级控制。它支持毫秒级精度的操作、多时间轴并行运行、按键触发、窗口过滤以及管理员权限自动提升。

## 主要功能

- **极低延迟**：优化后的内核支持毫秒级操作，适合“零帧”级的高精度需求。
- **多触发模式**：
  - `OneShot`: 触发一次执行一次。支持异步触发，按下即执行，松开才重置。
  - `Loop`: 切换开关，循环执行。
  - `Hold`: 按住触发，松开停止（自动清理按键状态）。
- **多触发键支持**：单个时间轴支持绑定多个触发键（如 `Trigger: e, xbutton2`），任意一个被按下即可触发。
- **子时间轴调用**：支持在时间轴内部异步调用其他 `OneShot` 时间轴，实现复杂逻辑复用或同时执行。
- **窗口过滤**：支持指定目标窗口，只有当指定程序处于前台时脚本才会生效。
- **混合指令**：支持在同一毫秒内执行多个指令（用逗号分隔）。
- **外置配置**：按键映射表 (`key_mapping.json`) 和脚本配置 (`config.ini`) 均外置，方便维护。

## 快速开始

### 手动运行

#### 1. 安装依赖

确保你已经安装了 Python 3.6+ 环境，并安装必要的库：

```bash
pip install -r requirements.txt
```

#### 2. 运行程序

使用根目录下的 `run.py` 启动程序：

```bash
# 使用默认配置文件
python run.py

# 或指定配置文件
python run.py config.ini
```

## 配置文件说明 (`config.ini`)

### 全局设置
- `RequireAdmin = True`：如果设置为 True，程序启动时会自动请求管理员权限（解决部分游戏无法输入的问题）。

### 时间轴语法
```ini
[Timeline: 你的脚本名称]
Trigger: rbutton, xbutton2  ; 触发按键 (支持多键，用逗号分隔。支持 xbutton1/2 侧键)
Target: Arknights           ; 目标窗口标题关键词 (可选，不填则对所有窗口生效)
Mode: Hold                  ; 触发模式: OneShot / Loop / Hold
Remark: 备注说明
```

### 动作指令 (时间单位: 毫秒)
格式：`时间(ms) 指令 参数...`

| 指令 | 描述 | 示例 |
| :--- | :--- | :--- |
| `key_down` | 按下按键 | `0 key_down w` |
| `key_up` | 松开按键 | `500 key_up w` |
| `press_key` | 点击按键 | `0 press_key f` |
| `click_mouse` | 点击鼠标 | `0 click_mouse left` |
| `mouse_down` | 按下鼠标 | `10 mouse_down right` |
| `mouse_up` | 松开鼠标 | `20 mouse_up right` |
| `move_mouse` | 移动至绝对坐标 | `0 move_mouse 1920 1080` |
| `move_mouse_relative` | 相对移动 | `0 move_mouse_relative 0 -10` |
| `wait` | 强制等待 (秒) | `0 wait 0.5` |
| `run_timeline` | **异步调用**子时间轴 | `0 run_timeline 零帧部署` |

> **注意**：`run_timeline` 仅支持调用 `OneShot` 模式的时间轴。调用是异步的，主时间轴不会等待子时间轴结束，而是立即执行下一条指令，从而实现“同时执行”。

**高级技巧：单行多指令**
使用逗号 `,` 分隔，可在同一毫秒内执行多个操作：
```ini
10 mouse_down left, move_mouse_relative 0 -10
```

### 安全机制
为防止逻辑冲突和无限循环，**触发键 (Trigger)** 不能出现在该时间轴的动作指令中。如果配置了相同的键（例如用 `E` 触发 `press_key E`），脚本将拒绝执行并报错。

### 示例配置

```ini
RequireAdmin = True

[Timeline: 零帧部署]
Trigger: rbutton
Target: Arknights
Mode: Hold
Remark: 按住右键触发：松开左键 -> 按下ESC -> 10ms后按下左键并上滑
0 mouse_up left
0 key_down esc
10 mouse_down left, move_mouse_relative 0 -100
17 key_down esc

[Timeline: 组合技]
Trigger: f1
Mode: OneShot
Remark: 同时执行两个技能脚本
0 run_timeline 技能A
0 run_timeline 技能B
```

## 按键映射
项目根目录下的 `key_mapping.json` 文件包含了所有支持的按键名称（如 `f1`, `ctrl`, `left_click` 等）。
- 新增支持鼠标侧键：`xbutton1` (后退), `xbutton2` (前进)。

## 项目结构
- `run.py`: 启动入口。
- `config.ini`: 用户配置文件。
- `key_mapping.json`: 用户可编辑的按键映射表。
- `src/`: 核心代码目录。
- `requirements.txt`: 项目依赖列表。
- `README.md`: 项目说明文档。
- `LICENSE`: 许可证文件。

## 免责声明

本工具及其相关代码（以下简称“软件”）仅用于教育、研究和个人学习目的。在使用本软件之前，请务必仔细阅读并理解以下条款：

1. **自担风险**：使用本软件由用户自行决定，并自行承担风险。作者不对因使用本软件而导致的任何形式的损失、损害、账号封禁（包括但不限于游戏账号、应用账号等）或任何其他负面后果负责。
2. **合法性**：用户在使用本软件时，必须遵守所在国家/地区的法律法规以及所操作目标软件的服务协议。用户不得利用本软件从事任何非法活动或违反第三方协议的行为。
3. **无担保**：本软件按“原样”提供，不提供任何形式的明示或暗示保证。作者不保证软件的功能能满足您的所有需求，也不保证软件运行不会中断或没有错误。
4. **责任限制**：在任何情况下，作者均不对因使用或无法使用本软件而产生的任何直接、间接、偶然、特殊或惩罚性损害承担法律责任。

**一旦开始使用本软件，即表示您已阅读、理解并同意本声明的所有条款。**