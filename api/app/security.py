import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.config import Settings, get_settings


def require_access_code(
    settings: Annotated[Settings, Depends(get_settings)],
    x_access_code: Annotated[str | None, Header()] = None,
) -> None:
    expected = settings.access_code.get_secret_value()
    if not expected or not x_access_code or not secrets.compare_digest(x_access_code, expected):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Código de acceso incorrecto.")
