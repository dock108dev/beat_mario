from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image


FIXTURE_STATES = {
    "title_menu.png": "TITLE_MENU",
    "world_1_map.png": "WORLD_1_MAP",
    "level_1_1_start.png": "LEVEL_1_1",
}


@dataclass(frozen=True)
class StateMatch:
    state: str
    fixture: str
    rmse: float
    confidence: float


@dataclass(frozen=True)
class StateDetection:
    state: str
    confidence: float
    best_match: StateMatch
    matches: list[StateMatch]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def detect_state(image_path: Path, fixtures_dir: Path) -> StateDetection:
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    if not fixtures_dir.exists():
        raise FileNotFoundError(f"Fixtures directory not found: {fixtures_dir}")

    target = normalize_image(Image.open(image_path))
    matches: list[StateMatch] = []

    for fixture_path in sorted(fixtures_dir.glob("*.png")):
        state = FIXTURE_STATES.get(fixture_path.name, fixture_path.stem.upper())
        fixture = normalize_image(Image.open(fixture_path))
        rmse = float(np.sqrt(np.mean((target - fixture) ** 2)))
        confidence = max(0.0, min(1.0, 1.0 - (rmse / 140.0)))
        matches.append(
            StateMatch(
                state=state,
                fixture=str(fixture_path),
                rmse=round(rmse, 4),
                confidence=round(confidence, 4),
            )
        )

    if not matches:
        raise RuntimeError(f"No PNG fixtures found in {fixtures_dir}")

    matches.sort(key=lambda match: match.rmse)
    best = matches[0]
    return StateDetection(
        state=best.state,
        confidence=best.confidence,
        best_match=best,
        matches=matches,
    )


def normalize_image(image: Image.Image) -> np.ndarray:
    grayscale = image.convert("L").resize((256, 224), Image.Resampling.BILINEAR)
    return np.asarray(grayscale, dtype=np.float32)

