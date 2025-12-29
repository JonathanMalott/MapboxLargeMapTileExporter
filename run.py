"""
Mapbox Tile Stitcher
===================

Downloads Mapbox raster tiles for a given geographic bounding box,
stitches them into a single image, and exports a cropped PNG.

Requirements:
- Python 3.9+
- requests
- pillow
- tqdm

Environment variables required:
- MAPBOX_ACCESS_TOKEN
- MAPBOX_STYLE_ID   (e.g. "username/style_id")
"""

import math
import io
import os
import sys
import requests
from PIL import Image
from tqdm import tqdm


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Disable PIL's decompression bomb warning for very large stitched images
Image.MAX_IMAGE_PIXELS = None

# Mapbox configuration (loaded from environment)
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")
MAPBOX_STYLE_ID = os.getenv("MAPBOX_STYLE_ID")

if not MAPBOX_ACCESS_TOKEN or not MAPBOX_STYLE_ID:
    sys.exit(
        "Error: MAPBOX_ACCESS_TOKEN and MAPBOX_STYLE_ID must be set "
        "as environment variables."
    )

# Tile and render settings
ZOOM = 14                 # Mapbox zoom level
TILE_SIZE = 1024          # Size of @2x tiles in pixels
SCALE_FACTOR = 1.0        # Final image scaling multiplier
TILES_DIR = "tiles"       # Directory for cached tiles


# ---------------------------------------------------------------------------
# Coordinate helpers
# ---------------------------------------------------------------------------

def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> tuple[float, float]:
    """
    Convert latitude/longitude to fractional Mapbox tile coordinates.
    """
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom

    x_tile = (lon + 180.0) / 360.0 * n
    y_tile = (
        (1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi)
        / 2.0 * n
    )

    return x_tile, y_tile


# ---------------------------------------------------------------------------
# Core functionality
# ---------------------------------------------------------------------------

def generate_rectangle_map(
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    output_file: str = "map.png",
) -> str:
    """
    Generate a stitched Mapbox image for a rectangular bounding box.

    Args:
        min_lat, min_lon: Southwest corner
        max_lat, max_lon: Northeast corner
        output_file: Path to the output PNG

    Returns:
        Path to the saved image
    """
    os.makedirs(TILES_DIR, exist_ok=True)

    # Convert geographic bounds to tile coordinates
    x_min, y_max = lat_lon_to_tile(min_lat, min_lon, ZOOM)
    x_max, y_min = lat_lon_to_tile(max_lat, max_lon, ZOOM)

    # Determine tile index ranges
    x_start, x_end = math.floor(x_min), math.ceil(x_max)
    y_start, y_end = math.floor(y_min), math.ceil(y_max)

    tiles_x = x_end - x_start
    tiles_y = y_end - y_start
    total_tiles = tiles_x * tiles_y

    # Create a canvas large enough to hold all tiles
    stitched = Image.new(
        "RGB",
        (tiles_x * TILE_SIZE, tiles_y * TILE_SIZE)
    )

    # Download and paste tiles
    with tqdm(total=total_tiles, desc="Downloading tiles", unit="tile") as pbar:
        for x in range(x_start, x_end):
            for y in range(y_start, y_end):
                tile_url = (
                    f"https://api.mapbox.com/styles/v1/{MAPBOX_STYLE_ID}/tiles/"
                    f"{ZOOM}/{x}/{y}@2x"
                    f"?access_token={MAPBOX_ACCESS_TOKEN}&tilesize=512"
                )

                response = requests.get(tile_url, timeout=30)

                if response.status_code != 200:
                    print(f"Warning: missing tile {ZOOM}/{x}/{y}")
                    pbar.update(1)
                    continue

                tile_img = Image.open(io.BytesIO(response.content))

                # Cache individual tiles on disk
                tile_path = os.path.join(TILES_DIR, f"{ZOOM}_{x}_{y}.png")
                tile_img.save(tile_path, "PNG")

                # Paste into stitched image
                stitched.paste(
                    tile_img,
                    ((x - x_start) * TILE_SIZE, (y - y_start) * TILE_SIZE),
                )

                pbar.update(1)

    # Crop stitched image to exact bounding box
    left = (x_min - x_start) * TILE_SIZE
    right = (x_max - x_start) * TILE_SIZE
    top = (y_min - y_start) * TILE_SIZE
    bottom = (y_max - y_start) * TILE_SIZE

    final = stitched.crop((
        int(left),
        int(top),
        int(right),
        int(bottom),
    ))

    # Optional scaling
    if SCALE_FACTOR != 1.0:
        w, h = final.size
        final = final.resize(
            (round(w * SCALE_FACTOR), round(h * SCALE_FACTOR)),
            Image.LANCZOS,
        )

    final.save(output_file, "PNG")
    print(f"Saved stitched map to: {output_file}")

    return output_file


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Example bounding box (replace with your own)
    MIN_LAT = 29.4115
    MIN_LON = -98.5055
    MAX_LAT = 29.4335
    MAX_LON = -98.4790

    generate_rectangle_map(
        MIN_LAT,
        MIN_LON,
        MAX_LAT,
        MAX_LON,
        output_file="output_map.png",
    )
