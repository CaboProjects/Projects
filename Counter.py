import tkinter as tk
import time
import threading

class CounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Counter")
        self.root.geometry("300x150")

        self.count = 0
        self.running = True

        self.label = tk.Label(
            root,
            text="0",
            font=("Arial", 48, "bold"),
            bg="white"
        )
        self.label.pack(expand=True)

        self.root.configure(bg="white")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def loop(self):
        while self.running:
            self.count += 1
            self.root.after(0, self.update)
            time.sleep(0.2)

    def update(self):
        self.label.config(text=f"{self.count:_}")

    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CounterApp(root)
    root.mainloop()