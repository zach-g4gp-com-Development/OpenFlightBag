import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import datetime
import time
import requests
import json

with open("apps/shared/callsign.txt", "r") as file:
    CALLSIGN = file.read()
def normalize_version(v):
    return v.strip().lower().replace("v", "")



def launch_app(file):
    subprocess.Popen(["python", file])
    quit()


def get_zulu_time():
    now_utc = datetime.datetime.utcnow()
    return now_utc.strftime("%a %d %b %Y • %H:%M Z")



apps = [
    {"name": "Install Resources",
     "file": "apps/store/resources/local_apps/resources.py",
     "icon": "resources.png"},
     
     {"name": "Install Apps",
     "file": "apps/store/resources/local_apps/install_new.py",
     "icon": "apps.png"}
]

# ---------- GUI ---------- #
root = tk.Tk()
root.title("App Store - OpenFlightBag")
root.geometry("1000x700")
root.configure(bg="#121418")

# 🧑‍✈️ Top Bar: Callsign + Zulu Clock
topbar = tk.Frame(root, bg="#121418")
topbar.pack(side="top", fill="x")

callsign_label = tk.Label(topbar, text=f"OpenFlightMap Store", font=("Consolas", 20), fg="cyan", bg="#121418")
callsign_label.pack(side="top", padx=20, pady=10)



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
        from io import BytesIO

        try:
            response = requests.get(f"https://wdcprp.com/openflightbag/store/{app["icon"]}")
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img = img.resize((72, 72), Image.LANCZOS)
            icon = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading {app['icon']}: {e}")
            icon = None
    except Exception as e:
            print(f"Error loading {app['icon']}: {e}")
            icon = None



        

    if icon:
        btn = tk.Button(frame, image=icon, command=lambda f=app["file"], n=app["name"]: launch_app(file=f),
                        bg="#121418", borderwidth=0, highlightthickness=0,
                        activebackground="#2a2e39", cursor="hand2")
        btn.image = icon  # 👈 Prevent garbage collection
        btn.pack()
        icons.append(icon)  # 👈 Keep reference

    tk.Label(frame, text=app["name"], fg="white", bg="#121418", font=("Consolas", 12)).pack(pady=5)
def get_zulu_time():
    from datetime import datetime
    return datetime.utcnow().strftime("%a %d %b %Y • %H:%M Z")

# 🛫 Return Navigation Logic
def return_to_main():
    import subprocess
    # Swap with your navigation logic or frame switch
    subprocess.Popen(["python", "mainwindow.py"])
    quit()

# 🧱 Bottom Bar Frame
bottom_bar = tk.Frame(root, bg="#121418")
bottom_bar.pack(side="bottom", fill="x")
def callsign():
    with open("apps/shared/callsign.txt", "r") as file:
        content = file.read()
    return content
# 📡 Callsign Label (Left)
callsign_btm = tk.Label(
    bottom_bar,
    text=f"📡 {callsign()}",
    font=("Consolas", 12),
    fg="white",
    bg="#121418"
)
callsign_btm.pack(side="left", padx=20, pady=10)

# ⬅️ Return Button (Centered)
return_btn = tk.Button(
    bottom_bar,
    text="Home",
    font=("Consolas", 12),
    fg="white",
    bg="#1f222a",
    activebackground="#2c2f38",
    activeforeground="cyan",
    relief="flat",
    padx=20,
    pady=5,
    command=return_to_main
)
bottom_bar.update_idletasks()
return_btn.place(relx=0.5, rely=0.5, anchor="center")

# 🕐 Zulu Clock Label (Right)
zulu_btm = tk.Label(
    bottom_bar,
    text=get_zulu_time(),
    font=("Consolas", 12),
    fg="lightgray",
    bg="#121418"
)
zulu_btm.pack(side="right", padx=20, pady=10)

# 🔄 Clock Refresher
def update_bottom_clock():
    zulu_btm.config(text=get_zulu_time())
    root.after(1000, update_bottom_clock)

update_bottom_clock()
root.mainloop()