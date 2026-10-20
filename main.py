"""
***** File Integrity Watcher *****
Auteur : Adrien RICQUE
Description : 
"""
from cli import parse_args
from hasher import fingerprint_file, scan_directory
from comparison import compare_snapshots
from snapshot import generate_snapshot
from utils import Timestamp_Utils
import json
from pathlib import Path
from stat import S_ISREG, S_ISDIR
from models import FileFingerprint

tmutl = Timestamp_Utils()

def identify_target(target: Path) -> dict[str, FileFingerprint]:
    mode = target.lstat().st_mode
    if S_ISREG(mode):
        return {target.name: fingerprint_file(target)}
    if S_ISDIR(mode):
        return scan_directory(target)
    raise ValueError(f"Type de cible non pris en charge : {target}")


def main() -> None:
    args = parse_args()
    if args.command == "init":
        # Enregistrer l'état initial du fichier
        snapshot_data = identify_target(args.target)
        snapshot_name = f"Snpsht_{args.target.name}_{tmutl.timestamp_generator()}.json"
        generate_snapshot(snap_data= snapshot_data, snap_name= snapshot_name)
        
    if args.command == "check":
        snapshot_file = args.baseline
        with open(snapshot_file, "r", encoding="utf-8") as baseline_snapshot:
            raw_snapshot = json.load(baseline_snapshot)

        snapshot: dict[str, FileFingerprint] = {}

        for path, data in raw_snapshot.items():
            snapshot[path] = FileFingerprint(
                sha256=data["sha256"],
                size=data["size"],
            )
            
        current = identify_target(args.target)
        changes = compare_snapshots(snapshot, current)
        for change in changes:
            print(f"{change.path} : {change.kind}")


if __name__ == "__main__":
    main()