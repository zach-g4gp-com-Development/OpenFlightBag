import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import datetime
import json


with open("apps/shared/callsign.txt", "r") as file:
        CALLSIGN = file.read()

with open("apps/shared/installed.json", "r") as f:
        apps = json.load(f)


def launch_app(file):

    subprocess.Popen(["python", file])
    quit()
def get_zulu_time():
    now_utc = datetime.datetime.utcnow()
    return now_utc.strftime("%a %d %b %Y • %H:%M Z")

# ---------- GUI ---------- #
root = tk.Tk()
root.title("OpenFlightBag")
root.geometry("1000x700")
root.configure(bg="#121418")

# 🧑‍✈️ Top Bar: Callsign + Zulu Clock
topbar = tk.Frame(root, bg="#121418")
topbar.pack(side="top", fill="x")

callsign_label = tk.Label(topbar, text=f"📡 {CALLSIGN}", font=("Consolas", 14), fg="cyan", bg="#121418")
callsign_label.pack(side="left", padx=20, pady=10)

zulu_label = tk.Label(topbar, text=get_zulu_time(), font=("Consolas", 14), fg="lightgray", bg="#121418")
zulu_label.pack(side="right", padx=20, pady=10)

def update_clock():
    zulu_label.config(text=get_zulu_time())
    root.after(1000, update_clock)

update_clock()

# 🧭 Icon Grid
grid_frame = tk.Frame(root, bg="#121418")
grid_frame.pack(expand=True)

icons = []  # keep references alive

for idx, app in enumerate(apps):
    row = idx // 3
    col = idx % 3

    frame = tk.Frame(grid_frame, bg="#121418", padx=10, pady=10)
    frame.grid(row=row, column=col, padx=25, pady=25)

    try:
        img = Image.open(app["icon"])
        img = img.resize((72, 72), Image.LANCZOS)
        icon = ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading {app['icon']}: {e}")
        icon = None

    if icon:
        btn = tk.Button(frame, image=icon, command=lambda f=app["file"]: launch_app(f),
                        bg="#121418", borderwidth=0, highlightthickness=0,
                        activebackground="#2a2e39", cursor="hand2")
        btn.image = icon  # 👈 Prevent garbage collection
        btn.pack()
        icons.append(icon)  # 👈 Keep reference

    tk.Label(frame, text=app["name"], fg="white", bg="#121418", font=("Consolas", 12)).pack(pady=5)
root.mainloop()