import tkinter as tk
from tkinter import messagebox
import os
from tkintermapview import TkinterMapView
import json

def launch_map():
    # Load data from flight plan
    try:
        with open("apps/shared/flight_plan.txt", "r") as f:
            lines = f.read().splitlines()
            dep_icao = lines[0]
            route = lines[1:-1]
            arr_icao = lines[-1]
    except Exception as e:
        messagebox.showerror("Error", f"Problem reading flight plan file:\n{e}")
        return

    # Load airport and waypoint data
    try:
        with open("apps/map/resources/eg_icao_locations.json", "r") as f:
            airport_data = json.load(f)
        with open("apps/map/resources/uk_waypoints.json", "r") as f:
            waypoint_data = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Couldn’t read JSON files:\n{e}")
        return

    # Start map window
    map_win = tk.Toplevel(root)
    map_win.title("Flight Route Map")
    map_widget = TkinterMapView(map_win, width=800, height=1000, corner_radius=0)
    map_widget.pack(fill="both", expand=True)

    def get_coords(identifier):
        # Check airports
        for item in airport_data:
            if item.get("icao") == identifier and "location" in item:
                loc = item["location"]
                return (loc["latitude"], loc["longitude"])
        
        # Check waypoints
        for item in waypoint_data:
            if item.get("ident") == identifier:
                return (item["latitude"], item["longitude"])
    
        return None  # not found

    route_points = []

    for wp in [dep_icao] + route + [arr_icao]:
        coords = get_coords(wp)
        if coords:
            lat, lon = coords
            marker = map_widget.set_marker(lat, lon, text=wp)
            route_points.append((lat, lon))
        else:
            print(f"Waypoint/Airport '{wp}' not found.")

    # Draw path
    if len(route_points) > 1:
        map_widget.set_path(route_points)

    # Center map on departure
    dep_coords = get_coords(dep_icao)
    if dep_coords:
        map_widget.set_position(*dep_coords)
        map_widget.set_zoom(7)
def save_flightplan():
    aircraft = aircraft_var.get()
    registration = reg_var.get()
    callsign = callsign_var.get()
    departure = dep_var.get()
    arrival = arr_var.get()
    route = route_var.get()

    if not all([aircraft, registration, callsign, departure, arrival, route]):
        messagebox.showerror("Missing Info", "Please fill in all fields.")
        return

    # Prepare save paths

    callsign_path = "apps/shared/callsign.txt"
    flightplan_path = "apps/shared/flight_plan.txt"


    # Write callsign
    with open(callsign_path, "w") as f:
        f.write(callsign.strip())
    if "dct" in route.lower():
        if "DCT" in route:

            route = route.replace("DCT", "")
        else:
            route = route.replace("dct", "")
        print("replaced DCT")
    # Write flight plan
    route_parts = route.strip().split(" ")

    with open(flightplan_path, "w") as f:
        f.write(f"{departure.strip()}\n")
        for waypoint in route_parts:
            f.write(f"{waypoint}\n")
        f.write(f"{arrival.strip()}\n")

    messagebox.showinfo("Success", "Flight plan saved!")

# GUI setup
root = tk.Tk()
root.title("Flight Planner - OpenFlightBag")
root.geometry("600x700")
root.configure(bg="#1f222a")

title = tk.Label(root, text="✈ Flight Plan Composer", fg="cyan", bg="#1f222a", font=("Consolas", 16))
title.pack(pady=10)

def labeled_entry(label_text, var):
    frame = tk.Frame(root, bg="#1f222a")
    frame.pack(pady=5)
    tk.Label(frame, text=label_text, fg="white", bg="#1f222a", font=("Consolas", 12)).pack(anchor="w")
    tk.Entry(frame, textvariable=var, font=("Consolas", 12), width=30).pack()

aircraft_var = tk.StringVar()
reg_var = tk.StringVar()
callsign_var = tk.StringVar()
dep_var = tk.StringVar()
arr_var = tk.StringVar()
route_var = tk.StringVar()

labeled_entry("Aircraft Type (e.g. DA62):", aircraft_var)
labeled_entry("Registration (e.g. GBFFS):", reg_var)
labeled_entry("Callsign:", callsign_var)
labeled_entry("Departure ICAO:", dep_var)
labeled_entry("Route (space-separated):", route_var)
labeled_entry("Arrival ICAO:", arr_var)

tk.Button(root, text="Save Flight Plan", command=save_flightplan, bg="#2a2e39", fg="white", font=("Consolas", 12)).pack(pady=20)
tk.Button(root, text="Launch Map", command=launch_map, bg="#2a2e39", fg="white", font=("Consolas", 12)).pack(pady=5)
tk.Button(root, text="File Flightplan to UK CAA (coming soon.......)", bg="#2a2e39", fg="white", font=("Consolas", 12)).pack(pady=20)
# ⌚ Zulu Time Utility


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