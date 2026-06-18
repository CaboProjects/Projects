import ctypes
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.withdraw()

answer = messagebox.askyesno(
    "Sleep Confirmation",
    "Are you sure you want to put your PC to sleep?"
)

if answer:
    ctypes.windll.powrprof.SetSuspendState(False, True, False)

root.destroy()