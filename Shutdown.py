import ctypes
import os


MB_OKCANCEL = 1
MB_ICONEXCLAMATION = 48
IDOK = 1

ctypes.windll.user32.MessageBeep(0xFFFFFFFF)


result = ctypes.windll.user32.MessageBoxW(
    0, 
    "Are you sure you want to shut down your PC?", 
    "Windows Shutdown", 
    MB_OKCANCEL | MB_ICONEXCLAMATION
)


if result == IDOK:
    os.system("shutdown /s /t 0")
else:
    print("Shutdown cancelled :D")
