import time
from pathlib import Path
from fastapi import UploadFile
from src.utils import validate_file


class FileService:

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

    async def save_uploaded_file(self, file: UploadFile) -> str:
        content = await file.read()
        validate_file(file, content)

        timestamp = int(time.time())
        file_name = f"{timestamp}-{file.filename}"
        file_path = self.upload_dir / file_name

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        return f"/{self.upload_dir}/{file_name}"

    async def save_optional_file(
        self,
        file: UploadFile | None,
        default_path: str = "/images/default.jpg"
    ) -> str:
        if file:
            return await self.save_uploaded_file(file)
        return default_path


# Singleton instance
file_service = FileService()
