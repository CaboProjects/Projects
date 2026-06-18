#!/usr/bin/env python3

import math
import random
import time
import tkinter as tk

try:
    import psutil
    HAVE_PSUTIL = True
except ImportError:
    HAVE_PSUTIL = False


def get_memory_stats():
    """Return (percent_used, used_gb, total_gb)."""
    if HAVE_PSUTIL:
        vm = psutil.virtual_memory()
        return vm.percent, vm.used / (1024 ** 3), vm.total / (1024 ** 3)

    info = {}
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                key, _, rest = line.partition(":")
                info[key] = int(rest.strip().split()[0])
        total = info.get("MemTotal", 1)
        avail = info.get("MemAvailable", info.get("MemFree", 0))
        used = total - avail
        percent = 100.0 * used / total
        return percent, used / (1024 ** 2), total / (1024 ** 2)
    except Exception:
        return 50.0, 4.0, 8.0


PALETTES = [
    ("#ff6ec7", "#ff2fb0"),  # hot pink
    ("#6ee7ff", "#1fb6ff"),  # cyan
    ("#ffe66e", "#ffb01f"),  # amber
    ("#9d6eff", "#6a1fff"),  # violet
    ("#6effa0", "#1fff7a"),  # mint
    ("#ff8a6e", "#ff4f1f"),  # coral
]


