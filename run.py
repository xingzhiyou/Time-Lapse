import sys
import os

# 将 src 目录添加到模块搜索路径，以便导入 control 和 key_mapping
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from control import main_loop
except ImportError as e:
    print(f"Error: Failed to import core modules from src. {e}")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("时隙 (Time-Lapse) 自动化工具")
        print("用法: python run.py <配置文件路径>")
        print("示例: python run.py config.ini")
        sys.exit(1)
    
    config_path = sys.argv[1]
    if not os.path.exists(config_path):
        print(f"错误: 找不到配置文件 '{config_path}'")
        sys.exit(1)
        
    main_loop(config_path)
