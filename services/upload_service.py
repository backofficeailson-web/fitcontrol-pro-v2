"""
Upload service — armazenamento seguro com validação MIME, tamanho e nome.
"""
from __future__ import annotations

import hashlib
import mimetypes
import os
import secrets
from datetime import datetime, UTC
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


ALLOWED_MIME_BY_CATEGORY = {
    "images": {"image/png", "image/jpeg", "image/webp", "image/gif"},
    "reports": {"application/pdf"},
    "posture": {"image/png", "image/jpeg", "image/webp"},
    "ai_analysis": {
        "application/zip",
        "application/x-zip-compressed",
        "application/pdf",
        "image/png", "image/jpeg", "image/webp",
        "text/plain", "text/x-python", "text/html", "text/css", "text/javascript",
        "application/json", "application/octet-stream",
    },
    "temp": None,  # no restriction
}

ALLOWED_EXT_BY_CATEGORY = {
    "images": {".png", ".jpg", ".jpeg", ".webp", ".gif"},
    "reports": {".pdf"},
    "posture": {".png", ".jpg", ".jpeg", ".webp"},
    "ai_analysis": {
        ".zip", ".pdf", ".png", ".jpg", ".jpeg", ".webp",
        ".py", ".html", ".css", ".js", ".json", ".txt", ".md",
        ".sql", ".yml", ".yaml", ".toml", ".ini", ".cfg",
    },
    "temp": None,
}


class UploadError(ValueError):
    """Erro de upload (tamanho, MIME, extensão ou conteúdo)."""


class UploadService:
    @staticmethod
    def _upload_root() -> Path:
        root = Path(current_app.config["UPLOAD_DIR"])
        for sub in ("images", "reports", "posture", "ai_analysis", "temp"):
            (root / sub).mkdir(parents=True, exist_ok=True)
        return root

    @staticmethod
    def _max_size() -> int:
        return int(current_app.config.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))

    @staticmethod
    def _validate(file: FileStorage, category: str) -> None:
        if category not in ALLOWED_EXT_BY_CATEGORY:
            raise UploadError(f"Categoria de upload inválida: {category}")
        if not file or not file.filename:
            raise UploadError("Nenhum arquivo enviado.")

        # Tamanho
        file.stream.seek(0, os.SEEK_END)
        size = file.stream.tell()
        file.stream.seek(0)
        if size <= 0:
            raise UploadError("Arquivo vazio.")
        if size > UploadService._max_size():
            raise UploadError(
                f"Arquivo muito grande ({size // 1024} KB). "
                f"Máximo permitido: {UploadService._max_size() // 1024} KB."
            )

        # Extensão
        ext = Path(file.filename).suffix.lower()
        allowed_ext = ALLOWED_EXT_BY_CATEGORY[category]
        if allowed_ext is not None and ext not in allowed_ext:
            raise UploadError(
                f"Extensão '{ext}' não permitida em '{category}'. "
                f"Permitidas: {sorted(allowed_ext)}"
            )

        # MIME
        allowed_mime = ALLOWED_MIME_BY_CATEGORY.get(category)
        if allowed_mime is not None:
            declared = (file.mimetype or "").lower()
            guessed = (mimetypes.guess_type(file.filename)[0] or "").lower()
            if declared not in allowed_mime and guessed not in allowed_mime:
                raise UploadError(
                    f"Tipo MIME '{declared or guessed}' não permitido em '{category}'."
                )

    @staticmethod
    def save(file: FileStorage, category: str, owner_id: int) -> dict:
        """Salva o arquivo e retorna metadados."""
        UploadService._validate(file, category)

        safe_name = secure_filename(file.filename) or "arquivo"
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        token = secrets.token_hex(4)
        final_name = f"u{owner_id}_{stamp}_{token}_{safe_name}"

        target_dir = UploadService._upload_root() / category
        target_path = target_dir / final_name
        file.save(str(target_path))

        # Hash para integridade
        sha256 = hashlib.sha256()
        with open(target_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                sha256.update(chunk)

        rel_path = f"uploads/{category}/{final_name}"
        return {
            "filename": final_name,
            "original_name": file.filename,
            "path": rel_path,                       # path relativo a /static/
            "absolute_path": str(target_path),
            "size_bytes": target_path.stat().st_size,
            "mime": file.mimetype or mimetypes.guess_type(file.filename)[0] or "",
            "sha256": sha256.hexdigest(),
            "category": category,
        }

    @staticmethod
    def delete(rel_path: str) -> bool:
        """Remove arquivo dado caminho relativo a /static/."""
        if not rel_path or ".." in rel_path:
            return False
        static_root = Path(current_app.static_folder)
        full = (static_root / rel_path).resolve()
        try:
            full.relative_to(static_root.resolve())
        except ValueError:
            return False
        if full.is_file():
            full.unlink()
            return True
        return False
