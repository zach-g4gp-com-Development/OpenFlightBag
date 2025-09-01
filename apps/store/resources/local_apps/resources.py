import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import datetime
import requests
import json
from io import BytesIO

import tkinter.messagebox as messagebox

# --- Configuration & Helpers ---
with open("apps/settings/resources/maps/openaip_key.txt") as f:
    API_KEY = f.read().strip()


HEADERS = {
    "Accept": "application/json",
    "x-openaip-api-key": API_KEY
}

# Single, canonical Zulu‐time formatter
def get_zulu_time():
    return datetime.datetime.utcnow().strftime("%a %d %b %Y • %H:%M Z")

# Append a newly downloaded country code to the installed list


# Handle Enter press in the country‐code entry field


# --- GUI: App Launcher Dialog ---
# --- GUI: App Launcher Dialog ---

def launch_app(app_name):
    try:
        subprocess.Popen(["python", f"apps/{app_name}/resources/resource_store/store.py"])
    except Exception:
        messagebox.showerror(
            "Launch Error",
            f"{app_name}'s resource store could not be launched. It may not be installed or is missing files, or may just not have one."
        )
        return


# --- Main App Store Window ---

# Load installed apps (expects list of dicts with 'name' and optional 'icon')
with open("apps/shared/installed.json") as f:
    installed_apps = json.load(f)

root = tk.Tk()
root.title("App Store - OpenFlightBag")
root.geometry("1000x700")
root.configure(bg="#121418")

# Top bar: title
topbar = tk.Frame(root, bg="#121418")
topbar.pack(fill="x", pady=(10,0))
tk.Label(
    topbar,
    text="OpenFlightMap Store",
    font=("Consolas", 20),
    fg="cyan",
    bg="#121418"
).pack()

# Grid of app icons
grid = tk.Frame(root, bg="#121418")
grid.pack(expand=True)

for idx, app in enumerate(installed_apps):
    row, col = divmod(idx, 3)
    frm = tk.Frame(grid, bg="#121418", padx=25, pady=25)
    frm.grid(row=row, column=col)

    # Load each app’s icon
    icon_img = None
    try:
        url = f"https://wdcprp.com/openflightbag/store/apps/{app['name'].lower()}.png"
        resp = requests.get(url)
        resp.raise_for_status()
        im = Image.open(BytesIO(resp.content)).resize((72,72), Image.LANCZOS)
        icon_img = ImageTk.PhotoImage(im)
    except Exception as e:
        print("Icon load error for", app['name'], e)

    if icon_img:
        btn = tk.Button(
            frm, image=icon_img,
            command=lambda n=app['name']: launch_app(n),
            bg="#121418", borderwidth=0, cursor="hand2"
        )
        btn.image = icon_img
        btn.pack()

    tk.Label(
        frm,
        text=app['name'],
        font=("Consolas", 12),
        fg="white",
        bg="#121418"
    ).pack(pady=(5,0))

# Bottom bar: callsign, home button, Zulu clock
bottom = tk.Frame(root, bg="#121418")
bottom.pack(fill="x", side="bottom", pady=(0,10))

def get_callsign():
    with open("apps/shared/callsign.txt") as f:
        return f.read().strip()

tk.Label(
    bottom,
    text=f"📡 {get_callsign()}",
    font=("Consolas", 12),
    fg="white",
    bg="#121418"
).pack(side="left", padx=20)

def return_home():
    subprocess.Popen(["python", "mainwindow.py"])
    root.quit()

home_btn = tk.Button(
    bottom,
    text="Home",
    font=("Consolas", 12),
    fg="white",
    bg="#1f222a",
    relief="flat",
    command=return_home
)
home_btn.place(relx=0.5, rely=0.5, anchor="center")

zulu_lbl = tk.Label(
    bottom,
    text=get_zulu_time(),
    font=("Consolas", 12),
    fg="lightgray",
    bg="#121418"
)
zulu_lbl.pack(side="right", padx=20)

def refresh_clock():
    zulu_lbl.config(text=get_zulu_time())
    root.after(1000, refresh_clock)

refresh_clock()
root.mainloop()