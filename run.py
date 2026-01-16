import sys
import os
import ctypes

# 标准化导入：PyInstaller 可以静态分析出 src.control
try:
    from src.control import main_loop
except ImportError as e:
    print(f"Error: Failed to import core modules. {e}")
    sys.exit(1)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_admin_required(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip().lower()
                if line.startswith('requireadmin') and ('true' in line or 'yes' in line or '1' in line):
                    return True
    except:
        pass
    return False

if __name__ == "__main__":
    # 打印免责声明提示
    print("-" * 40)
    print("时隙 (Time-Lapse) 自动化工具")
    print("免责声明: 使用本软件即表示您同意 README.md 中的条款。")
    print("请仅用于教育与个人研究，勿用于违反第三方协议的行为。")
    print("-" * 40)

    # Determine base path
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    if len(sys.argv) < 2:
        # No argument provided, try to find config.ini in the base path
        default_config = os.path.join(base_path, 'config.ini')
        if os.path.exists(default_config):
            print(f"Auto-detected config file: {default_config}")
            config_path = default_config
        else:
            print("时隙 (Time-Lapse) 自动化工具")
            print("用法: python run.py <配置文件路径>")
            print(f"错误: 未提供参数且在 {base_path} 中找不到 config.ini")
            input("按回车键退出...")
            sys.exit(1)
    else:
        config_path = sys.argv[1]
    
    if not os.path.exists(config_path):
        print(f"错误: 找不到配置文件 '{config_path}'")
        input("按回车键退出...")
        sys.exit(1)

    # 检查并请求管理员权限
    if check_admin_required(config_path) and not is_admin():
        print("Config requires administrator privileges. Requesting...")
        
        # 判断是否为打包后的 exe 环境
        if getattr(sys, 'frozen', False):
            # PyInstaller 模式: sys.executable 是程序本身
            # 我们只需要传递后续的参数 (sys.argv[1:])
            params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        else:
            # 脚本模式: sys.executable 是 python.exe
            # 我们需要传递完整的参数 (sys.argv[0:]) 包括脚本路径
            params = " ".join([f'"{arg}"' for arg in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        
        sys.exit()
        
    main_loop(config_path)
