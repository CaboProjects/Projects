import tkinter as tk
from tkinter import messagebox
import requests
import threading
import time

running = False

def send_loop():
    global running

    webhook = webhook_entry.get().strip()
    if not webhook:
        messagebox.showerror("Error", "Webhook URL missing")
        return

    delay = float(delay_entry.get())

    running = True

    while running:
        try:
            r = requests.post(
                webhook,
                json={"content": "add_msg_here_credit_caboprojects_github"},
                timeout=1
            )

            status_label.config(text=f"Status: {r.status_code}")

        except Exception as e:
            status_label.config(text=f"Error: {e}")

        time.sleep(delay)

def start():
    global running
    if not running:
        # Show warning before starting because yes
        proceed = messagebox.askyesno(
            "Warning",
            "Warning: Webhook spamming is against Discord's TOS.\nAre you sure you want to proceed?"
        )
        if proceed:
            threading.Thread(target=send_loop, daemon=True).start()

def stop():
    global running
    running = False
    status_label.config(text="Stopped :D")

root = tk.Tk()
root.title("Webhookify (By CaboProjects)")
root.geometry("420x250")

# credits to Spain2000 in discord for helping me make this project below is what i wrote
corner_label = tk.Label(root, text="CaboProjects", fg="gray")
corner_label.place(x=5, y=5)

tk.Label(root, text="Webhook URL").pack()
webhook_entry = tk.Entry(root, width=50)
webhook_entry.pack()

tk.Label(root, text="Delay (0.8 sec → 14400 sec / 4 hours)").pack()
delay_entry = tk.Entry(root, width=20)
delay_entry.insert(0, "1")
delay_entry.pack()

tk.Button(root, text="Send", command=start).pack(pady=10)
tk.Button(root, text="Stop", command=stop).pack()

status_label = tk.Label(root, text="Status: idle")
status_label.pack(pady=10)

root.mainloop()
