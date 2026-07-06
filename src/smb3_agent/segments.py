from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from smb3_agent.goals import GoalContract


SUPPORTED_SEGMENT_STATUSES = {"planned", "solved", "flaky", "bridged", "blocked"}
REQUIRED_SEGMENT_FIELDS = (
    "id",
    "name",
    "status",
    "start_condition",
    "success_condition",
    "failure_conditions",
    "current_method",
)


class SegmentValidationError(ValueError):
    pass


@dataclass(frozen=True)
class RouteSegment:
    id: str
    name: str
    status: str
    start_condition: dict[str, Any]
    success_condition: dict[str, Any]
    failure_conditions: tuple[dict[str, Any], ...]
    current_method: dict[str, Any]
    evidence: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class SegmentCatalog:
    catalog_id: str
    game: str
    segments: tuple[RouteSegment, ...]
    path: Path

    @property
    def by_id(self) -> dict[str, RouteSegment]:
        return {segment.id: segment for segment in self.segments}


def load_segment_catalog(path: Path) -> SegmentCatalog:
    if not path.is_file():
        raise SegmentValidationError(f"Segment catalog not found: {path}")

    raw = yaml.safe_load(path.read_text()) or {}
    if not isinstance(raw, dict):
        raise SegmentValidationError("Segment catalog must be a YAML mapping")

    _require_fields(raw, ("catalog_id", "game", "segments"))
    if not isinstance(raw["segments"], list) or not raw["segments"]:
        raise SegmentValidationError("segments must be a non-empty list")

    segments = tuple(_load_segment(index, item) for index, item in enumerate(raw["segments"]))
    ids = [segment.id for segment in segments]
    duplicates = sorted({segment_id for segment_id in ids if ids.count(segment_id) > 1})
    if duplicates:
        raise SegmentValidationError(f"Duplicate segment id(s): {', '.join(duplicates)}")

    return SegmentCatalog(
        catalog_id=str(raw["catalog_id"]),
        game=str(raw["game"]),
        segments=segments,
        path=path,
    )


def validate_goal_segments(contract: GoalContract, catalog: SegmentCatalog) -> None:
    missing = [segment_id for segment_id in contract.segments if segment_id not in catalog.by_id]
    if missing:
        raise SegmentValidationError(
            f"Goal {contract.id} references missing segment(s): {', '.join(missing)}"
        )


def render_goal_status(contract: GoalContract, catalog: SegmentCatalog) -> str:
    validate_goal_segments(contract, catalog)
    segments = catalog.by_id
    lines = [
        f"goal_id={contract.id}",
        f"catalog_id={catalog.catalog_id}",
        f"segments={len(contract.segments)}",
    ]
    for index, segment_id in enumerate(contract.segments, start=1):
        segment = segments[segment_id]
        bridge = " bridged=true" if segment_id in contract.bridged_segments else " bridged=false"
        evidence = ",".join(segment.evidence) if segment.evidence else "none"
        lines.append(
            f"{index}. id={segment.id} status={segment.status}{bridge} "
            f"method={segment.current_method['type']} evidence={evidence}"
        )
    return "\n".join(lines)


def _load_segment(index: int, raw: Any) -> RouteSegment:
    if not isinstance(raw, dict):
        raise SegmentValidationError(f"segments[{index}] must be a mapping")
    _require_fields(raw, REQUIRED_SEGMENT_FIELDS)

    segment_id = raw["id"]
    if not isinstance(segment_id, str) or not segment_id:
        raise SegmentValidationError(f"segments[{index}].id must be a non-empty string")

    status = raw["status"]
    if status not in SUPPORTED_SEGMENT_STATUSES:
        raise SegmentValidationError(f"Unsupported status for {segment_id}: {status}")

    for field in ("start_condition", "success_condition", "current_method"):
        if not isinstance(raw[field], dict):
            raise SegmentValidationError(f"{segment_id}.{field} must be a mapping")
    _require_fields(raw["current_method"], ("type",))

    failures = raw["failure_conditions"]
    if not isinstance(failures, list) or not failures or not all(isinstance(item, dict) for item in failures):
        raise SegmentValidationError(f"{segment_id}.failure_conditions must be a non-empty list of mappings")

    evidence = raw.get("evidence", ())
    if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
        raise SegmentValidationError(f"{segment_id}.evidence must be a list of strings")

    notes = raw.get("notes", "")
    if not isinstance(notes, str):
        raise SegmentValidationError(f"{segment_id}.notes must be a string")

    return RouteSegment(
        id=segment_id,
        name=str(raw["name"]),
        status=status,
        start_condition=raw["start_condition"],
        success_condition=raw["success_condition"],
        failure_conditions=tuple(failures),
        current_method=raw["current_method"],
        evidence=tuple(evidence),
        notes=notes,
    )


def _require_fields(data: dict[str, Any], fields: tuple[str, ...]) -> None:
    missing = [field for field in fields if field not in data]
    if missing:
        raise SegmentValidationError(f"Missing required field(s): {', '.join(missing)}")

