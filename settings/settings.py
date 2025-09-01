import tkinter as tk
from tkinter import ttk
import datetime
import subprocess

with open("apps/shared/callsign.txt", "r") as file:
    CALLSIGN = file.read().strip()

def get_zulu_time():
    return datetime.datetime.utcnow().strftime("%a %d %b %Y • %H:%M Z")

# 🛫 Return navigation
def return_to_main():
    print("Returning to main...")
    subprocess.Popen(["python", "mainwindow.py"])
    quit()

root = tk.Tk()
root.title("Settings - OpenFlightBag")
root.geometry("800x600")
root.configure(bg="#121418")


# ⚙️ Settings Section
settings_frame = tk.Frame(root, bg="#121418")
settings_frame.pack(fill="both", padx=30, pady=20)
def sound_check():
    print()
def setting_row(label_text, widget, row):
    tk.Label(settings_frame, text=label_text, font=("Consolas", 12), fg="white", bg="#121418", anchor="w", width=25).grid(row=row, column=0, sticky="w", pady=4, padx=5)
    widget.grid(row=row, column=1, sticky="w", padx=5)
    return widget
row_counter = iter(range(100))  # You’ll never hit 100... probably 😄
def handle_zoom(event):
    widget = event.widget
    current_text = widget.get()
    try:
        with open("apps/settings/resources/maps/zoom.txt", "w", encoding="utf-8") as f:
            f.write(int(current_text))
        widget.delete(0, tk.END)
        widget.insert(0, current_text)
    except:
        widget.delete(0, tk.END)
        widget.insert(0, "Numbers only")
def handle_callsign(event):
    widget = event.widget
    current_text = widget.get()
    
    with open("apps/shared/callsign.txt", "w", encoding="utf-8") as f:
        f.write(current_text)
    widget.delete(0, tk.END)
    widget.insert(0, current_text)
def handle_key(event):
    widget = event.widget
    current_text = widget.get()
    
    with open("apps/settings/resources/maps/openaip_key.txt", "w", encoding="utf-8") as f:
        f.write(current_text)
    widget.delete(0, tk.END)
    widget.insert(0, current_text)
def handle_enter(event):
    widget = event.widget
    current_text = widget.get()
    result = current_text[::-1]  # Example logic: reverse string
    widget.delete(0, tk.END)
    widget.insert(0, result)
def sound():
    with open("apps/shared/sound.txt", "r") as file:
        content = file.read().strip()
    if content == "1":
        with open("apps/shared/sound.txt", "w") as file:
            file.write("0")
    else:
        with open("apps/shared/sound.txt", "w") as file:
            file.write("1")
zoom_entry = setting_row("Zoom_level", tk.Entry(settings_frame, font=("Consolas", 12), width=30), next(row_counter))
zoom_entry.bind("<Return>", handle_zoom)
callsign_entry = setting_row("Callsign", tk.Entry(settings_frame, font=("Consolas", 12), width=30), next(row_counter))
callsign_entry.bind("<Return>", handle_callsign)
callsign_entry = setting_row("OpenAIP API Key", tk.Entry(settings_frame, font=("Consolas", 12), width=30), next(row_counter))
callsign_entry.bind("<Return>", handle_key)
airport_combo = ttk.Combobox(settings_frame, values=["EGLL", "EGSS", "EGCC"], font=("Consolas", 12), width=28)
airport_combo.set("EGLL")
setting_row("Default Airport", airport_combo, next(row_counter))


map_theme_combo = ttk.Combobox(settings_frame, values=["light", "dark", "satellite"], font=("Consolas", 12), width=28)
map_theme_combo.set("dark")
setting_row("Map Theme", map_theme_combo, next(row_counter))

sound_check = tk.Button(settings_frame, text="Enable", font=("Consolas", 12), bg="#1f222a", fg="white", command=sound)
setting_row("Sound Alerts", sound_check, next(row_counter))

# 🧱 Bottom Bar
bottom_bar = tk.Frame(root, bg="#121418")
bottom_bar.pack(side="bottom", fill="x")

# ← Callsign
callsign_btm = tk.Label(bottom_bar, text=f"📡 {CALLSIGN}", font=("Consolas", 12), fg="white", bg="#121418")
callsign_btm.pack(side="left", padx=20, pady=10)

# → Zulu Clock
zulu_btm = tk.Label(bottom_bar, text=get_zulu_time(), font=("Consolas", 12), fg="lightgray", bg="#121418")
zulu_btm.pack(side="right", padx=20, pady=10)

# ⬅️ Return Button Centered
return_btn = tk.Button(
    bottom_bar,
    text="🏠 Main",
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

# 🔁 Clock Updater
def update_bottom_clock():
    zulu_btm.config(text=get_zulu_time())
    root.after(1000, update_bottom_clock)

update_bottom_clock()

root.mainloop()