class MemFish:
    """A wobbly blob-creature whose properties track memory usage."""

    def __init__(self, canvas, width, height, kind="used"):
        self.canvas = canvas
        self.w = width
        self.h = height
        self.kind = kind
        self.x = random.uniform(0.1, 0.9) * width
        self.y = random.uniform(0.1, 0.9) * height
        self.angle = random.uniform(0, math.tau)
        self.t = random.uniform(0, 1000)
        self.base_size = random.uniform(18, 34)
        self.fill, self.outline = random.choice(PALETTES)
        self.tail_phase = random.uniform(0, math.tau)
        self.body_id = None
        self.eye_id = None
        self.tail_ids = []

    def speed(self, pressure):
        if self.kind == "used":
            return 0.6 + pressure * 3.2
        return 0.15 + pressure * 0.4

    def wobble_amount(self, pressure):
        return 6 + pressure * 18 if self.kind == "used" else 4 + pressure * 6

    def size(self, pressure):
        if self.kind == "used":
            return self.base_size * (0.8 + pressure * 0.9)
        return self.base_size * (1.0 - pressure * 0.3)

    def step(self, dt, pressure):
        self.t += dt
        spd = self.speed(pressure)
        wob = self.wobble_amount(pressure)

        self.angle += math.sin(self.t * 1.7 + self.tail_phase) * 0.04 * (
            1.5 if self.kind == "used" else 0.4
        )
        if random.random() < 0.01 + pressure * 0.04:
            self.angle += random.uniform(-1.2, 1.2)

        self.x += math.cos(self.angle) * spd
        self.y += math.sin(self.angle) * spd + math.sin(self.t * 2.3) * (wob * 0.02)

        m = self.size(pressure) + 10
        if self.x < m:
            self.x = m
            self.angle = math.pi - self.angle
        elif self.x > self.w - m:
            self.x = self.w - m
            self.angle = math.pi - self.angle
        if self.y < m:
            self.y = m
            self.angle = -self.angle
        elif self.y > self.h - m:
            self.y = self.h - m
            self.angle = -self.angle

    def draw(self, pressure):
        s = self.size(pressure)
        x, y = self.x, self.y
        wob = self.wobble_amount(pressure)
        facing = math.cos(self.angle)

        if self.kind == "used":
            self._draw_eel(x, y, s, wob, facing)
        else:
            self._draw_jelly(x, y, s, wob)

    def _blob_points(self, cx, cy, base_r, n=14, irregularity=0.25, phase=0.0):
        pts = []
        for i in range(n):
            ang = math.tau * i / n
            wig = (
                math.sin(ang * 3 + self.t * 2 + phase) * irregularity
                + math.sin(ang * 5 - self.t * 1.3) * irregularity * 0.5
            )
            r = base_r * (1 + wig)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        return pts

    def _draw_eel(self, x, y, s, wob, facing):
        body = self._blob_points(x, y, s, n=16, irregularity=0.22 + wob * 0.01)
        stretched = []
        for px, py in body:
            dx, dy = px - x, py - y
            stretched.append((x + dx * (1.3 if abs(facing) > 0.2 else 1.0), y + dy * 0.85))

        cid = self.canvas.create_polygon(
            *[c for pt in stretched for c in pt],
            fill=self.fill, outline=self.outline, width=2, smooth=True
        )

        tail_id = None
        flick = math.sin(self.t * 8 + self.tail_phase) * (4 + wob * 0.3)
        tx = x - math.cos(self.angle) * (s * 1.4)
        ty = y - math.sin(self.angle) * (s * 1.4) + flick
        tail_id = self.canvas.create_polygon(
            x - math.cos(self.angle) * s * 0.6 + math.sin(self.angle) * s * 0.4,
            y - math.sin(self.angle) * s * 0.6 - math.cos(self.angle) * s * 0.4,
            tx, ty,
            x - math.cos(self.angle) * s * 0.6 - math.sin(self.angle) * s * 0.4,
            y - math.sin(self.angle) * s * 0.6 + math.cos(self.angle) * s * 0.4,
            fill=self.outline, outline="", smooth=True
        )

        ex = x + math.cos(self.angle) * s * 0.55
        ey = y + math.sin(self.angle) * s * 0.55
        eye_id = self.canvas.create_oval(ex - 3, ey - 3, ex + 3, ey + 3, fill="white", outline="")

        self.body_id, self.eye_id, self.tail_ids = cid, eye_id, [tail_id]

    def _draw_jelly(self, x, y, s, wob):
        body = self._blob_points(x, y, s, n=12, irregularity=0.15)
        cid = self.canvas.create_polygon(
            *[c for pt in body for c in pt],
            fill=self.fill, outline=self.outline, width=2, smooth=True
        )
        tail_ids = []
        n_tent = 4
        for i in range(n_tent):
            tx0 = x + (i - (n_tent - 1) / 2) * s * 0.4
            ty0 = y + s * 0.6
            sway = math.sin(self.t * 2 + i * 1.3) * (s * 0.25)
            tx1 = tx0 + sway
            ty1 = ty0 + s * 0.9
            tid = self.canvas.create_line(
                tx0, ty0, (tx0 + tx1) / 2 + sway * 0.5, (ty0 + ty1) / 2, tx1, ty1,
                fill=self.outline, width=2, smooth=True
            )
            tail_ids.append(tid)
        self.body_id, self.eye_id, self.tail_ids = cid, None, tail_ids

    def erase(self):
        for iid in [self.body_id, self.eye_id] + self.tail_ids:
            if iid is not None:
                self.canvas.delete(iid)
        self.body_id = self.eye_id = None
        self.tail_ids = []


class Bubble:
    """Decorative rising bubble, spawn rate tied to memory pressure."""

    def __init__(self, width, height):
        self.w, self.h = width, height
        self.x = random.uniform(0, width)
        self.y = height + random.uniform(0, 40)
        self.r = random.uniform(2, 6)
        self.speed = random.uniform(0.5, 1.6)
        self.wiggle = random.uniform(0, math.tau)
        self.id = None

    def step(self, dt):
        self.y -= self.speed
        self.x += math.sin(self.y * 0.05 + self.wiggle) * 0.4
        return self.y > -10

    def draw(self, canvas):
        self.id = canvas.create_oval(
            self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r,
            outline="#cdefff", width=1
        )

    def erase(self, canvas):
        if self.id is not None:
            canvas.delete(self.id)


