# File-Integrity-Watcher

Outil Python en ligne de commande pour comparer l’état d’un fichier ou d’un dossier à une référence enregistrée en JSON.

Chaque fichier est représenté par son empreinte **SHA-256** et sa **taille en octets**. Une comparaison permet de repérer les fichiers ajoutés, supprimés ou modifiés.

**Statut : prototype en cours de développement.** Les vérifications sont déclenchées à la demande avec la commande `check`. La version actuelle ne surveille pas les fichiers en continu et n’explore pas les sous-dossiers.

## Cas d’usage

- Vérifier si un fichier de configuration a changé depuis sa validation.
- Contrôler les fichiers d’un dossier de scripts avant et après une intervention.
- Repérer des ajouts ou des suppressions dans un répertoire.
- Pratiquer le hachage, la manipulation de fichiers, la sérialisation JSON et la conception d’une CLI Python.

Une différence indique un changement de contenu ou de présence. L’outil ne détermine pas si ce changement est légitime ou malveillant.

## Fonctionnement

1. **Créer une référence** avec `init` : analyser la cible et enregistrer les empreintes dans un fichier JSON.
2. **Conserver cette référence** : elle représente l’état à partir duquel les vérifications seront effectuées.
3. **Lancer une vérification** avec `check` : charger la référence et analyser à nouveau la même cible.
4. **Comparer les deux états** et afficher les changements.

| Résultat | Signification |
| --- | --- |
| `added` | Fichier présent dans l’état actuel et absent de la référence. |
| `removed` | Fichier présent dans la référence et absent de l’état actuel. |
| `modified` | Fichier présent dans les deux états, avec une empreinte SHA-256 ou une taille différente. |

Un changement de contenu peut être détecté même si la taille du fichier reste identique.

La commande `check` ne met pas à jour la baseline. Pour établir une nouvelle référence après validation des changements, relancer `init`.

## Préparer l’environnement

Environnement conseillé : **Python 3.10 ou supérieur** et un terminal.

Les modules présentés utilisent la bibliothèque standard Python, notamment `argparse`, `pathlib`, `hashlib`, `json` et `stat`. Aucune dépendance tierce n’est nécessaire pour les fonctionnalités décrites.

Depuis le dossier contenant `main.py`, vérifier Python et afficher l’aide :

```console
python --version
python main.py --help
```

Les exemples suivants utilisent PowerShell sous Windows. Sous Linux ou macOS, utiliser des chemins comme `./watched/config.ini` et, selon l’environnement, la commande `python3`.

## Utilisation

### Créer la référence d’un fichier

Préparer un fichier de test `config.ini` dans un dossier `watched`, puis lancer :

```powershell
python main.py init -t ".\watched\config.ini"
```

Le nom de la snapshot est généré automatiquement. Avec un timestamp au format `%Y%m%d_%H%M%S`, il ressemble à :

```text
Snpsht_config.ini_20261022_143025.json
```

Avec un nom relatif transmis à `open()`, le fichier est créé dans le répertoire depuis lequel la commande est exécutée.

L’argument `--baseline` n’est pas nécessaire pour `init`.

### Vérifier ce fichier

Utiliser le nom exact du JSON créé à l’étape précédente. L’horodatage ci-dessous est un exemple :

```powershell
python main.py check -t ".\watched\config.ini" --baseline ".\Snpsht_config.ini_20261022_143025.json"
```

Après une modification du contenu, le résultat peut être :

```text
config.ini : modified
```

Dans l’affichage actuel, une vérification réussie sans différence n’affiche aucune ligne. Une erreur ou une interruption ne doit pas être interprétée comme une absence de changement.

### Créer puis vérifier la référence d’un dossier

Depuis le dossier parent de `watched` :

```powershell
python main.py init -t ".\watched"
```

Puis, en remplaçant le nom de baseline par celui réellement généré :

```powershell
python main.py check -t ".\watched" --baseline ".\Snpsht_watched_20261022_143025.json"
```

Exemple de changements :

```text
config.ini : modified
nouveau_script.py : added
ancien_script.py : removed
```

Seuls les fichiers ordinaires directement présents dans le dossier sont analysés. Les sous-dossiers et les liens symboliques rencontrés sont ignorés.

**Conserver la baseline hors du dossier surveillé.** Sinon, le JSON créé après le premier scan sera lui-même détecté comme un fichier ajouté à la vérification suivante.

### Arguments

| Argument | Rôle | Utilisation |
| --- | --- | --- |
| `init` | Créer une snapshot de référence. | Première commande à lancer. |
| `check` | Comparer la cible à une référence existante. | Nécessite une baseline. |
| `-t <chemin>` | Désigner un fichier ou un dossier à analyser. | Utilisé avec les deux commandes. |
| `-b <chemin>` ou `--baseline <chemin>` | Désigner le JSON de référence. | Obligatoire avec `check`. |
| `-h` ou `--help` | Afficher l’aide. | Disponible depuis la CLI. |

## Format d’une snapshot

La baseline associe chaque nom de fichier à son empreinte SHA-256 et à sa taille.

Exemple pour un fichier `config.ini` vide :

```json
{
  "config.ini": {
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "size": 0
  }
}
```

