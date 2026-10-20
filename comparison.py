"""
***** File Integrity Watcher *****
Auteur : Adrien RICQUE
Description : 
"""

from models import FileChange, FileFingerprint
from hasher import fingerprint_file, scan_directory
from pathlib import Path

def compare_snapshots(
    previous: dict[str, FileFingerprint],
    current: dict[str, FileFingerprint]) -> list[FileChange]:
    result : list = []
    for path in current:
        if path not in previous:
            change = FileChange(path=path, kind="added")
            result.append(change)
        else :
            old = previous[path]
            new = current[path]
            if old.sha256 != new.sha256 or old.size != new.size:
                change = FileChange(path=path, kind="modified")
                result.append(change)
            
    for path in previous:
        if path not in current:
            change = FileChange(path=path, kind="removed")
            result.append(change)
    # Retourner les changements en utilisant leur attribut path pour les classer
    return sorted(result, key=lambda change: change.path)
