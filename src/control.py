import pydirectinput
import time
import sys
import threading
import ctypes
import re
import os
from src.key_mapping import VK_MAPPING

# --- Configuration & Constants ---
pydirectinput.PAUSE = 0.0  # Set to 0 for minimum latency

class Timeline:
    def __init__(self, name="Unnamed"):
        self.name = name
        self.trigger_keys = [] # List of trigger keys
        self.target_window = None  # None or "ALL" means all, otherwise partial title match
        self.remark = ""
        self.actions = []  # List of tuples: (timestamp, command, args)
        
        # New attributes for modes
        self.mode = "oneshot"  # 'oneshot', 'loop', 'hold'
        self.loop_interval = 0.1
        
        # Runtime state
        self.loop_stop_event = None
        self.loop_thread = None
        self.is_running = False # Flag to prevent overlapping executions for OneShot/Hold

    def __repr__(self):
        return f"<Timeline '{self.name}' Triggers: {self.trigger_keys} Mode: {self.mode}>"

# --- Core Functions ---

def get_active_window_title():
    """获取当前前台窗口的标题"""
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value

def key_check(key_name):
    """
    检查某个键是否被按下。
    使用 Windows API GetAsyncKeyState.
    """
    if not key_name:
        return False
    vk = VK_MAPPING.get(key_name.lower())
    if vk is None:
        if len(key_name) == 1:
            vk = ord(key_name.upper())
        else:
            return False
    
    return (ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000) != 0

def parse_config(file_path: str):
    timelines = []
    current_timeline = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Ignore global config keys that are handled separately
                if line.lower().startswith('requireadmin'):
                    continue

                # Parse Timeline Header
                timeline_match = re.match(r'^\[Timeline(?::\s*(.*))?\]$', line, re.IGNORECASE)
                if timeline_match:
                    name = timeline_match.group(1) or f"Timeline_{len(timelines)+1}"
                    current_timeline = Timeline(name)
                    timelines.append(current_timeline)
                    continue

                if current_timeline is None:
                    current_timeline = Timeline("Default")
                    timelines.append(current_timeline)

                # Parse Key-Value Pairs
                if '=' in line or ':' in line:
                    if not line[0].isdigit():
                        parts = re.split(r'[:=]', line, 1)
                        key = parts[0].strip().lower()
                        value = parts[1].strip()
                        
                        if key == 'trigger':
                            # Support multiple keys separated by comma
                            keys = [k.strip().lower() for k in value.split(',') if k.strip()]
                            current_timeline.trigger_keys.extend(keys)
                            continue
                        elif key == 'remark' or key == 'description':
                            current_timeline.remark = value
                            continue
                        elif key == 'name':
                            current_timeline.name = value
                            continue
                        elif key == 'target' or key == 'window':
                            current_timeline.target_window = value
                            continue
                        elif key == 'mode':
                            mode_val = value.lower()
                            if 'loop' in mode_val: current_timeline.mode = 'loop'
                            elif 'hold' in mode_val: current_timeline.mode = 'hold'
                            else: current_timeline.mode = 'oneshot'
                            continue
                        elif key == 'interval' or key == 'loopinterval':
                            try:
                                current_timeline.loop_interval = float(value)
                            except ValueError:
                                pass
                            continue

                # Parse Actions
                # Split the line into Timestamp and the Rest
                parts = line.split(maxsplit=1)
                if len(parts) >= 2:
                    try:
                        # Treat first column as milliseconds, convert to seconds internally
                        timestamp = float(parts[0]) / 1000.0
                        actions_str = parts[1]
                        
                        # Split multiple actions by comma
                        action_groups = actions_str.split(',')
                        
                        for action_str in action_groups:
                            action_parts = action_str.strip().split()
                            if not action_parts:
                                continue
                                
                            command = action_parts[0]
                            args = action_parts[1:]
                            current_timeline.actions.append((timestamp, command, args))
                            
                    except ValueError:
                        pass

    except FileNotFoundError:
        print(f"Error: Config file not found: {file_path}")
        return []

    for t in timelines:
        t.actions.sort(key=lambda x: x[0])
    
    return timelines

