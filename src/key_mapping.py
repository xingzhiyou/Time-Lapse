# Windows Virtual Key Codes for GetAsyncKeyState
# https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
import json
import os

import sys

# Default mapping (fallback)
VK_MAPPING = {
    'lbutton': 0x01, 'rbutton': 0x02, 'mbutton': 0x04,
    # Aliases for mouse buttons
    'mouse_left': 0x01, 'left_click': 0x01,
    'mouse_right': 0x02, 'right_click': 0x02,
    'mouse_middle': 0x04, 'middle_click': 0x04,

    'back': 0x08, 'tab': 0x09, 'clear': 0x0C, 'enter': 0x0D,
    'shift': 0x10, 'ctrl': 0x11, 'alt': 0x12, 'pause': 0x13, 'caps_lock': 0x14,
    'esc': 0x1B, 'space': 0x20, 'page_up': 0x21, 'page_down': 0x22,
    'end': 0x23, 'home': 0x24, 'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
    # Aliases for arrow keys to avoid confusion
    'arrow_left': 0x25, 'arrow_up': 0x26, 'arrow_right': 0x27, 'arrow_down': 0x28,

    'print_screen': 0x2C, 'insert': 0x2D, 'delete': 0x2E,
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46,
    'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C,
    'm': 0x4D, 'n': 0x4E, 'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52,
    's': 0x53, 't': 0x54, 'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58,
    'y': 0x59, 'z': 0x5A,
    'lwin': 0x5B, 'rwin': 0x5C,
    'numpad0': 0x60, 'numpad1': 0x61, 'numpad2': 0x62, 'numpad3': 0x63,
    'numpad4': 0x64, 'numpad5': 0x65, 'numpad6': 0x66, 'numpad7': 0x67,
    'numpad8': 0x68, 'numpad9': 0x69,
    'multiply': 0x6A, 'add': 0x6B, 'separator': 0x6C, 'subtract': 0x6D, 'decimal': 0x6E, 'divide': 0x6F,
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74, 'f6': 0x75,
    'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
    'num_lock': 0x90, 'scroll_lock': 0x91,
}

# Determine the directory where the application is running
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle (PyInstaller)
    base_path = os.path.dirname(sys.executable)
else:
    # If the application is run as a script
    # This file is in src/, so we want the parent directory (project root)
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Try to load external JSON configuration from the base path
json_path = os.path.join(base_path, 'key_mapping.json')

if os.path.exists(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            custom_mapping = json.load(f)
            # Update/Override the default mapping with custom values
            # Normalize keys to lowercase for consistency
            for k, v in custom_mapping.items():
                VK_MAPPING[k.lower()] = v
        print(f"[System] Loaded external key mapping from {json_path}")
    except Exception as e:
        print(f"[Warning] Failed to load {json_path}: {e}")