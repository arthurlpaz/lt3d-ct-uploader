"""
Security
========
HTTP Basic authentication used as a global dependency on the app.
"""

import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import REALM, UPLOAD_PASS, UPLOAD_USER

security = HTTPBasic(realm=REALM)


def verify(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Validate username and password (HTTP Basic Auth) in constant time."""
    user_ok = secrets.compare_digest(credentials.username.encode(), UPLOAD_USER.encode())
    pass_ok = secrets.compare_digest(credentials.password.encode(), UPLOAD_PASS.encode())
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": f'Basic realm="{REALM}"'},
        )
    return credentials.username