def execute_action_wrapper(command, args, all_timelines=None):
    """Wrapper to call pydirectinput functions safely."""
    try:
        if command == 'key_down':
            if args: pydirectinput.keyDown(args[0])
        elif command == 'key_up':
            if args: pydirectinput.keyUp(args[0])
        elif command == 'press_key':
            if args: pydirectinput.press(args[0])
        elif command == 'mouse_down':
            button = args[0] if args else 'left'
            pydirectinput.mouseDown(button=button)
        elif command == 'mouse_up':
            button = args[0] if args else 'left'
            pydirectinput.mouseUp(button=button)
        elif command == 'click_mouse':
            button = args[0] if args else 'left'
            pydirectinput.click(button=button)
        elif command == 'move_mouse':
            if len(args) >= 2:
                pydirectinput.moveTo(int(args[0]), int(args[1]))
        elif command == 'move_mouse_relative':
            if len(args) >= 2:
                pydirectinput.move(int(args[0]), int(args[1]))
        elif command == 'wait':
             if args: time.sleep(float(args[0]))
        elif command == 'run_timeline':
            if not all_timelines:
                print("  [Error] run_timeline called but timeline list not available.")
                return
            
            target_name = " ".join(args).strip()
            target_t = next((t for t in all_timelines if t.name.lower() == target_name.lower()), None)
            
            if target_t:
                if target_t.mode == 'oneshot':
                    if not target_t.is_running:
                        print(f"  [Action] Starting async timeline '{target_t.name}'...")
                        target_t.is_running = True # Mark as running to prevent re-entry
                        threading.Thread(target=run_timeline_once, args=(target_t, None, all_timelines)).start()
                    else:
                        print(f"  [Warn] Skipped async call to '{target_t.name}': already running.")
                else:
                    print(f"  [Warn] Cannot call timeline '{target_name}' because it is not OneShot.")
            else:
                print(f"  [Warn] Timeline '{target_name}' not found.")
        else:
            print(f"  [Warn] Unknown command: {command}")
    except Exception as e:
        print(f"  [Error] Failed to execute {command} {args}: {e}")

# --- Execution Logic for Different Modes ---

def run_timeline_once(timeline: Timeline, active_trigger_key: str, all_timelines: list = None):
    """Standard OneShot execution."""
    # Safety Check: Prevent trigger key from being used in actions to avoid recursive loops/conflicts
    if active_trigger_key:
        trigger_key_lower = active_trigger_key.lower()
        for _, command, args in timeline.actions:
            if args and args[0].lower() == trigger_key_lower:
                if command in ['key_down', 'press_key', 'key_up']:
                    print(f"[Error] Timeline '{timeline.name}' conflict: Trigger key '{active_trigger_key}' cannot be used in actions.")
                    timeline.is_running = False
                    return

    print(f"[Action] '{timeline.name}' (OneShot) started. Triggered by: {active_trigger_key}")
    
    def wait_for_release(t: Timeline, trigger_key: str):
        if trigger_key:
            # Wait for key to be released (with debounce)
            while True:
                if not key_check(trigger_key):
                    time.sleep(0.05)
                    if not key_check(trigger_key):
                        break
                time.sleep(0.01)
        t.is_running = False
        print(f"[Action] '{t.name}' finished and ready for next trigger.")

    try:
        start_time = time.perf_counter()
        for timestamp, command, args in timeline.actions:
            target_time = start_time + timestamp
            while True:
                current_time = time.perf_counter()
                if current_time >= target_time:
                    break
                wait_time = target_time - current_time
                if wait_time > 0.002:
                     time.sleep(wait_time - 0.001)

            execute_action_wrapper(command, args, all_timelines)
            
    finally:
        # Start release monitor in background so actions can finish independently
        if active_trigger_key:
             threading.Thread(target=wait_for_release, args=(timeline, active_trigger_key), daemon=True).start()
        else:
             timeline.is_running = False
