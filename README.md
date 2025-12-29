# MapboxLargeMapTileExporter

<p align="center">
  <img src="tokyo.webp" width="750" />
</p>

A Python utility for exporting large, high-resolution static maps from Mapbox by
downloading individual raster tiles, stitching them together, and cropping the
result to an exact geographic bounding box.

This tool is designed for cases where the Mapbox Static Images API is too limited
in size or resolution.

---

## What This Does

Given a latitude/longitude bounding box, the script:

1. Converts geographic coordinates to Mapbox tile coordinates  
2. Downloads all required `@2x` raster tiles at a fixed zoom level  
3. Stitches the tiles into a single image  
4. Crops precisely to the requested bounding box  
5. Saves the final image as a PNG  

---

## Use Cases

- Exporting large city or neighborhood maps
- Generating print-quality static maps
- Creating map backgrounds for design or visualization
- Offline map image generation

---

## Requirements

- Python 3.9+
- A Mapbox account and access token

Python dependencies:
- `requests`
- `pillow`
- `tqdm`

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/MapboxLargeMapTileExporter.git
cd MapboxLargeMapTileExporter
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt` yet, you can install manually:

```bash
pip install requests pillow tqdm
```

---

## Configuration

This project uses environment variables for Mapbox credentials.

Copy the sample environment file:

```bash
cp .env.sample .env
```

Edit `.env` and set your values:

```env
MAPBOX_ACCESS_TOKEN=pk_your_access_token_here
MAPBOX_STYLE_ID=your_username/your_style_id
```

Notes:

- Do not commit `.env`
- `.env.sample` is safe to commit
- The access token should have `styles:read` and `tiles:read` permissions

---

## Usage

Edit the bounding box values in `run.py`:

```python
if __name__ == "__main__":
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
```

Then run:

```bash
python run.py
```

The final stitched map will be saved as:

```text
output_map.png
```

Downloaded tiles are cached locally in the `tiles/` directory.

---

## Output Quality Notes

- Tile size uses Mapbox `@2x` (512px tiles rendered at 1024px)
- Zoom level is fixed in the script (`ZOOM = 14`)
- Large bounding boxes can generate very large images and consume significant memory

---

## Limitations

- No automatic rate-limit handling
- Fixed zoom level (manual edit required)
- Raster tiles only (not vector)

---

## Attribution

Map data and imagery © Mapbox.  
You are responsible for complying with Mapbox’s terms of service when using or
distributing generated images.

---

## License

MIT License (or choose another license appropriate for your project).
