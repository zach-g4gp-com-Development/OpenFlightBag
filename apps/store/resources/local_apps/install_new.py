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

def get_update_status(store_apps, installed_apps):
    status_list = []

    for store_app in store_apps:
        name = store_app["name"]
        store_version = normalize_version(store_app["version"])

        # Find installed app by name
        installed_app = next((app for app in installed_apps if app["name"] == name), None)

        if not installed_app:
            status = 1  # Not installed
        else:
            installed_version = normalize_version(installed_app["version"])
            if store_version == installed_version:
                status = 0  # Up to date
            else:
                status = 2  # Update available

        status_list.append({
            "name": name,
            "status": status,
            "store_version": store_app["version"],
            "installed_version": installed_app["version"] if installed_app else None
        })

    return status_list

def add_app(new_app):
    file_path = "apps/shared/installed.json"
    with open(file_path, "r") as f:
        apps = json.load(f)

    apps.append(new_app)

    with open(file_path, "w") as f:
        json.dump(apps, f, indent=4)
def launch_app(file, name,update=1,desc="N/A"): # update=2 means update button, 1 means install button, 0 means no button (latest and installed)
    import tkinter as tk
    from tkinter import PhotoImage
    icon = name.lower() + ".png"
    # Create main window
    roote = tk.Toplevel()
    roote.title("App Installer")
    roote.geometry("700x200")
    roote.configure(bg="#2b2b2b")  # Dark background for contrast
    from io import BytesIO

    try:
        response = requests.get(f"https://wdcprp.com/openflightbag/store/apps/{icon}")
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img = img.resize((120, 120), Image.LANCZOS)
        icone = ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading {icon}: {e}")
        icone = None
        
    

        # Frame to hold everything
    main_frame = tk.Frame(roote, bg="#2b2b2b")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # 🖼️ Left side: Icon
    if icone:
        icon_frame = tk.Frame(main_frame, bg="#2b2b2b")
        icon_frame.pack(side="left", padx=(0, 20), pady=10)

        icon_label = tk.Label(icon_frame, image=icone, bg="#2b2b2b")
        icon_label.image = icone  # 👈 Keep reference alive
        icon_label.pack()

    # 📄 Right side: Text and Button
    right_frame = tk.Frame(main_frame, bg="#2b2b2b")
    right_frame.pack(side="left", fill="both", expand=True)

    name_label = tk.Label(right_frame, text=name, fg="white", bg="#2b2b2b",
                        font=("Segoe UI", 16, "bold"))
    name_label.pack(anchor="w")

    desc_label = tk.Label(right_frame, text=desc,
                        fg="#cccccc", bg="#2b2b2b", font=("Segoe UI", 12))
    desc_label.pack(anchor="w", pady=(5, 10))

    if update == 2:
        install_button = tk.Button(right_frame, text="Update", bg="#add8e6", fg="black",
                                font=("Segoe UI", 12, "bold"), padx=20, pady=5,
                                command=lambda: install_app(name, file))
    elif update == 1:
        install_button = tk.Button(right_frame, text="Install", bg="#add8e6", fg="black",
                                font=("Segoe UI", 12, "bold"), padx=20, pady=5,
                                command=lambda: install_app(name, file))
    else:
        install_button = tk.Button(right_frame, text="Already latest/installed", bg="#add8e6", fg="black",
                                font=("Segoe UI", 12, "bold"), padx=20, pady=5, state="disabled")
    install_button.pack(anchor="w")

    

    

    root.mainloop()


def install_app(name, f):

    import requests
    import zipfile
    import os
    name = name.lower()
    # URL of the zip file
    url = f"https://wdcprp.com/openflightbag/store/apps/{name}.zip"

    # Download the zip file
    response = requests.get(url)
    zip_path = f"apps/store/resources/cache/{name}.zip"

    with open(zip_path, "wb") as file:
        file.write(response.content)

    # Extract the zip file
    extract_path = f"apps/{name}"
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    # Clean up (optional)
    os.remove(zip_path)
    print(f"Folder downloaded and extracted to: {extract_path}")
    with open(f"{extract_path}/config.json", "r") as foxtrot:
        configloc = json.load(foxtrot)

    add_app(configloc)


def get_zulu_time():
    now_utc = datetime.datetime.utcnow()
    return now_utc.strftime("%a %d %b %Y • %H:%M Z")

with open("apps/store/resources/cache/latest_apps.json", "w") as file:
        
    file.write(requests.get("https://wdcprp.com/openflightbag/store/latest_apps.json").text)
with open("apps/store/resources/cache/latest_apps.json", "r") as f:
        apps = json.load(f)
with open("apps/shared/installed.json", "r") as file:
    installed_apps = json.load(file)
results = get_update_status(apps, installed_apps)



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
            response = requests.get(f"https://wdcprp.com/openflightbag/store/apps/{app["icon"]}")
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
    for result in results:
        if result["name"] == app["name"]:
            update = result["status"]
            

        print(f"{result['name']}: status {result['status']}")

    if icon:
        btn = tk.Button(frame, image=icon, command=lambda f=app["file"], n=app["name"]: launch_app(file=f, name=n, update=update, desc=app["description"]),
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