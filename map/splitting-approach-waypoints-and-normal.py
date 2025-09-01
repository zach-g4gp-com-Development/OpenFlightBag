import json

# Load input JSON
with open("development/map/waypoints.json", "r", encoding="utf-8") as f:
    waypoints = json.load(f)

# Prepare lists
normal_waypoints = []
approach_waypoints = []

# Split based on presence of digit in ident
for wp in waypoints:
    if any(char.isdigit() for char in wp["ident"]):
        approach_waypoints.append(wp)
    else:
        normal_waypoints.append(wp)

# Save output files
with open("normal_waypoints.json", "w", encoding="utf-8") as f:
    json.dump(normal_waypoints, f, indent=4)

with open("approach_waypoints.json", "w", encoding="utf-8") as f:
    json.dump(approach_waypoints, f, indent=4)