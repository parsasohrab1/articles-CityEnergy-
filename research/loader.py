"""Download Building Data Genome 2 v1.0 and refuse a file whose hash does not match."""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"

DATASET_NAME = "Building Data Genome Project 2"
DATASET_VERSION = "v1.0"
DATASET_DOI = "10.5281/zenodo.3887306"
PAPER_DOI = "10.1038/s41597-020-00712-x"
DATA_LICENSE = "CC-BY-4.0"
SOFTWARE_LICENSE_OF_UPSTREAM_REPO = "MIT"
ELECTRICITY_URL = (
    "https://media.githubusercontent.com/media/buds-lab/"
    "building-data-genome-project-2/v1.0/data/meters/cleaned/electricity_cleaned.csv"
)
METADATA_URL = (
    "https://media.githubusercontent.com/media/buds-lab/"
    "building-data-genome-project-2/v1.0/data/metadata/metadata.csv"
)
ELECTRICITY_BYTES = 177_466_613
METADATA_SHA256 = "992d0b29f24f96ad4332bc4dbb534b7bdd7dd2689aad093f94e93068ecddca02"
ELECTRICITY_SHA256 = "b01056f4ceec1992ce019297e674d6d6ecd0240e50a2aaeb6f958c65efdc282d"

METADATA_COLUMNS = ["building_id", "site_id", "primaryspaceusage", "sqm"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    request = urllib.request.Request(url, headers={"User-Agent": "cityenergy-research"})
    with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    temporary.replace(path)


def _ensure(path: Path, url: str, expected_hash: str, expected_bytes: int | None) -> str:
    if path.exists():
        digest = sha256_file(path)
        if digest == expected_hash:
            return digest
    _download(url, path)
    size = path.stat().st_size
    if expected_bytes is not None and size != expected_bytes:
        raise RuntimeError(f"{path.name} has {size} bytes, expected {expected_bytes}")
    digest = sha256_file(path)
    if digest != expected_hash:
        raise RuntimeError(f"{path.name} sha256 {digest} does not match the pinned v1.0 hash")
    return digest


def ensure_dataset() -> dict[str, str]:
    """Return pinned hashes after the cache matches the v1.0 release."""
    if not ELECTRICITY_SHA256 or set(ELECTRICITY_SHA256) == {"0"} or len(ELECTRICITY_SHA256) != 64:
        raise RuntimeError("ELECTRICITY_SHA256 is not pinned to the v1.0 file")
    electricity_hash = _ensure(
        CACHE / "electricity_cleaned.csv",
        ELECTRICITY_URL,
        ELECTRICITY_SHA256,
        ELECTRICITY_BYTES,
    )
    metadata_hash = _ensure(CACHE / "metadata.csv", METADATA_URL, METADATA_SHA256, None)
    return {"electricity_sha256": electricity_hash, "metadata_sha256": metadata_hash}


def load_tables() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]:
    hashes = ensure_dataset()
    meters = pd.read_csv(CACHE / "electricity_cleaned.csv", low_memory=False)
    if "timestamp" not in meters.columns:
        raise RuntimeError("electricity file has no timestamp column")
    meters["timestamp"] = pd.to_datetime(meters["timestamp"])
    meters = meters.sort_values("timestamp", kind="mergesort").reset_index(drop=True)
    if not meters["timestamp"].is_unique:
        raise RuntimeError("electricity timestamps are not unique")
    metadata = pd.read_csv(CACHE / "metadata.csv", low_memory=False)
    missing = [column for column in METADATA_COLUMNS if column not in metadata.columns]
    if missing:
        raise RuntimeError(f"metadata is missing {missing}")
    metadata = metadata.loc[:, METADATA_COLUMNS].copy()
    if metadata["building_id"].duplicated().any():
        raise RuntimeError("metadata building_id values are not unique")
    return meters, metadata, hashes
