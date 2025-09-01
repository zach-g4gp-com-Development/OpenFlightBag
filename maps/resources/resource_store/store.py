import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import datetime
import requests
import json
from io import BytesIO
import tkinter.messagebox as messagebox

# Config

with open("apps/settings/resources/maps/openaip_key.txt") as f:
    API_KEY = f.read().strip()
win = tk.Tk()
win.title(f"Map Resource Installer")
win.geometry("700x400")
win.configure(bg="#2b2b2b")
HEADERS = {
    "Accept": "application/json",
    "x-openaip-api-key": API_KEY
}

# Modules

def add_app_map(app_name, country_code):
    path = f"apps/{app_name}/resources/maps/resources/airspace/installed_airspace.json"
    with open(path, "r") as f:
        codes = json.load(f)
    codes.append(country_code.lower())
    with open(path, "w") as f:
        json.dump(codes, f, indent=4)

# Download and save the JSON payload for a given country
def install_map_airspace(app_name, country_code):
    url = (
        "https://api.core.openaip.net/api/airspaces"
        f"?page=1&limit=1000&sortBy=name&sortDesc=true&country={country_code}"
    )
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()

    out_path = f"apps/{app_name}/resources/airspace/{country_code.lower()}.json"
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    add_app_map(app_name, country_code)

def handle_airspace(event, app_name):
    country = event.widget.get().strip()
    if len(country) != 2 or not country.isalpha():
        messagebox.showerror(
            "Invalid Country Code",
            "Please enter a valid 2-letter country code."
        )
        return
    else:
        install_map_airspace(app_name, country)




# Load remote icon
try:
    icon_url = f"https://wdcprp.com/openflightbag/store/apps/maps.png"
    resp = requests.get(icon_url)
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content))
    img = img.resize((120, 120), Image.LANCZOS)
    icon_img = ImageTk.PhotoImage(img)
except Exception as err:
    print("Icon load error:", err)
    icon_img = None

main_frame = tk.Frame(win, bg="#2b2b2b")
main_frame.pack(fill="both", expand=True)

# Scrollable right side
canvas = tk.Canvas(main_frame, bg="#2b2b2b", highlightthickness=0)
scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas, bg="#2b2b2b")

scroll_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Title row with icon and name
title_row = tk.Frame(scroll_frame, bg="#2b2b2b")
title_row.pack(anchor="w", pady=(10, 5), padx=10)

if icon_img:
    icon_lbl = tk.Label(title_row, image=icon_img, bg="#2b2b2b")
    icon_lbl.image = icon_img
    icon_lbl.pack(side="left", padx=(0, 10))
app_name = "Maps"
tk.Label(
    title_row,
    text="Maps",
    font=("Segoe UI", 16, "bold"),
    fg="white",
    bg="#2b2b2b"
).pack(side="left", anchor="center")

# Indented content frame
content_frame = tk.Frame(scroll_frame, bg="#2b2b2b")
content_frame.pack(anchor="w", padx=140, pady=(5, 10))  # Indent to align under title


tk.Label(
    content_frame,
    text="Map Downloads",
    font=("SegoeUI", 15),
    fg="white",
    bg="#2b2b2b"
).pack(anchor="w", pady=12)

tk.Label(
    content_frame,
    text="Airspace Downloads",
    font=("Consolas", 11),
    fg="lightgray",
    bg="#2b2b2b"
).pack(anchor="w", pady=5)

entry = tk.Entry(
    content_frame,
    font=("Consolas", 10),
    width=45
)
entry.insert(0, "Enter 2-letter country code and press ENTER")
entry.bind("<Return>", lambda evt: handle_airspace(evt, app_name))
entry.pack(pady=3, anchor="w")
tk.Label(
    content_frame,
    text="Navaids Download",
    font=("Consolas", 11),
    fg="lightgray",
    bg="#2b2b2b"
).pack(anchor="w", pady=25)
def install_navaids():
    import requests
    import json
    european_country_codes = [
    # EU Member States
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU",
    "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",

    # EFTA States
    "IS", "LI", "NO", "CH",

    # Other European Countries
    "AL", "AD", "AM", "AZ", "BY", "BA", "GE", "XK", "MD", "MC", "ME", "MK", "RU",
    "SM", "RS", "TR", "UA", "GB", "VA"
]
    country_codes = european_country_codes
    parsed_data = []
    for country in country_codes:
        url = f"https://api.core.openaip.net/api/navaids?page=1&country={country}&sortBy=name&sortDesc=true"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()

        # Type mapping (only confirmed types)
        navaid_type_map = {
            1: "TACAN",
            2: "NDB",
            4: "DME-VOR",
            5: "VORTAC"
        }

        # Parse the data
        
        for item in data.get('items', []):
            navaid_type = navaid_type_map.get(item.get("type"))
            if navaid_type:  # Only include confirmed types
                parsed_data.append({
                    "ident": item.get("identifier"),
                    "latitude": item["geometry"]["coordinates"][1],
                    "longitude": item["geometry"]["coordinates"][0],
                    "frequency": float(item["frequency"]["value"]),
                    "channel": item.get("channel"),
                    "type": navaid_type
                })

    # Output the result
    json.dump(parsed_data, open("apps/maps/resources/navaids.json", "w"), indent=2)
    print("Navaids data saved to navaids.json")
def install_navaids_warn():
    if messagebox.askyesno(
        "Install Navaids",
        "This will download and install navaids data. This will take a hell lot of time (you might want to make a cuppa).\n\n"
        "Do you want to proceed?"
    ):
        try:
            install_navaids()
            messagebox.showinfo("Success", "Navaids data installed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install navaids: {e}")
tk.Button(
    content_frame,
    text="Install Navaids",
    command=install_navaids_warn,
    font=("Consolas", 10),
    bg="#2b2b2b",
    fg="white",

).pack(anchor="w", pady=5)

tk.Label(
    content_frame,
    text="Map information provided by OpenAIP",
    font=("Consolas", 5),
    fg="lightgray",
    bg="#2b2b2b"
).pack(anchor="w", pady=50)

win.mainloop()