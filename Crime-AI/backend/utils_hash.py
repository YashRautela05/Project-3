# backend/utils_hash.py

import hashlib

def compute_video_hash(file_path: str, chunk_size: int = 1024 * 1024) -> str:
    """
    Compute a stable SHA256 hash for a video file, without loading
    the entire file into memory.
    """
    hasher = hashlib.sha256()

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()
