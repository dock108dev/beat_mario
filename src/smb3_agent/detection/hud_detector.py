from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


# Coordinates are for the normalized 1024x896 game crop produced by Mednafen.
LIVES_DIGIT_BOX = (188, 812, 220, 836)


@dataclass(frozen=True)
class HudDetection:
    lives_digit_crop: str | None
    lives_rmse_from_reference: float | None
    lives_changed_from_reference: bool | None
    mean_luma: float
    darkened_frame: bool


def detect_hud(
    image_path: Path,
    *,
    output_crop_path: Path | None = None,
    reference_lives_crop_path: Path | None = None,
    lives_change_threshold: float = 75.0,
) -> HudDetection:
    image = Image.open(image_path).convert("RGB")
    crop = image.crop(LIVES_DIGIT_BOX)
    if output_crop_path is not None:
        output_crop_path.parent.mkdir(parents=True, exist_ok=True)
        crop.save(output_crop_path)

    lives_rmse: float | None = None
    lives_changed: bool | None = None
    if reference_lives_crop_path is not None and reference_lives_crop_path.exists():
        reference = Image.open(reference_lives_crop_path).convert("RGB")
        lives_rmse = image_rmse(crop, reference)
        lives_changed = lives_rmse >= lives_change_threshold

    luma = np.asarray(image.convert("L"), dtype=np.float32)
    mean_luma = float(np.mean(luma))

    return HudDetection(
        lives_digit_crop=str(output_crop_path.resolve()) if output_crop_path is not None else None,
        lives_rmse_from_reference=round(lives_rmse, 4) if lives_rmse is not None else None,
        lives_changed_from_reference=lives_changed,
        mean_luma=round(mean_luma, 4),
        darkened_frame=mean_luma < 120.0,
    )


def image_rmse(left: Image.Image, right: Image.Image) -> float:
    left_array = np.asarray(left, dtype=np.float32)
    right_array = np.asarray(right.resize(left.size, Image.Resampling.NEAREST), dtype=np.float32)
    return float(np.sqrt(np.mean((left_array - right_array) ** 2)))
