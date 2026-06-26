"""
API
===
Disk usage, patient listing and the upload endpoints.
"""

import shutil
import tarfile
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.archives import archive_stem, extract_tar, extract_zip
from app.config import RAW_DATA, TAR_EXTS
from app.storage import safe_dest, sanitize_folder, save_upload

router = APIRouter(prefix="/api")


@router.get("/disk")
async def disk_info():
    """Report VM disk usage and the size of the raw_data folder."""
    usage    = shutil.disk_usage(RAW_DATA)
    raw_size = sum(f.stat().st_size for f in RAW_DATA.rglob("*") if f.is_file())
    return {
        "total":         usage.total,
        "used":          usage.used,
        "free":          usage.free,
        "raw_data_size": raw_size,
    }


@router.get("/patients")
async def list_patients():
    """List patients (folders) and loose files in raw_data."""
    items = []
    for p in sorted(RAW_DATA.iterdir()):
        if p.name.startswith("."):
            continue

        if p.is_dir():
            files      = [f for f in p.rglob("*") if f.is_file()]
            total_size = sum(f.stat().st_size for f in files)
            mtime      = max((f.stat().st_mtime for f in files), default=0)
            items.append({
                "name":          p.name,
                "type":          "folder",
                "files":         len(files),
                "size":          total_size,
                "last_modified": datetime.fromtimestamp(mtime).isoformat() if mtime else None,
            })
        elif p.is_file():
            st = p.stat()
            items.append({
                "name":          p.name,
                "type":          "file",
                "files":         1,
                "size":          st.st_size,
                "last_modified": datetime.fromtimestamp(st.st_mtime).isoformat(),
            })

    return {"patients": items, "path": str(RAW_DATA)}


@router.post("/upload/files")
async def upload_files(
    file: UploadFile = File(...),
    relative_path: str = Form(""),
):
    """Upload a single file. relative_path preserves the folder hierarchy."""
    rel   = relative_path or file.filename or "file"
    parts = [sanitize_folder(p) for p in Path(rel).parts]
    dest  = safe_dest(*parts)
    await save_upload(file, dest)
    return {"ok": True, "path": str(dest.relative_to(RAW_DATA))}


@router.post("/upload/archive")
async def upload_archive(file: UploadFile = File(...)):
    """Receive a ZIP or TAR.GZ and extract it (flattened) into raw_data/<archive_name>/.

    The archive's internal hierarchy is discarded: every file lands directly in the
    patient folder (PACIENTE1.zip -> raw_data/PACIENTE1/*.dcm), no matter how many
    nested directories the archive contains. Packaging cruft is skipped.
    """
    name        = file.filename or "archive.zip"
    folder_name = sanitize_folder(archive_stem(name))
    dest        = safe_dest(folder_name)
    dest.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix="".join(Path(name).suffixes)) as tmp:
        tmp_path = Path(tmp.name)
    await save_upload(file, tmp_path)

    lower = name.lower()
    try:
        if lower.endswith(".zip"):
            extract_zip(tmp_path, dest)
        elif lower.endswith(TAR_EXTS):
            extract_tar(tmp_path, dest)
        else:
            raise HTTPException(400, "Use .zip, .tar.gz or .tgz")
    except (zipfile.BadZipFile, tarfile.TarError) as exc:
        raise HTTPException(400, f"Corrupted archive: {exc}")
    finally:
        tmp_path.unlink(missing_ok=True)

    return {"ok": True, "folder": folder_name}
