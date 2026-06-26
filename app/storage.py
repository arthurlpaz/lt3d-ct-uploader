"""
Storage
=======
Filesystem helpers for writing uploads safely under RAW_DATA.
"""

from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.config import CHUNK_SIZE, JUNK_DIRS, JUNK_NAMES, RAW_DATA


def safe_dest(*parts: str) -> Path:
    """Resolve a path inside RAW_DATA, blocking path traversal."""
    dest = (RAW_DATA / Path(*parts)).resolve()
    if not dest.is_relative_to(RAW_DATA):
        raise HTTPException(400, "Invalid path")
    return dest


async def save_upload(file: UploadFile, dest: Path) -> None:
    """Stream an UploadFile to disk without loading it all into memory."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as out:
        while chunk := await file.read(CHUNK_SIZE):
            out.write(chunk)


def sanitize_folder(name: str) -> str:
    """Normalize a patient folder name to the pipeline convention (spaces -> underscores)."""
    return "_".join(name.split())


def is_junk(member_path: str) -> bool:
    """True for packaging cruft (resource forks, OS metadata) we never want."""
    parts = Path(member_path).parts
    if any(part in JUNK_DIRS for part in parts):
        return True
    name = Path(member_path).name
    return name in JUNK_NAMES or name.startswith("._")


def unique_path(dest_dir: Path, filename: str) -> Path:
    """Return a non-colliding path inside dest_dir, suffixing _1, _2, ... if needed."""
    target = dest_dir / filename
    if not target.exists():
        return target
    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    while (target := dest_dir / f"{stem}_{counter}{suffix}").exists():
        counter += 1
    return target
