from PIL import Image
import cairosvg
from io import BytesIO

def svg_to_png(svg_path):
    png_data = cairosvg.svg2png(url=svg_path)
    return Image.open(BytesIO(png_data)).convert("RGBA")

lang_grid = svg_to_png("./img/profile/lang_grid.svg")
weekly = svg_to_png("./img/profile/weekly_activity_dark.svg")

# Use wider image as target width
target_width = max(lang_grid.width, weekly.width)

def resize_to_width(img, w):
    ratio = w / img.width
    return img.resize((w, int(img.height * ratio)), Image.LANCZOS)

lang_grid = resize_to_width(lang_grid, target_width)
weekly = resize_to_width(weekly, target_width)

gap = 20
total_height = lang_grid.height + weekly.height + gap
combined = Image.new("RGBA", (target_width, total_height), (0, 0, 0, 0))

combined.paste(lang_grid, (0, 0))
combined.paste(weekly, (0, lang_grid.height + gap))

combined.save("./img/profile/svgs_combined.png")
print(f"Done! Saved: {target_width}x{total_height}")
