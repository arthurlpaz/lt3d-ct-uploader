"""
Configuration
=============
Environment loading, filesystem paths and shared constants.

Credentials come from the UPLOAD_USER / UPLOAD_PASS environment variables
(defined in .env and injected by docker compose).
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # load .env for local runs; in the container compose injects the vars


def _require_env(name: str) -> str:
    """Read a required environment variable or exit with a clear error."""
    value = os.getenv(name)
    if not value:
        sys.exit(f"Error: environment variable {name} is not set (configure it in .env).")
    return value


# ── Paths ──────────────────────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
RAW_DATA   = Path(os.getenv("RAW_DATA_DIR", BASE_DIR / "raw_data")).resolve()
RAW_DATA.mkdir(parents=True, exist_ok=True)

PORT = int(os.getenv("PORT", "8000"))

# ── Auth ───────────────────────────────────────────────────────────────────────────

UPLOAD_USER = os.getenv("UPLOAD_USER", "protesia")
UPLOAD_PASS = _require_env("UPLOAD_PASS")
REALM       = "ProtesIA CT Uploader"

# ── Archives ───────────────────────────────────────────────────────────────────────

ARCHIVE_EXTS = (".tar.gz", ".tar.bz2", ".tgz", ".tar", ".zip")
TAR_EXTS     = (".tar.gz", ".tar.bz2", ".tgz", ".tar")
CHUNK_SIZE   = 1 << 20  # 1 MiB

# Packaging artifacts to drop while extracting archives.
JUNK_DIRS  = {"__MACOSX"}
JUNK_NAMES = {".DS_Store", "Thumbs.db"}
