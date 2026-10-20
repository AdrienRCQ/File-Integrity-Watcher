"""
***** File Integrity Watcher *****
Auteur : Adrien RICQUE
Description : Définition et récupération des arguments
"""

import argparse
from pathlib import Path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=""
    )

    parser.add_argument(
        "command",
        choices=["init","check"],
        help="Action à effectuer : créer une référence ou contrôler les fichiers"
    )

    parser.add_argument(
        "-t",
        "--target",
        type=Path,
        help="Chemin du fichier à analyser."
    )
    
    parser.add_argument(
        "-b",
        "--baseline",
        type=Path,
        help="Chemin du fichier JSON contenant l'inventaire de référence."
    )

    args = parser.parse_args()

    if args.command == "check" and args.baseline is None:
        parser.error("--baseline est obligatoire avec la commande check.")

    return args