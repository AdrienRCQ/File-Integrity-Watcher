"""
***** File Integrity Watcher *****
Auteur : Adrien RICQUE
Description : 
"""
from models import FileFingerprint
import json

def generate_snapshot(snap_data:dict[str, FileFingerprint], snap_name:str):
    serializable_data = {}
    for path, fingerprint in snap_data.items():
        serializable_data[path] = {
            "sha256" : fingerprint.sha256,
            "size" : fingerprint.size
        }
    json_data = json.dumps(serializable_data, indent=2)
    with open(snap_name, 'x') as f:
        f.write(json_data)