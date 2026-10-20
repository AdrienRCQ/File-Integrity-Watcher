from models import FileChange, FileFingerprint

def compare_snapshots(
    previous: dict[str, FileFingerprint],
    current: dict[str, FileFingerprint]) -> list[FileChange]:
    result : list = []
    for path in current:
        if path not in previous:
            change = FileChange(path=path, kind="added")
            result.append(change)
    for path in previous:
        if path not in current:
            change = FileChange(path=path, kind="removed")
            result.append(change)

    return result


# tests :
# Empreinte fictive : aucun fichier réel n'est lu.
fingerprint = FileFingerprint(sha256="a" * 64, size=10)

previous = {
    "config.ini": fingerprint,
    "ancien.txt": fingerprint,
}

current = {
    "config.ini": fingerprint,
}

changes = compare_snapshots(previous, current)
print(changes)