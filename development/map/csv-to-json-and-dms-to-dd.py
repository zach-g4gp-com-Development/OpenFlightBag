import csv
import re
import json

def dms_to_dd(dms_str):
    # Match DMS like: 55° 08' 12.00" N
    match = re.match(r'(\d+)° (\d+)' + r"' ([\d.]+)\"\"? ([NSEW])", dms_str)
    if not match:
        return None
    deg, minutes, seconds, direction = match.groups()
    dd = float(deg) + float(minutes)/60 + float(seconds)/3600
    return -dd if direction in ['S', 'W'] else dd

input_file = "development/map/uk_waypoints.csv"
output_file = "development/map/waypoints.json"
waypoints = []

with open(input_file, "r", encoding="latin1") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if len(row) >= 5:
            name = row[0].strip()
            lat_str = row[2].strip().replace("″", "\"")  # normalize double-prime
            lon_str = row[4].strip().replace("″", "\"")
            lat_dd = dms_to_dd(lat_str)
            lon_dd = dms_to_dd(lon_str)
            if lat_dd is not None and lon_dd is not None:
                waypoints.append({
                    "ident": name,
                    "latitude": lat_dd,
                    "longitude": lon_dd
                })
            else:
                print(f"❌ Failed to parse: {name} → {lat_str}, {lon_str}")

# Save JSON file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(waypoints, f, indent=4)