def run_timeline_loop(timeline: Timeline, stop_event: threading.Event, all_timelines: list = None):
    """Loop execution until stop_event is set."""
    # timeline.is_running = True <-- Handled in main_loop now
    print(f"[Action] '{timeline.name}' (Loop) started. Interval: {timeline.loop_interval}s")
    
    try:
        while not stop_event.is_set():
            start_time = time.perf_counter()
            for timestamp, command, args in timeline.actions:
                if stop_event.is_set(): break
                
                target_time = start_time + timestamp
                while True:
                    current_time = time.perf_counter()
                    if current_time >= target_time:
                        break
                    wait_time = target_time - current_time
                    if wait_time > 0.002:
                         time.sleep(wait_time - 0.001)
                
                execute_action_wrapper(command, args, all_timelines)
            
            # Wait for loop interval or stop signal
            if not stop_event.is_set():
                time.sleep(timeline.loop_interval)
    finally:
        print(f"[Action] '{timeline.name}' (Loop) stopped.")
        timeline.is_running = False

def run_timeline_hold(timeline: Timeline, active_trigger_key: str, all_timelines: list = None):
    """
    Executes timeline once, tracks keys pressed down.
    Waits for trigger key release to release tracked keys.
    """
    # timeline.is_running = True <-- Handled in main_loop now
    print(f"[Action] '{timeline.name}' (Hold) started. Hold trigger '{active_trigger_key}' to keep state.")
    
    try:
        # Track keys that are explicitly pressed down
        keys_held_down = set()
        mouse_buttons_held = set()

        start_time = time.perf_counter()
        for timestamp, command, args in timeline.actions:
            target_time = start_time + timestamp
            
            # Precise wait loop
            while True:
                current_time = time.perf_counter()
                if current_time >= target_time:
                    break
                wait_time = target_time - current_time
                if wait_time > 0.002:
                     time.sleep(wait_time - 0.001)

            # Track state before executing
            if command == 'key_down' and args:
                keys_held_down.add(args[0])
            elif command == 'key_up' and args:
                if args[0] in keys_held_down:
                    keys_held_down.remove(args[0])
            elif command == 'mouse_down':
                btn = args[0] if args else 'left'
                mouse_buttons_held.add(btn)
            elif command == 'mouse_up':
                btn = args[0] if args else 'left'
                if btn in mouse_buttons_held:
                    mouse_buttons_held.remove(btn)

            execute_action_wrapper(command, args, all_timelines)
        
        # Debug info
        if keys_held_down or mouse_buttons_held:
            print(f"  [Hold] Holding keys: {list(keys_held_down)}, Mouse: {list(mouse_buttons_held)}")
        
        print(f"  -> Script finished. Waiting for trigger '{active_trigger_key}' release...")
        
        # Wait for physical key release
        if active_trigger_key:
            while key_check(active_trigger_key):
                time.sleep(0.005) # Increased poll rate for release check
        
        print("  -> Trigger released. Cleaning up keys.")
        
        # Cleanup: Release all held keys/buttons
        for k in keys_held_down:
            print(f"    [Cleanup] Releasing Key: {k}")
            pydirectinput.keyUp(k)
        for b in mouse_buttons_held:
            print(f"    [Cleanup] Releasing Mouse: {b}")
            pydirectinput.mouseUp(button=b)

    finally:
        print(f"[Debug] Setting is_running=False for '{timeline.name}'")
        timeline.is_running = False

# --- Main Loop ---

