from fastapi import HTTPException, UploadFile, status

# Magic-byte prefixes for the formats Ollama accepts and phone cameras produce.
IMAGE_SIGNATURES = {
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/webp": (b"RIFF",),
}


async def read_image(upload: UploadFile, max_bytes: int) -> bytes:
    """Validate type and size, and return the bytes in memory. Nothing touches disk."""
    if upload.content_type not in IMAGE_SIGNATURES:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Solo se aceptan fotos JPG, PNG o WEBP."
        )
    if upload.size is not None and upload.size > max_bytes:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "La foto es demasiado grande.")
    data = await upload.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "La foto es demasiado grande.")
    if not data.startswith(IMAGE_SIGNATURES[upload.content_type]):
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "El archivo no parece una foto válida."
        )
    return data
