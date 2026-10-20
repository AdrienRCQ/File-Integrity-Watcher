"""
***** File Integrity Watcher *****
Auteur : Adrien RICQUE
Description : 
"""

import hashlib
from pathlib import Path
from models import FileFingerprint
from stat import S_ISREG

def fingerprint_file(path:Path) -> FileFingerprint:
    hasher = hashlib.sha256()
    size = 0
    with path.open("rb") as file:
        while True:
            block = file.read(65_536)
            if not block:
                break
            hasher.update(block)
            size += len(block)
    digest = hasher.hexdigest()
    return FileFingerprint(sha256=digest, size=size)

def scan_directory(root:Path) -> dict[str, FileFingerprint]:
    snapshot: dict[str, FileFingerprint] = {}
    for path in root.iterdir():
        mode = path.lstat().st_mode
        # garder uniquement les fichiers ordinaires
        if not S_ISREG(mode):
            continue
        fingerprint = fingerprint_file(path)
        snapshot[path.name] = fingerprint
    return snapshot
