# TP 3 : Le jeu de dames en objets

**Auteur :** Soulaimane Lbah
**Établissement :** École Nationale Supérieure d'Arts et Métiers de Casablanca (ENSAM)
**Module :** Programmation Avancée, partie Python · M1 S1 · Année universitaire 2026-2027

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Tests](https://img.shields.io/badge/tests-102%20passed-brightgreen)

---

## Présentation

Ce projet implémente le **jeu de dames international** (plateau de 10 x 10) en programmation orientée objet.
Deux joueurs peuvent s'affronter dans le terminal. Toutes les règles sont garanties par les classes :
déplacement des pions et des dames, prise obligatoire, prise à distance de la dame, promotion et fin de partie.

Simplifications prévues par l'énoncé : une seule prise par coup (pas de rafle) et pas de règle de la majorité.

## Structure du projet

```
tp3_dames/
├── dames.py              # Case, Piece, Pion, Dame, Plateau, Coup, Partie
├── exceptions.py         # ErreurDames, CoupInvalideError
├── main.py               # programme principal : partie à deux dans le terminal
├── RAPPORT.md            # explication détaillée et réponses aux questions « Pour réfléchir »
├── requirements.txt
├── pytest.ini
└── tests/
    ├── test_etape1.py … test_etape8.py   # tests fournis
    └── test_mes_tests.py                 # tests personnels (bonus étape 8)
```

## Conception

| Classe | Rôle | Notions mises en œuvre |
|---|---|---|
| `Case` | une case de a1 à j10 | dataclass gelée, `__post_init__`, `@classmethod`, `@property` |
| `Piece` | pièce abstraite, couleur immuable | classe abstraite (ABC), propriété en lecture seule |
| `Pion`, `Dame` | déplacements et prises propres à chaque pièce | héritage, redéfinition, polymorphisme |
| `Plateau` | contient les pièces, garantit les règles d'un coup | composition, `__getitem__`, `__contains__`, `__len__`, `__iter__` |
| `Coup` | un coup joué (`1. c3-d4`, `3. c5xe7`) | dataclass gelée |
| `Partie` | plateau, historique, trait, gagnant | composition, propriété calculée, JSON |
| `CoupInvalideError` | coup refusé avec sa raison | exception métier, `super()` |

**Choix de conception :** une pièce ne connaît pas sa case. Seul le plateau sait où sont les pièces.
Les méthodes reçoivent la case et le plateau en paramètres, par exemple `pion.deplacements(case, plateau)`.
La pièce et le plateau ne peuvent donc jamais se contredire.

`Plateau.deplacer` applique le principe **« vérifier d'abord, modifier ensuite »** :
un coup refusé ne modifie jamais le plateau.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate sous Linux/macOS)
pip install -r requirements.txt
```

## Utilisation

**Jouer une partie :**

```bash
python main.py
```

Les coups se saisissent sous la forme `c3 d4`, `c3-d4` ou `c5xe7`.

| Commande | Effet |
|---|---|
| `sauver` | enregistre la partie dans `partie.json` |
| `reprendre` | recharge la partie depuis `partie.json` |
| `quitter` | abandonne la partie |

**Exemple :**

```
blanc > d4 c5
1. d4-c5
noir > e7 d6
2. e7-d6
blanc > h4 g5
Refusé : coup h4-g5 refusé : la prise est obligatoire
blanc > c5 e7
3. c5xe7
```

**Console interactive :**

```python
>>> partie = Partie()
>>> partie.jouer("d4", "c5")
>>> print(partie.plateau)
```

## Tests

```bash
pytest
```

```
102 passed
```

| Étape | Contenu | Tests |
|---|---|---|
| 1 | La case | 23 |
| 2 | Les pièces | 11 |
| 3 | Le plateau, un conteneur | 9 |
| 4 | Le pion | 11 |
| 5 | La dame (classe écrite entièrement) | 11 |
| 6 | Jouer un coup | 12 |
| 7 | La partie et le programme | 17 |
| 8 | Sauvegarder une partie (JSON) | 5 |
| Bonus | Tests personnels (`test_mes_tests.py`) | 3 |

Tous les exemples de console de l'énoncé produisent exactement l'affichage attendu.

## Travail réalisé

- **Étapes 1 à 7** : toutes les méthodes du kit sont complétées et la classe `Dame` est écrite entièrement.
- **Étape 8** : sauvegarde et chargement d'une partie en JSON (`vers_dict`, `sauvegarder`, `charger`).
- **Bonus** : commandes `sauver` et `reprendre` dans `main.py`, avec tests personnels.
- **Défi de la rafle** et réponses aux questions « Pour réfléchir » : voir [RAPPORT.md](RAPPORT.md).
