#!/usr/bin/env python3

"""
Lock Screen

Description: Runs in background. Presses F15 every 15 min to keep computer awake. Listens the keyboard events.
If keyboard event matches lock shortcut, mouse and keyboard are blocked. Program continues to listen to keyboard
events. If keyboard event matches unlock password, mouse and keyboard are unblocked

Sources:
https://stackoverflow.com/questions/7529991/disable-or-lock-mouse-and-keyboard-in-python
https://stackoverflow.com/questions/13564851/how-to-generate-keyboard-events-in-python
msdn.microsoft.com/en-us/library/dd375731

Author: Nic La
Last modified: 19-07-20
"""


import time
import caffeine
import keyboard


lock_hotkey = 'alt + space'
password = 'unicorn'
locked = 0
recorded = []
event_clean = []


def lock_dev():
    global locked
    print('block mouse and keyboard')
    locked = 1
    # read any key press into keyboard.block_key('h') unless is matches password

    # TODO block keyboard and mouse CAREFUL be prepared to restart PC


def unlock_dev():
    global locked
    print('unblock mouse and keyboard')
    locked = 0
    keyboard.unhook_all()
    # TODO: unblock keyboard and mouse


if __name__ == "__main__":
    while True:

        # Listen for hotkey to lock computer
        if locked == 0:
            keyboard.add_hotkey(lock_hotkey, lambda: lock_dev())

        # While locked, record keyboard input until "enter" pressed
        if locked == 1:
            recorded = keyboard.record(until='enter')

        # Parse recorded and store in event_clean
        if len(recorded) != 0:
            for event in recorded:
                event_str = str(event).replace('KeyboardEvent', '')  # convert to str and remove 'KeyboardEvent'
                if 'down' in event_str:  # only record down events, ignore up events
                    event_str = event_str[1:-1]  # remove parentheses
                    event_str = event_str.replace(' down', '')
                    event_str = event_str.replace('space', ' ')
                    event_clean.append(event_str)

        # check event_clean for password
        # If password, unlock computer
        y = 0
        for x in event_clean:
            if x == password[y]:
                y += 1
                if y == len(password):
                    unlock_dev()
                    break
            else:
                y = 0

        if len(event_clean) > 1:
            print(''.join(event_clean))

        # If no password, clean recorded and continue
        recorded = []
        event_clean = []
        
        time.sleep(1)


