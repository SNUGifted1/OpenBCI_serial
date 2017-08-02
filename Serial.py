import serial
import binascii

import ctypes
from ctypes import wintypes
import time

sampNumb = ""
channel_data = [0,0,0,0,0,0,0,0,0]
accel_data = [0,0,0]
gain = 24
Vref = 4.5

scale_factor = Vref / (gain * ((2 ** 23) - 1))
i = 0

# keypress
user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008


MAPVK_VK_TO_VSC = 0

# msdn.microsoft.com/en-us/library/dd375731
VK_TAB  = 0x09
VK_MENU = 0x12
VK_SPACE = 0x20
VK_W = 0x57

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

#Keypress end

with serial.Serial('COM8', 115200, timeout = 1,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE) as ser:
    ser.write('b')
    while(1):
        s = ser.read(1)
        if binascii.hexlify(s) == "a0":
            sample = ser.read(31)
            sampleID = sample[0]
            channel_data[1] = sample[1:4]
            channel_data[2] = sample[4:7]
            channel_data[3] = sample[7:10]
            channel_data[4] = sample[10:13]
            channel_data[5] = sample[13:16]
            channel_data[6] = sample[16:19]
            channel_data[7] = sample[19:22]
            channel_data[8] = sample[22:25]

            accel_data[0] = sample[25:27]
            accel_data[1] = sample[27:29]
            accel_data[2] = sample[29:31]

            if int(binascii.hexlify(channel_data[2]), 16) * scale_factor < 0.03:
                PressKey(VK_W)
            else :
                ReleaseKey(VK_W)


            print(str(int(binascii.hexlify(channel_data[1]), 16) * scale_factor) + "\t" + str(int(binascii.hexlify(channel_data[2]), 16) * scale_factor) + "\t" + str(int(binascii.hexlify(channel_data[3]), 16) * scale_factor)+ "\t" + str(int(binascii.hexlify(channel_data[4]), 16) * scale_factor)+ "\t" + str(int(binascii.hexlify(channel_data[5]), 16) * scale_factor))