class AquariumApp:
    WIDTH, HEIGHT = 900, 600
    SAMPLE_EVERY = 1.5
    MAX_USED_FISH = 18
    MAX_FREE_FISH = 6

    def __init__(self, root):
        self.root = root
        root.title("RAM Aquarium")
        root.configure(bg="#021024")

        self.canvas = tk.Canvas(
            root, width=self.WIDTH, height=self.HEIGHT,
            bg="#021024", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.label = tk.Label(
            root, font=("Helvetica", 12), fg="#bfe9ff", bg="#021024", anchor="w"
        )
        self.label.place(x=12, y=8)

        self.last_sample = 0
        self.percent = 0.0
        self.used_gb = 0.0
        self.total_gb = 0.0
        self._poll_memory()

        self.fish = []
        self._rebuild_fish()

        self.bubbles = []
        self.last_time = time.time()

        self.root.bind("<Configure>", self._on_resize)
        self._tick()

    def _poll_memory(self):
        self.percent, self.used_gb, self.total_gb = get_memory_stats()
        self.last_sample = time.time()
        self.root.after(int(self.SAMPLE_EVERY * 1000), self._poll_memory)

    @property
    def pressure(self):
        return max(0.0, min(1.0, self.percent / 100.0))

    def _rebuild_fish(self):
        for f in self.fish:
            f.erase()
        self.fish.clear()

        n_used = 3 + round(self.pressure * (self.MAX_USED_FISH - 3))
        n_free = max(1, round((1 - self.pressure) * self.MAX_FREE_FISH))

        for _ in range(n_used):
            self.fish.append(MemFish(self.canvas, self.WIDTH, self.HEIGHT, "used"))
        for _ in range(n_free):
            self.fish.append(MemFish(self.canvas, self.WIDTH, self.HEIGHT, "free"))

    def _on_resize(self, event):
        if event.widget is self.root:
            self.WIDTH = max(300, event.width)
            self.HEIGHT = max(200, event.height - 0)

    def _tick(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        if random.random() < 0.01:
            target_used = 3 + round(self.pressure * (self.MAX_USED_FISH - 3))
            used_now = sum(1 for f in self.fish if f.kind == "used")
            if used_now < target_used:
                self.fish.append(MemFish(self.canvas, self.WIDTH, self.HEIGHT, "used"))
            elif used_now > target_used and used_now > 1:
                for i, f in enumerate(self.fish):
                    if f.kind == "used":
                        f.erase()
                        del self.fish[i]
                        break

        self.canvas.delete("bg")
        self._draw_background()

        for f in self.fish:
            f.erase()
            f.step(dt * 30, self.pressure)
            f.draw(self.pressure)

        if random.random() < 0.03 + self.pressure * 0.12:
            self.bubbles.append(Bubble(self.WIDTH, self.HEIGHT))
        alive = []
        for b in self.bubbles:
            b.erase(self.canvas)
            if b.step(dt * 30):
                b.draw(self.canvas)
                alive.append(b)
        self.bubbles = alive

        self.label.config(
            text=f"RAM: {self.percent:4.1f}%  used  ({self.used_gb:.1f} / {self.total_gb:.1f} GB)"
            f"   —  {sum(1 for f in self.fish if f.kind=='used')} anxious eels, "
            f"{sum(1 for f in self.fish if f.kind=='free')} lazy jellies"
        )

        self.root.after(33, self._tick)

    def _draw_background(self):
        bands = 24
        for i in range(bands):
            t = i / bands
            r = int(2 + 10 * t + self.pressure * 25)
            g = int(16 + 40 * (1 - t))
            b = int(36 + 60 * (1 - t))
            color = f"#{r:02x}{g:02x}{b:02x}"
            y0 = self.HEIGHT * i / bands
            y1 = self.HEIGHT * (i + 1) / bands
            self.canvas.create_rectangle(0, y0, self.WIDTH, y1, fill=color, outline="", tags="bg")
        self.canvas.create_rectangle(
            0, self.HEIGHT - 18, self.WIDTH, self.HEIGHT,
            fill="#3a2f1f", outline="", tags="bg"
        )


def main():
    root = tk.Tk()
    AquariumApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
