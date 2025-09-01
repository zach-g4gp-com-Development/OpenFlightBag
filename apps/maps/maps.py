import tkinter as tk
from tkinter import ttk, PhotoImage
from tkintermapview import TkinterMapView
import json
import requests, time, threading, queue
from PIL import Image, ImageTk
from math import atan2, radians, degrees, sin, cos, sqrt
from haversine import haversine
import pyttsx3
with open("apps/settings/resources/maps/openaip_key.txt", "r") as file:
    api_key = file.read().strip()
with open("apps/shared/sound.txt", "r") as file:
    audio_setting = file.read().strip()

headers = {
    "Accept": "application/json",
    "x-openaip-api-key": api_key
}
def play_sound_alert(message):
    def run_speech():
        try:
            engine = pyttsx3.init()

            voices = engine.getProperty("voices")
            engine.setProperty("voice", voices[1].id)
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            print("TTS ERROR:", e)
    if audio_setting == "1":
        threading.Thread(target=run_speech, daemon=True).start()
    # else: skip sound and avoid printing to reduce console spam
play_sound_alert("Initializing map...")

def haversine_nm(lat1, lon1, lat2, lon2):
    R = 3440.065  # Earth radius in NM
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def calculate_bearing(lat1, lon1, lat2, lon2):
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    x = sin(dLon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
    bearing = atan2(x, y)
    return (degrees(bearing) + 360) % 360

def bearing_to_clock(your_heading, target_bearing):
    relative = (target_bearing - your_heading + 360) % 360
    clock_pos = int((relative + 15) // 30) or 12  # 360° circle divided into 12 segments
    return f"{clock_pos} o'clock"

def bearing_to_clock(your_heading, target_bearing):
    relative = (target_bearing - your_heading + 360) % 360
    clock = int((relative + 15) // 30) or 12  # 360° circle divided into 12 segments
    return f"{clock} o'clock"

def run_traffic_advisories(own_lat, own_lon, own_heading, target_lat, target_lon,alt=None,local_alt=None):
    if None not in (own_lat, own_lon, target_lat, target_lon):
        distance = haversine_nm(own_lat, own_lon, target_lat, target_lon)
        bearing = calculate_bearing(own_lat, own_lon, target_lat, target_lon)
        clock = bearing_to_clock(own_heading, bearing)
        
        if alt and local_alt:
            if distance < 1 and (clock == "12 o'clock" or clock == "1 o'clock" or clock == "11 o'clock") and abs(alt - local_alt) <= 3000:
                bearing = calculate_bearing(own_lat, own_lon, target_lat, target_lon)
                clock = bearing_to_clock(own_heading, bearing)
                play_sound_alert(f"Make {own_heading+90} now! Traffic {distance:.1f} nautical miles, {clock}.")

            elif distance < 3 and abs(alt - local_alt) <= 3000:
                bearing = calculate_bearing(own_lat, own_lon, target_lat, target_lon)
                clock = bearing_to_clock(own_heading, bearing)
                play_sound_alert(f"Traffic! Traffic! {distance:.1f} nautical miles, {clock}.")
        else:
            if distance < 1 and (clock == "12 o'clock" or clock == "1 o'clock" or clock == "11 o'clock"):
                bearing = calculate_bearing(own_lat, own_lon, target_lat, target_lon)
                clock = bearing_to_clock(own_heading, bearing)
                play_sound_alert(f"Make {own_heading+90} now! Traffic {distance:.1f} nautical miles, {clock}.")
            elif distance < 3:
                bearing = calculate_bearing(own_lat, own_lon, target_lat, target_lon)
                clock = bearing_to_clock(own_heading, bearing)
                play_sound_alert(f"Traffic! Traffic! {distance:.1f} nautical miles, {clock}.")
            
            
    else:
        print("⚠️ Skipping advisory: missing coordinates")

dump1090_markers = {}

last_update_time = time.time()

aircraft_queue = queue.Queue()
def listen_dump1090_stream():
    """ Runs in a background thread """
    global aircraft_queue
    while True:
        try:
            resp = requests.get("http://localhost:8080/data.json", timeout=10)
            aircraft_list = resp.json()

            # Ensure it's a proper list before adding
            if isinstance(aircraft_list, list) and aircraft_list:
                if aircraft_queue.empty():
                    aircraft_queue.put(aircraft_list)

        except Exception as e:
            print(f"❌ Failed to fetch dump1090 data: {e}")
        time.sleep(2)  # adjust polling rate as needed

threading.Thread(target=listen_dump1090_stream, daemon=True).start()

phone_gps_position = None  # global to store (lat, lon)
heading_from_phone = 0     # optional: if your phone sends bearing

dump1090_markers = {}
# load the one callsign you want to track
with open("apps/shared/callsign.txt", "r", encoding="utf-8") as f:
    TRACKED_CALLSIGN = f.read().strip().upper()
    CALLSIGN = TRACKED_CALLSIGN

use_callsign_position = False
user_pos_override = None  # will hold (lat, lon) when callsign is seen

user_marker = None
direct_target_coords = None
direct_path = None
# Store previous GPS position globally
last_gps_position = None

def update_user_location(lat,lon,heading):
    global user_marker

    def do_update():
        global user_marker, direct_path
        icon = get_rotated_icon(heading)
        if user_marker:
            user_marker.delete()
        user_marker = map_widget.set_marker(lat, lon, icon=icon)
        if follow_var.get():
            map_widget.set_position(lat, lon)
        if direct_target_coords:
            coords = [(lat, lon), direct_target_coords]
            if direct_path:
                direct_path.delete()
            direct_path = map_widget.set_path(coords, color="orange")
    root.after(0, do_update)

# Then use the same map_widget.set_marker() call
# Track markers so we can delete them
waypoint_markers = []
search_marker = None

# Main window
root = tk.Tk()
root.title("Map - OpenFlightBag")
root.geometry("1000x600")
style = ttk.Style(root)
style.theme_use("default")
style.configure("Dark.TButton",
                foreground="white",   # Text color
                background="#1f222a", # Button color
                font=("Segoe UI", 12),
                padding=10)

def get_rotated_icon(degrees):
    # Cache rotated icons to avoid repeated computation
    if not hasattr(get_rotated_icon, "cache"):
        get_rotated_icon.cache = {}
    key = int(degrees) % 360
    if key in get_rotated_icon.cache:
        return get_rotated_icon.cache[key]
    rotated = original_img.rotate(-degrees, resample=Image.BICUBIC, expand=True)
    img = ImageTk.PhotoImage(rotated)
    get_rotated_icon.cache[key] = img
    return img

# Load icons AFTER root is created
normal_icon   = PhotoImage(file="apps/maps/icons/normal_waypoint.png")
approach_icon = PhotoImage(file="apps/maps/icons/approach_waypoint.png")
airport_icon  = PhotoImage(file="apps/maps/icons/airport.png")
original_img = Image.open("apps/maps/icons/aircraft_icon.png")  # Store original for future rotation
bottom_nav = tk.Frame(root, bg="#121418")
bottom_nav.pack(side="bottom", fill="x")
import subprocess
def launch_app(file):
    subprocess.Popen(["python", file])
    quit()
import datetime
def get_zulu_time():
    now_utc = datetime.datetime.utcnow()
    return now_utc.strftime("%a %d %b %Y • %H:%M Z")
bottom_bar = tk.Frame(root, bg="#121418")
bottom_bar.pack(side="bottom", fill="x")

# ← Bottom-left: Callsign
callsign_btm = tk.Label(bottom_bar, text=f"📡 {CALLSIGN}", font=("Consolas", 12), fg="white", bg="#121418")
callsign_btm.pack(side="left", padx=20, pady=10)

# → Bottom-right: Zulu Time
zulu_btm = tk.Label(bottom_bar, text=get_zulu_time(), font=("Consolas", 12), fg="lightgray", bg="#121418")
zulu_btm.pack(side="right", padx=20, pady=10)

# 🏠 Center: Home Button
home_btn = tk.Button(
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
    command=lambda: launch_app("mainwindow.py")
)
# Manual center placement
bottom_bar.update_idletasks()
home_btn.place(relx=0.5, rely=0.5, anchor="center")

# 🔁 Zulu Time Updater
def update_bottom_clock():
    zulu_btm.config(text=get_zulu_time())
    root.after(1000, update_bottom_clock)

control_frame = tk.Frame(root, bg="#121418", width=200)
control_frame.pack(side="left", fill="y", expand=True)
# Map widget
main_frame = tk.Frame(root)
main_frame.pack(side="top", fill="both", expand=True)

# 🗺️ Map Frame (takes most space, but not all)
map_frame = tk.Frame(main_frame, bg="black")
map_frame.pack(side="top", fill="both", expand=True)

map_widget = TkinterMapView(map_frame, width=1000, height=600)
map_widget.pack(fill="both", expand=True)

# Set max zoom to 8


with open("apps/settings/resources/maps/zoom.txt", "r", encoding="utf-8") as f:
    zoom = int(f.read().strip())

# 
tk.Label(control_frame, text="Waypoint Controls",foreground="white",bg="#121418" ,font=("Segoe UI", 12)).pack(pady=10)

# Dropdowns
source_var = tk.StringVar(value="All Waypoints")
source_dd  = ttk.Combobox(
    control_frame,
    style="Dark.TButton",
    textvariable=source_var,
    state="readonly",
    values=["All Waypoints", "Enroute Only", "Approach Only"]
)
map_widget.set_position(51.5074, -0.1278)  # Default to London
source_dd.pack(pady=5)

action_var = tk.StringVar(value="Hide")
action_dd  = ttk.Combobox(
    control_frame,
    textvariable=action_var,
    style="Dark.TButton",
    state="readonly",
    values=["Show", "Hide"]
)
action_dd.pack(pady=5)

tk.Label(control_frame, text="Search",bg="#121418",fg="white", font=("Segoe UI", 12)).pack(pady=(10, 0))
search_var = tk.StringVar()
search_entry = ttk.Entry(control_frame,style="Dark.TButton", textvariable=search_var)
search_entry.pack(pady=5)

search_btn = ttk.Button(control_frame, text="Find", style="Dark.TButton",command=lambda: search_location(search_var.get()))
search_btn.pack(pady=(0, 10))

from lxml import etree


def parse_kml(file_path):
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    with open(file_path, "rb") as f:
        doc = etree.parse(f)

    placemarks = doc.xpath("//kml:Placemark", namespaces=ns)
    polygons = []

    for placemark in placemarks:
        name = placemark.find("kml:name", namespaces=ns)
        name_text = name.text if name is not None else "Unnamed"

        coords = placemark.xpath(".//kml:coordinates", namespaces=ns)
        if coords:
            raw = coords[0].text.strip()
            coord_pairs = [
                (float(c.split(",")[1]), float(c.split(",")[0]))  # lat, lon order
                for c in raw.replace("\n", " ").split()
            ]
            polygons.append((name_text, coord_pairs))

    return polygons

# ---------------------
# 🗺️ Basic Map Setup
# ---------------------


# ---------------------
# 📍 Draw Airspace Boundaries
# ---------------------



def extract_coordinates(data):
    """
    Extracts polygon coordinates from all items in the JSON response.
    Returns a list of polygons, each as a list of (lat, lon) tuples.
    """
    coordinates_list = []

    for item in data.get("items", []):
        geometry = item.get("geometry", {})
        if geometry.get("type") == "Polygon":
            # Each polygon may contain multiple rings (outer + holes)
            for ring in geometry.get("coordinates", []):
                polygon = [(lat, lon) for lon, lat in ring]  # Flip to (lat, lon)
                coordinates_list.append(polygon)

    return coordinates_list

def draw_polygons_on_map(map_widget, polygons): #WIP
    for polygon in polygons:
        map_widget.set_polygon(polygon, outline_color="blue", fill_color="lightblue", border_width=2)

def fetch_and_draw_airport_polygons_web(map_widget,target):

    url = f"https://api.core.openaip.net/api/airspaces?page=1&limit=1000&sortBy=name&sortDesc=true&country={target}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    polygons = extract_coordinates(data)

    draw_polygons_on_map(map_widget, polygons)

def fetch_and_draw_airport_polygons(map_widget,target):

    loc = f"apps/maps/resources/airspace/{target}.json"
    print("locally getting airspace for ", target)
    try:
        with open(loc, "r", encoding="utf-8") as f:
            data = json.load(f)
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    polygons = extract_coordinates(data)

    draw_polygons_on_map(map_widget, polygons)
with open("apps/maps/resources/airspace/installed_airspace.json", "r", encoding="utf-8") as f:
    content = f.read().strip()
    if content == "":
        airspace = []
    else:
        airspace = json.loads(content)
    # ------------------------------------------
installed = []
for country_code in airspace["installed"]:
    fetch_and_draw_airport_polygons(map_widget, country_code)

if False:
    subprocess.Popen("tileserver-gl --config C:/Users/Zach/Downloads/code/apps/maps/resources/local_maps/config.json", shell=True)
    map_widget.set_tile_server("http://localhost:8080/styles/basic-preview/{z}/{x}/{y}.png")

country_codes = ["GB", "PL"]

for code in country_codes:
    if code not in installed:
        fetch_and_draw_airport_polygons_web(map_widget, code)
# Simple JSON loader
def load_json(fname):
    try:
        with open(fname, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def search_location(query):
    global search_marker

    query = query.strip().lower()
    if not query:
        return

    # Clear previous search result if it exists
    if search_marker:
        search_marker.delete()
        search_marker = None

    # combine datasets
    waypoints = load_json("apps/maps/resources/normal_waypoints.json") + load_json("apps/maps/resources/approach_waypoints.json")
    airports  = load_json("apps/maps/resources/icao_locations.json")
    navaids = load_json("apps/maps/resources/navaids.json")
    all_data  = waypoints + airports + navaids

    for item in all_data:
        # Grab coordinates
        lat = item.get("latitude")
        lon = item.get("longitude")

        if not lat or not lon:
            location = item.get("location", {})
            lat = location.get("latitude")
            lon = location.get("longitude")

        if lat is None or lon is None:
            continue

        # Grab label candidates
        ident = str(item.get("ident", "")).lower()
        icao  = str(item.get("icao", "")).lower()
        name  = str(item.get("name", "")).lower()

        if query in ident or query in icao or query in name:
            # Pan and drop search result
            map_widget.set_position(lat, lon)
            map_widget.set_zoom(9)

            label_text = f"🔍 {item.get('ident') or item.get('icao') or item.get('name', 'Search')}"
            search_marker = map_widget.set_marker(lat, lon, text=label_text)
            return
def clear_search_marker():
    global search_marker
    if search_marker:
        search_marker.delete()
        search_marker = None
def constant_map_recenter():
    if follow_var.get() and user_marker:
        map_widget.set_position(*user_marker.position)
    root.after(500, constant_map_recenter)  # Recenter every 0.5 seconds
clear_btn = ttk.Button(control_frame, text="Clear Search",style="Dark.TButton", command=clear_search_marker)
clear_btn.pack(pady=(0, 10))
tk.Label(control_frame, text="Direct To",fg="white",bg="#121418", font=("Segoe UI", 12)).pack(pady=(10, 0))
# Old dropdown version



direct_search_var = tk.StringVar()
direct_search_entry = ttk.Entry(control_frame, style="Dark.TButton",textvariable=direct_search_var)
direct_search_entry.pack(pady=5)

direct_search_btn = ttk.Button(control_frame, text="Go Direct", style="Dark.TButton",command=lambda: go_direct_to(direct_search_var.get()))
direct_search_btn.pack(pady=(0, 10))
# Remove all markers from map
follow_var = tk.BooleanVar(value=True)  # already in your GUI
follow_check = ttk.Checkbutton(control_frame, style="Dark.TButton",text="Follow GPS Position", variable=follow_var)
follow_check.pack(pady=(5, 10))
def load_flight_plan(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Couldn't read flight plan file: {e}")
        return []
def render_flight_plan(txt_path):

    plan_ids = load_flight_plan(txt_path)
    if not plan_ids:
        return

    # Load waypoint/airport data
    sources = load_json("apps/maps/resources/normal_waypoints.json") + load_json("apps/maps/resources/approach_waypoints.json")
    sources += load_json("apps/maps/resources/icao_locations.json") 
    sources += load_json("apps/maps/resources/navaids.json")

    # Create lookup by ident/icao
    lookup = {}
    for wp in sources:
        ident = wp.get("ident") or wp.get("icao")
        lat   = wp.get("latitude") or wp.get("location", {}).get("latitude")
        lon   = wp.get("longitude") or wp.get("location", {}).get("longitude")
        if ident and lat and lon:
            lookup[ident.upper()] = (lat, lon)

    # Collect coordinates for waypoints in order
    path_coords = []
    for ident in plan_ids:
        coords = lookup.get(ident)
        if coords:
            path_coords.append(coords)
        else:
            print(f"⚠️ Waypoint not found: {ident}")

    # Draw line if path is valid
    if len(path_coords) >= 2:
        map_widget.set_path(path_coords,color="red")

    root.after(25000, lambda: render_flight_plan(txt_path))  # Re-render every 25 seconds

def go_direct_to(target_label):
    global direct_target_coords, direct_path

    data = load_json("apps/maps/resources/normal_waypoints.json") + load_json("apps/maps/resources/approach_waypoints.json")
    data += load_json("apps/maps/resources/icao_locations.json")
    data += load_json("apps/maps/resources/navaids.json")

    for item in data:
        lat = item.get("latitude") or item.get("location", {}).get("latitude")
        lon = item.get("longitude") or item.get("location", {}).get("longitude")

        if lat is None or lon is None:
            continue

        label = item.get("ident") or item.get("icao") or item.get("name", "")
        label_text = str(label).title()

        if target_label.lower() in label_text.lower():
            direct_target_coords = (lat, lon)  # save target
            map_widget.set_position(lat, lon)
            map_widget.set_zoom(10)

            map_widget.set_marker(lat, lon, text=f"➡️ Direct To: {label_text}")

            # draw path from current location
            if user_marker:
                path_coords = [user_marker.position, (lat, lon)]
                if direct_path:
                    direct_path.delete()
                direct_path = map_widget.set_path(path_coords)
            return
aircraft_markers = []
def clear_waypoints():
    for m in waypoint_markers:
        m.delete()
import requests
def set_loc(lat, lon, text="", icon=None):
    print(f"📍 Creating marker at ({lat}, {lon}) with text '{text}'")
    marker = map_widget.set_marker(lat, lon, text=text, icon=icon)
    print("✅ Marker created:", marker)
    return marker

local_lat, local_lon, local_heading,local_alt = None,None, None, None
def update_dump1090_live():
    global dump1090_markers, last_update_time
    global local_lat, local_lon, local_heading, aircraft_queue, local_alt

    if aircraft_queue.empty():
        root.after(500, update_dump1090_live)
        return

    aircraft_batch = aircraft_queue.get()

    # Throttle updates — skip if too soon
    if time.time() - last_update_time < 0.5:
        root.after(100, update_dump1090_live)
        return
    last_update_time = time.time()

    active_icao = set()
    for ac in aircraft_batch:
        lat = ac.get("lat")
        lon = ac.get("lon")
        cs = ac.get("flight", "ACFT").strip()
        hdg = ac.get("track", 0)
        alt = ac.get("altitude", 0)
        icao = ac.get("hex", cs)

        if lat is None or lon is None:
            continue

        try:
            with open("apps/shared/callsign.txt", "r", encoding="utf-8") as f:
                callsign = f.read().strip().lower()
        except Exception:
            callsign = ""

        if callsign and callsign in cs.lower():
            update_user_location(lon=lon, lat=lat, heading=hdg)
            local_lon, local_lat, local_heading,local_alt = lon, lat, hdg,alt
            return

        icon = get_rotated_icon(hdg)
        text = f"{cs} @ FL{alt // 100}" if alt > 7000 else f"{cs} @ {alt}" if alt else cs
        

        if icao in dump1090_markers:
            marker = dump1090_markers[icao]

            marker.set_position(lat, lon)
            marker.set_text(text)
        else:
            marker = set_loc(lat, lon, text=text, icon=icon)
            dump1090_markers[icao] = marker

        active_icao.add(icao)

    # Cull stale markers
    for icao in list(dump1090_markers):
        if icao not in active_icao:
            dump1090_markers[icao].delete()
            del dump1090_markers[icao]

    # Run traffic advisories
    run_traffic_advisories(
        alt=alt,
        local_alt=local_alt,
        own_lat=local_lat,
        own_lon=local_lon,
        own_heading=local_heading,
        target_lat=lat,
        target_lon=lon
    )

    root.after(100, update_dump1090_live)
def add_to_flight_plan(icao):
    """ Adds the given ICAO to the flight plan file """
    flight_plan_path = "apps/shared/flight_plan.txt"
    try:
        with open(flight_plan_path, "a", encoding="utf-8") as f:
            f.write(f"{icao.upper()}\n")
        print(f"✅ Added {icao.upper()} to flight plan.")
    except Exception as e:
        print(f"❌ Error adding {icao.upper()} to flight plan: {e}")
adsb_thread = threading.Thread(target=update_dump1090_live, daemon=True)
adsb_thread.start()

def format_waypoint_info(data):
    items = data.get("items", [])
    if not items:
        return "⚠️ No airport data found."

    item = items[0]

    # 📞 Contact Info
    contact = item.get("contact", "N/A")
    phone_services = item.get("telephoneServices", [])
    phone = phone_services[0].get("phoneNumber", "N/A") if phone_services else "N/A"

    # 📡 Frequencies
    frequencies = item.get("frequencies", [])
    freq_lines = []
    for freq in frequencies:
        name = freq.get("name", "Unknown")
        value = freq.get("value", "N/A")
        primary = "✅ Primary" if freq.get("primary") else "Secondary"
        public = "🟢 Public" if freq.get("publicUse") else "🔒 Private"
        freq_lines.append(f" - {name}: {value} MHz ({primary}, {public})")

    # 🧭 Instrument Approach Aids
    runways = item.get("runways", [])
    navaid_lines = []
    for runway in runways:
        aids = runway.get("instrumentApproachAids", [])
        for aid in aids:
            ident = aid.get("identifier", "N/A")
            freq = aid.get("frequency", {}).get("value", "N/A")
            channel = aid.get("channel", "N/A")
            aid_type = aid.get("type", "Unknown")
            rw_designator = runway.get("designator", "?")
            navaid_lines.append(f" - {ident} ({aid_type}) on RWY {rw_designator}: {freq} kHz, Channel: {channel}")

    # 👀 Visual Approach Aids
    VISUAL_AID_TYPES = {
        1: "PAPI",
        2: "VASI",
        3: "ALS",
        4: "REIL"
    }

    visual_lines = []
    for runway in runways:
        aids = runway.get("visualApproachAids", [])
        if aids:
            aid_names = [VISUAL_AID_TYPES.get(aid, f"Unknown({aid})") for aid in aids]
            rw_designator = runway.get("designator", "?")
            visual_lines.append(f" - RWY {rw_designator}: {', '.join(aid_names)}")

    # 🕒 Operating Hours
    ops = item.get("hoursOfOperation", {}).get("operatingHours", [])
    ops_lines = []
    for op in ops:
        line = f"  Day {op.get('dayOfWeek', '?')}:"
        if "startTime" in op:
            line += f" Start: {op['startTime']}"
        if "endTime" in op:
            line += f" End: {op['endTime']}"
        if op.get("sunrise"):
            line += " Sunrise"
        if op.get("sunset"):
            line += " Sunset"
        if op.get("byNotam"):
            line += " By NOTAM"
        ops_lines.append(line)

    # 🧾 Final Output
    info = f"""📞 Contact: {contact}
Phone: {phone}

📡 Frequencies:
{chr(10).join(freq_lines) if freq_lines else " - None available"}

🧭 Instrument Approach Aids:
{chr(10).join(navaid_lines) if navaid_lines else " - None listed"}

👀 Visual Approach Aids:
{chr(10).join(visual_lines) if visual_lines else " - None listed"}

🕒 Operating Times:
{chr(10).join(ops_lines) if ops_lines else " - No operating hours listed"}
"""

    return info
api_key = "0f2d4da9981a05ce88e52f8aaabe8a05"
def fetch_airport_info(icao):
    print(f"Fetching info for {icao}...")

    url = f"https://api.core.openaip.net/api/airports?search={icao}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        responser = response.json()
    except Exception as e:
        print(f"Error fetching data for {icao}: {e}")
        responser = {"items": []}

    # Create popup window
    info_window = tk.Toplevel(root)
    info_window.title(f"Airport Info: {icao}")
    info_window.geometry("400x450")

    # Frame for text + scrollbar
    text_frame = tk.Frame(info_window)
    text_frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")

    text_widget = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set, font=("Consolas", 10))
    text_widget.insert("1.0", format_waypoint_info(responser))
    text_widget.config(state="disabled")
    text_widget.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=text_widget.yview)

    # Frame for button
    button_frame = tk.Frame(info_window)
    button_frame.pack(fill="x", pady=10)

    button = tk.Button(button_frame, text="Direct To", command=lambda i=icao: go_direct_to(i))
    button.pack(padx=5)
    button2 = tk.Button(button_frame, text="Add to Flight Plan", command=lambda i=icao: add_to_flight_plan(i))
    button2.pack(padx=5)
    
def fetch_navaid_info(icao,freq,channel,type):
    print(f"Fetching info for {icao}...")

    # Create popup window
    info_window = tk.Toplevel(root)
    info_window.title(f"Navaid Info: {icao}")
    info_window.geometry("400x450")

    # Frame for text + scrollbar
    text_frame = tk.Frame(info_window)
    text_frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")
    text = f"Name: {icao}\nFrequency: {freq} kHz\nChannel: {channel}\nType: {type}\n\n"
    text_widget = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set, font=("Consolas", 10))
    text_widget.insert("1.0", )
    text_widget.config(state="disabled")
    text_widget.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=text_widget.yview)

    # Frame for button
    button_frame = tk.Frame(info_window)
    button_frame.pack(fill="x", pady=10)

    button = tk.Button(button_frame, text="Direct To", command=lambda i=icao: go_direct_to(i))
    button.pack(padx=5)
    button2 = tk.Button(button_frame, text="Add to Flight Plan", command=lambda i=icao: add_to_flight_plan(i))
    button2.pack(padx=5)
  # update every 10s
# Show/hide logic, default text
def toggle_waypoints(event=None):
    clear_waypoints()
    if action_var.get() == "Hide":
        return

    # Batch load all icons once
    icon_cache = {}
    def get_icon(ntype):
        key = ntype.lower().replace('-', '').replace(' ', '')
        if key in icon_cache:
            return icon_cache[key]
        path = f"apps/maps/icons/{key}.png"
        try:
            icon = PhotoImage(file=path)
        except Exception:
            icon = None
        icon_cache[key] = icon
        return icon

    normals    = load_json("apps/maps/resources/normal_waypoints.json")
    approaches = load_json("apps/maps/resources/approach_waypoints.json")
    airports   = load_json("apps/maps/resources/icao_locations.json")
    navaids    = load_json("apps/maps/resources/navaids.json")
    mode       = source_var.get()

    # Enroute + airports
    if mode in ("All Waypoints", "Enroute Only"):
        for wp in normals:
            m = map_widget.set_marker(
                wp["latitude"], wp["longitude"],
                text=wp["ident"], icon=normal_icon
            )
            waypoint_markers.append(m)

        for ap in airports:
            loc = ap.get("location", {})
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            icao = ap["icao"] 
            if lat is not None and lon is not None:
                label = f"{ap['name'].title()} / {ap['icao']}"
                m = map_widget.set_marker(
                    lat, lon,
                    text=label, icon=airport_icon, command=lambda self, code=ap["icao"]: fetch_airport_info(code)
                )
                waypoint_markers.append(m)
        for ap in navaids:
            lat = ap.get("latitude") or ap.get("location", {}).get("latitude")
            lon = ap.get("longitude") or ap.get("location", {}).get("longitude")
            ident = ap.get("ident", "?")
            freq = ap.get("frequency", "?")
            channel = ap.get("channel", "?")
            ntype = ap.get("type", "NDB")
            if lat is not None and lon is not None:
                label = f"{ident} / {freq}"
                icon_img = get_icon(ntype)
                def make_navaid_cmd(code=ident, freq=freq, channel=channel, ntype=ntype):
                    return lambda self=None: fetch_navaid_info(code, freq, channel, ntype)
                m = map_widget.set_marker(
                    lat, lon,
                    text=label, icon=icon_img, command=make_navaid_cmd()
                )
                waypoint_markers.append(m)

    # Approach + airports
    if mode in ("All Waypoints", "Approach Only"):
        for wp in approaches:
            m = map_widget.set_marker(
                wp["latitude"], wp["longitude"],
                text=wp["ident"], icon=approach_icon
            )
            waypoint_markers.append(m)

        for ap in airports:
            loc = ap.get("location", {})
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            if lat is not None and lon is not None:
                label = f"{ap['name'].title()} / {ap['icao']}"
                m = map_widget.set_marker(
                    lat, lon,
                    text=label, icon=airport_icon, command=lambda self, code=ap["icao"]: fetch_airport_info(code))
                waypoint_markers.append(m)
        for ap in navaids:
            lat = ap.get("latitude") or ap.get("location", {}).get("latitude")
            lon = ap.get("longitude") or ap.get("location", {}).get("longitude")
            ident = ap.get("ident", "?")
            freq = ap.get("frequency", "?")
            channel = ap.get("channel", "?")
            ntype = ap.get("type", "?")

            if lat is not None and lon is not None:
                label = f"{ident} / {freq}"
                
                icon_img = get_icon(ntype)
                def make_navaid_cmd(code=ident, freq=freq, channel=channel, ntype=ntype):
                    return lambda self=None: fetch_navaid_info(code, freq, channel, ntype)
                m = map_widget.set_marker(
                    lat, lon,
                    text=label, icon=icon_img, command=make_navaid_cmd()
                )
                waypoint_markers.append(m)
# Bind dropdowns
source_dd.bind("<<ComboboxSelected>>", toggle_waypoints)
action_dd.bind("<<ComboboxSelected>>", toggle_waypoints)
# 🔻 Bottom Navigation Bar

update_bottom_clock()
render_flight_plan("apps/shared/flight_plan.txt")
toggle_waypoints()  # Initial load
constant_map_recenter()
update_dump1090_live()


root.mainloop()