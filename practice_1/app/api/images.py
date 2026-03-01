from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
)
import shutil
import uuid
from pathlib import Path
from config import settings

router = APIRouter(
    tags=["Images"],
    prefix=settings.url.images,
)

upload_dir = Path("static/uploads")

@router.post("/upload-image")
async def upload_image(file: UploadFile = File()):
    ext = Path(file.filename).suffix.lower()
    if ext not in {".png", ".jpg", ".webp"}:
        raise HTTPException(400, "Only png, jpg, jpeg and webp")
    filename = f"{uuid.uuid4()}{ext}"
    path = upload_dir / filename

    with path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"url": f"/static/uploads/{filename}"}