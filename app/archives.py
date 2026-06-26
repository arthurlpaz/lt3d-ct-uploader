"""
Archives
========
Flattened extraction of uploaded ZIP/TAR archives.

The archive's internal hierarchy is discarded: every file lands directly in the
patient folder (PACIENTE1.zip -> raw_data/PACIENTE1/*.dcm), no matter how many
nested directories the archive contains. Packaging cruft is skipped.
"""

import shutil
import tarfile
import zipfile
from pathlib import Path

from app.config import ARCHIVE_EXTS
from app.storage import is_junk, unique_path


def archive_stem(name: str) -> str:
    """Base name without archive extension: Paciente_001.tar.gz -> Paciente_001."""
    lower = name.lower()
    for ext in ARCHIVE_EXTS:
        if lower.endswith(ext):
            return Path(name[: -len(ext)]).name or "upload"
    return Path(name).stem or "upload"


def extract_zip(archive: Path, dest: Path) -> None:
    """Extract every file from a ZIP into dest, flattening the directory tree."""
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            if member.is_dir() or is_junk(member.filename):
                continue
            target = unique_path(dest, Path(member.filename).name)
            with zf.open(member) as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)


def extract_tar(archive: Path, dest: Path) -> None:
    """Extract every file from a TAR into dest, flattening the directory tree."""
    with tarfile.open(archive) as tf:
        for member in tf.getmembers():
            if not member.isfile() or is_junk(member.name):
                continue
            src = tf.extractfile(member)
            if src is None:
                continue
            target = unique_path(dest, Path(member.name).name)
            with src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)
