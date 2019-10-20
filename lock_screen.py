#!/usr/bin/env python3

"""
Lock Screen

Description: Runs in background using threading.
    - Presses F15 every 15 min to keep computer awake.
    - Listens for keyboard addhotkey to enter lock mode. In lock mode, keyboard and mouse are blocked. Task Manager
    is automatically exited
    - In lock mode, listens for keyboard password. If entered, keyboard and mouse are unblocked

Sources:
https://stackoverflow.com/questions/7529991/disable-or-lock-mouse-and-keyboard-in-python
https://stackoverflow.com/questions/13564851/how-to-generate-keyboard-events-in-python
msdn.microsoft.com/en-us/library/dd375731
https://www.programcreek.com/python/example/10639/win32gui.EnumWindows
https://stackoverflow.com/questions/31402166/window-claims-to-be-visible-while-its-not

Author: Nic La
Last modified: 19-10-20
"""


import time
import threading
import keyboard
import mouse
import subprocess
import platform
import win32gui
import os


lock_hotkey = 'alt + space'
password = 'unicorn'
lock_flag = 0
monitor_flag = 0
ch = 0
windows = 0  # 0 = windows 7, 1 = windows 10
hwnd_ignore = [66562, 1050110, 65794]


# Press F15 every 15 min
def caffeine_thread():
    while True:
        time.sleep(900)
        keyboard.send('F15', do_press=True, do_release=True)
        print('F15')


# Return list of active window handlers
def get_hwnds():
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd) and hwnd not in hwnd_ignore and \
                win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds


# Listen for lock hotkey
def listen_thread():
    global lock_flag
    global monitor_flag
    global lock_hotkey
    global windows
    while True:
        time.sleep(1)
        if (lock_flag == 1) and (monitor_flag == 0):
            print('Entering lock mode')
            monitor_flag = 1
            keyboard.hook(monitor_keyevents, suppress=True)
            mouse.hook(monitor_mouse)
            for num, awnd in enumerate(get_hwnds()):
                print(win32gui.GetWindowText(awnd)[0:10], awnd, win32gui.GetWindowRect(awnd))  # Print active window name
                w_l, w_t, w_r, w_b = win32gui.GetWindowRect(awnd)  # get active window placement
                os.system(str(num + 1) + '.jpg')  # open picture
                time.sleep(0.5)  # delay to allow picture to enter foreground
                nwnd = win32gui.GetForegroundWindow()  # change window handle to foreground window
                win32gui.MoveWindow(nwnd, w_l, w_t, w_r - w_l, w_b - w_t, 0)  # place window handle
        if (lock_flag == 0) and (monitor_flag == 1):
            print('Entering unlock mode')
            monitor_flag = 0
            subprocess.call('taskkill /im Microsoft.Photos.exe /f')
            keyboard.unhook_all()
            keyboard.add_hotkey(lock_hotkey, lock, args=[1], suppress=True)
            mouse.unhook_all()
        if lock_flag == 1:
            search_task()


# Monitor keyboard events for password
def monitor_keyevents(key):
    global password
    global lock_flag
    global ch
    # On key event down, compare to password
    if str(key.event_type) == 'down':
        if password[ch] == str(key.name):
            ch += 1
        else:
            ch = 0
    if ch == len(password):
        lock_flag = 0
        ch = 0
    keyboard.block_key(str(key.name))


# Monitor mouse events
def monitor_mouse(event):
    mouse.move(0, 0, absolute=True, duration=0)


# Set lock flag
def lock(mode):
    global lock_flag
    lock_flag = mode


# Search tasks for Taskmgr.exe
def search_task():
    all_tasks = subprocess.check_output('tasklist')
    all_tasks_list = (all_tasks.decode("utf-8")).split('\n')
    for x in range(len(all_tasks_list)):
        for y in all_tasks_list[x].split('.exe'):
            if (y == 'Taskmgr') or (y == 'taskmgr'):
                subprocess.call('taskkill /im taskmgr.exe')


if __name__ == "__main__":
    # Initialize
    if platform.release() == '7':
        windows = 0
    elif platform.release() == '10':
        windows = 1
    keyboard.add_hotkey(lock_hotkey, lock, args=[1], suppress=True)
    x = threading.Thread(target=caffeine_thread)
    y = threading.Thread(target=listen_thread)
    x.start()
    y.start()