| Champ | Type | Description |
| --- | --- | --- |
| Clé de l’entrée | Chaîne | Nom du fichier, sans le chemin absolu. |
| `sha256` | Chaîne | Empreinte hexadécimale SHA-256 du contenu. |
| `size` | Entier | Nombre d’octets lus. |

La snapshot contient des empreintes et des tailles, pas le contenu des fichiers. Elle ne permet donc pas de restaurer un fichier supprimé ou modifié.

## Organisation du code

| Module | Responsabilité |
| --- | --- |
| `main.py` | Identifier le type de cible et coordonner les commandes. |
| `cli.py` | Définir et lire les arguments de ligne de commande. |
| `models.py` | Définir les modèles `FileFingerprint` et `FileChange`. |
| `hasher.py` | Calculer les empreintes et analyser les fichiers d’un dossier. |
| `comparison.py` | Comparer les snapshots indépendamment de la lecture du disque. |
| `snapshot.py` | Convertir les empreintes en données JSON et écrire la référence. |
| `utils.py` | Fournir notamment le générateur de timestamp. |

Les fichiers sont lus en mode binaire, par blocs de **65 536 octets**, pour calculer leur empreinte sans charger tout leur contenu en mémoire.

Avant l’écriture JSON, les objets `FileFingerprint` sont convertis en dictionnaires. Après le chargement, ils doivent être reconstruits avant l’appel à `compare_snapshots()`.

## Limites actuelles

- **Analyse non récursive** : les fichiers des sous-dossiers ne sont pas pris en compte.
- **Vérification ponctuelle** : chaque commande observe un nouvel état ; aucune boucle de surveillance ne tourne en arrière-plan.
- **Cible absente** : un fichier ou un dossier passé à `-t` doit exister. La suppression d’un fichier ciblé individuellement provoque actuellement une erreur lors de `lstat()`. Les suppressions sont détectées comme `removed` dans un dossier qui existe toujours.
- **Liens symboliques** : une cible qui est elle-même un lien symbolique est refusée ; les liens rencontrés dans un dossier sont ignorés.
- **Métadonnées limitées** : les permissions, propriétaires et dates de modification ne sont pas comparés.
- **Renommages** : dans un dossier, un renommage est représenté par une suppression et un ajout.
- **Identification de la cible** : la baseline actuelle ne conserve pas son chemin d’origine. Utiliser la référence correspondant à la même cible ; le programme ne garantit pas cette association.
- **Fichiers en cours d’écriture** : la lecture par blocs ne garantit pas un état cohérent si un autre programme modifie le fichier pendant le calcul.
- **Gestion des erreurs** : les erreurs de lecture, de JSON ou de cible ne disposent pas encore toutes de messages utilisateur dédiés.

Pour un usage de contrôle d’intégrité, établir la référence à partir d’un état connu et protéger son accès en écriture. Une personne pouvant modifier les fichiers et leur baseline pourrait remplacer les deux. La baseline actuelle n’est ni signée ni authentifiée.

## Validation manuelle

Effectuer ces essais sur des fichiers de test, en conservant la même baseline entre les vérifications.

| Essai | Résultat attendu |
| --- | --- |
| Vérifier immédiatement après `init`. | Aucune différence affichée, sans erreur. |
| Modifier le contenu d’un fichier. | `modified`. |
| Remplacer `abc` par `abd`, sans changer l’encodage ni la fin de ligne. | `modified`, malgré une taille identique. |
| Ajouter un fichier directement dans le dossier surveillé. | `added`. |
| Supprimer un fichier directement dans le dossier surveillé. | `removed`. |
| Modifier uniquement un fichier d’un sous-dossier. | Aucune différence dans le périmètre actuel. |

Cette liste décrit les contrôles à effectuer ; elle ne constitue pas un compte rendu de tests automatisés.

## Dépannage

| Symptôme | Point à vérifier |
| --- | --- |
| Fichier généré apparemment vide ou sans extension `.json`. | Afficher le nom généré et vérifier le timestamp. Utiliser un format comme `%Y%m%d_%H%M%S`, sans `:` ni séparateur de chemin. |
| `TypeError` lors de l’écriture JSON. | Convertir les objets `FileFingerprint` en dictionnaires contenant `sha256` et `size`. |
| `AttributeError` sur `sha256` ou `size` pendant la comparaison. | Reconstruire les `FileFingerprint` après `json.load()`. |
| `NameError` concernant `snapshot_file`. | Affecter `args.baseline` à cette variable avant son utilisation dans `check`. |
| `JSONDecodeError`. | Vérifier que la baseline contient un document JSON valide et complet. Son extension ne suffit pas à valider son contenu. |
| `FileNotFoundError`. | Vérifier les chemins de cible et de baseline, ainsi que le répertoire courant. |
| `PermissionError`. | Vérifier les droits de lecture sur la cible et d’écriture dans le dossier de sortie. |
| `FileExistsError` avec une création en mode `x`. | Le nom de sortie existe déjà. Générer un nouveau nom pour conserver la référence précédente. |

Pour empêcher l’écrasement accidentel d’une baseline, utiliser le mode de création exclusive `x` dans la fonction d’écriture.