def main_loop(file_path: str):
    timelines = parse_config(file_path)
    if not timelines:
        print("No timelines loaded.")
        return

    print(f"Loaded {len(timelines)} timelines from {os.path.basename(file_path)}")
    print("-" * 70)
    print(f"{ 'Name':<20} | {'Triggers':<20} | {'Mode':<8} | {'Target':<10}")
    print("-" * 70)
    for t in timelines:
        triggers_str = ",".join(t.trigger_keys) if t.trigger_keys else "(None)"
        target = t.target_window if t.target_window else "ALL"
        print(f"{t.name:<20} | {triggers_str:<20} | {t.mode:<8} | {target:<10}")
    print("-" * 70)
    print("Running... Press Ctrl+C to exit.")

    last_triggered = {}
    COOLDOWN = 0.3 # Basic debounce
    last_heartbeat = time.time()

    try:
        while True:
            # Heartbeat every 5 seconds
            if time.time() - last_heartbeat > 5.0:
                print(f"[System] Heartbeat. Active threads: {threading.active_count()}.")
                # Print status of all timelines
                for t in timelines:
                    print(f"  -> Timeline '{t.name}': is_running={t.is_running}")
                last_heartbeat = time.time()

            current_window_title = get_active_window_title()

            for t in timelines:
                if t.trigger_keys:
                    # Check all trigger keys for this timeline
                    active_trigger_key = None
                    for key in t.trigger_keys:
                        if key_check(key):
                            active_trigger_key = key
                            break
                    
                    if active_trigger_key:
                        # 2. Window Check
                        if t.target_window and t.target_window.upper() != "ALL":
                            if t.target_window.lower() not in current_window_title.lower():
                                now = time.time()
                                last_log = last_triggered.get(t.name + "_log", 0)
                                if now - last_log > 1.0: # Log max once per second per timeline
                                    print(f"[Debug] Key '{active_trigger_key}' ignored. Target '{t.target_window}' not found in current window '{current_window_title}'.")
                                    last_triggered[t.name + "_log"] = now
                                continue

                        now = time.time()
                        last_time = last_triggered.get(t.name, 0)
                        time_since_last = now - last_time
                        
                        # Debug log for every press detection (throttled to avoid spamming console completely)
                        # Only print if we are NOT running, to see if we are trying to start
                        if not t.is_running and (time_since_last > COOLDOWN):
                            print(f"[Debug] Key '{active_trigger_key}' detected. Mode: {t.mode}, Running: {t.is_running}, Cooldown: {time_since_last:.2f}s")

                        if (time_since_last > COOLDOWN):
                            if t.mode == 'loop':
                                last_triggered[t.name] = now
                                # Toggle Logic
                                if t.loop_thread and t.loop_thread.is_alive():
                                    t.loop_stop_event.set()
                                    t.loop_thread.join()
                                    print(f"[System] Loop '{t.name}' toggled OFF.")
                                else:
                                    if not t.is_running:
                                        t.is_running = True 
                                        t.loop_stop_event = threading.Event()
                                        t.loop_thread = threading.Thread(target=run_timeline_loop, args=(t, t.loop_stop_event, timelines))
                                        t.loop_thread.start()
                                        print(f"[System] Loop '{t.name}' toggled ON.")
                                    else:
                                        print(f"[Debug] '{t.name}' loop skipped (flag is_running=True).")
                            
                            elif t.mode == 'hold':
                                if not t.is_running:
                                    last_triggered[t.name] = now
                                    t.is_running = True 
                                    print(f"[Debug] Starting Hold thread for '{t.name}'")
                                    threading.Thread(target=run_timeline_hold, args=(t, active_trigger_key, timelines)).start()
                                else:
                                    # This is normal while holding
                                    pass 
                            
                            else: # OneShot
                                if not t.is_running:
                                    last_triggered[t.name] = now
                                    t.is_running = True 
                                    print(f"[Debug] Starting OneShot thread for '{t.name}'")
                                    threading.Thread(target=run_timeline_once, args=(t, active_trigger_key, timelines)).start()
                                else:
                                    print(f"[Debug] '{t.name}' oneshot skipped (flag is_running=True).")
                        else:
                             # Cooldown active
                             pass

            time.sleep(0.001) # Optimized polling rate

    except KeyboardInterrupt:
        print("\nExiting...")
        # Cleanup loops
        for t in timelines:
            if t.loop_stop_event:
                t.loop_stop_event.set()

if __name__ == "__main__":
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

    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        if check_admin_required(config_file) and not is_admin():
            print("Config requires administrator privileges. Requesting...")
            params = " ".join([f'"{arg}"' for arg in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            sys.exit()

        main_loop(config_file)
    else:
        print("Usage: python control.py <config_file>")
