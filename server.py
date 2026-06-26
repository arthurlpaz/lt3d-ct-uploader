"""
ProtesIA — CT Uploader
======================
Entry point for the upload server that ships CT data to the HUAC VM.

    python server.py
    http://10.100.100.179:8000

The application itself lives in the `app/` package; this module only wires up
configuration and launches uvicorn.
"""

import uvicorn

from app.config import PORT, RAW_DATA, UPLOAD_PASS, UPLOAD_USER
from app.main import app

if __name__ == "__main__":
    print(f"\n  🦾 ProtesIA CT Uploader")
    print(f"  raw_data → {RAW_DATA}")
    print(f"  URL      → http://0.0.0.0:{PORT}")
    print(f"  Login    → {UPLOAD_USER} / {'*' * len(UPLOAD_PASS)}\n")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
