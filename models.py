"""
***** File Integrity Watcher *****
Auteur : Adrien RICQUE
Description : 
"""

from pathlib import Path
from typing import Literal
from dataclasses import dataclass

@dataclass
class FileFingerprint:
    sha256 : str
    size : int

@dataclass
class FileChange:
    path: Path
    kind: Literal["added", "removed","modified"]
    