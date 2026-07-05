from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


GD_HEADER_BYTES = 11
NES_WIDTH = 256
NES_HEIGHT = 224
RGBA_BYTES_PER_PIXEL = 4


def load_gd_screenshot(path: Path) -> Image.Image:
    data = path.read_bytes()
    expected = GD_HEADER_BYTES + NES_WIDTH * NES_HEIGHT * RGBA_BYTES_PER_PIXEL
    if len(data) < expected:
        raise ValueError(f"{path} is too small to be a FCEUX screenshot")

    raw = data[GD_HEADER_BYTES:expected]
    image = Image.frombytes("RGBA", (NES_WIDTH, NES_HEIGHT), raw)
    channels = image.split()
    return Image.merge("RGB", (channels[1], channels[2], channels[3]))


def convert_gd_directory(input_dir: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    converted: list[Path] = []
    for gd_path in sorted(input_dir.glob("*.gd")):
        image = load_gd_screenshot(gd_path)
        output_path = output_dir / f"{gd_path.stem}.png"
        image.save(output_path)
        converted.append(output_path)
    return converted


def write_contact_sheet(image_paths: list[Path], output_path: Path, columns: int = 4) -> Path:
    if columns < 1:
        raise ValueError("columns must be at least 1")
    if not image_paths:
        raise ValueError("at least one image is required")

    label_height = 18
    rows = (len(image_paths) + columns - 1) // columns
    sheet = Image.new("RGB", (NES_WIDTH * columns, (NES_HEIGHT + label_height) * rows), "white")
    draw = ImageDraw.Draw(sheet)

    for index, image_path in enumerate(image_paths):
        row = index // columns
        column = index % columns
        x = column * NES_WIDTH
        y = row * (NES_HEIGHT + label_height)
        image = Image.open(image_path).convert("RGB")
        sheet.paste(image, (x, y + label_height))
        draw.text((x + 3, y + 3), image_path.stem[:36], fill=(0, 0, 0))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)
    return output_path
