"""
***** File Integrity Watcher *****
Auteur : Adrien RICQUE
Description : Fonctions utilitaires
"""
from datetime import datetime

class Timestamp_Utils:
    def timestamp_generator(self):  
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return timestamp


