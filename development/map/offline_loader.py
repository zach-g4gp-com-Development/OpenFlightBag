from tkintermapview import OfflineLoader

# Global bounds: top-left and bottom-right corners of the world
top_left = (85.0, -180.0)         # Near North Pole, far west
bottom_right = (-85.0, 180.0)     # Near South Pole, far east

zoom_min = 2   # Low zoom = fewer tiles
zoom_max = 6   # Higher zoom = more detail, but exponentially more tiles

loader = OfflineLoader(path="world_tiles.db")
loader.save_offline_tiles(top_left, bottom_right, zoom_min, zoom_max)