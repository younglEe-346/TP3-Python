"""Le jeu de dames en objets : cases, pièces, plateau et partie.

Règles du jeu de dames international (plateau de 10 x 10), simplifiées : une seule prise par
coup (pas de rafle) et pas de règle de la majorité.
"""
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

from exceptions import CoupInvalideError

COLONNES = "abcdefghij"
TAILLE = 10
DIAGONALES = [(1, 1), (-1, 1), (1, -1), (-1, -1)]


def adversaire(couleur: str) -> str:
    """La couleur de l'autre joueur."""
    return "noir" if couleur == "blanc" else "blanc"


# --- Étape 1 : la case ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Case:
    """Une case, de a1 à j10. Immuable : on peut la hacher et s'en servir comme clé."""
    colonne: str
    ligne: int

    def __post_init__(self):
        """Refuse une colonne hors de a..j ou une ligne hors de 1..10 (ValueError)."""
        raise NotImplementedError("à compléter")

    @classmethod
    def depuis_nom(cls, nom: str) -> "Case":
        """Case.depuis_nom("c3") donne Case('c', 3) ; un nom mal formé lève ValueError."""
        raise NotImplementedError("à compléter")

    @property
    def est_noire(self) -> bool:
        """On ne joue que sur les cases noires ; a1 est noire."""
        raise NotImplementedError("à compléter")

    def decaler(self, dc: int, dl: int) -> "Case | None":
        """La case située dc colonnes et dl lignes plus loin, ou None si on sort du plateau."""
        raise NotImplementedError("à compléter")

    def __str__(self) -> str:
        raise NotImplementedError("à compléter")


def en_case(valeur: "Case | str") -> Case:
    """Accepte une Case ou un nom comme "c3"."""
    return valeur if isinstance(valeur, Case) else Case.depuis_nom(valeur)


def ordre(case: Case) -> tuple[int, int]:
    """Clé de tri : ligne par ligne, puis de gauche à droite."""
    return case.ligne, COLONNES.index(case.colonne)


# --- Étape 2 : les pièces ------------------------------------------------------------------------
class Piece(ABC):
    """Une pièce : une couleur qui ne change jamais. Elle ne connaît pas sa case :
    c'est le plateau qui sait où sont les pièces."""

    COULEURS = ("blanc", "noir")
    LETTRE = "?"          # redéfinis par chaque sous-classe
    NOM = "pièce"
    FEMININ = False

    def __init__(self, couleur: str):
        """Refuse une couleur autre que "blanc" ou "noir" (ValueError)."""
        raise NotImplementedError("à compléter")

    @property
    def couleur(self) -> str:
        """Lecture seule : pas de setter."""
        raise NotImplementedError("à compléter")

    @property
    def sens(self) -> int:
        """Le sens de la marche : +1 (vers la ligne 10) pour les blancs, -1 pour les noirs."""
        raise NotImplementedError("à compléter")

    @property
    def symbole(self) -> str:
        """La lettre en majuscule pour les blancs, en minuscule pour les noirs."""
        raise NotImplementedError("à compléter")

    def est_adverse(self, autre: "Piece | None") -> bool:
        """Vrai si autre est une pièce de l'autre couleur (faux pour None)."""
        raise NotImplementedError("à compléter")

    @abstractmethod
    def deplacements(self, case: Case, plateau: "Plateau") -> set[Case]:
        """Les cases où la pièce peut aller depuis case, sans prendre."""

    @abstractmethod
    def prises(self, case: Case, plateau: "Plateau") -> dict[Case, Case]:
        """Les prises possibles depuis case : {case d'arrivée: case de la pièce prise}."""

    def promouvoir(self, case: Case) -> "Piece":
        """La pièce qui occupe case après le coup. Par défaut, la pièce reste la même."""
        return self

    def __repr__(self) -> str:
        raise NotImplementedError("à compléter")

    def __str__(self) -> str:
        raise NotImplementedError("à compléter")


# --- Étape 3 : le plateau ------------------------------------------------------------------------
class Plateau:
    """Le plateau A des pièces (composition), rangées dans un dict privé case -> pièce."""

    def __init__(self):
        self._pieces: dict[Case, Piece] = {}

    @classmethod
    def depuis_dict(cls, pieces: dict[str, str]) -> "Plateau":
        """Constructeur alternatif : Plateau.depuis_dict({"c3": "P", "f6": "d"}).
        P = pion, D = dame ; majuscule pour les blancs, minuscule pour les noirs."""
        plateau = cls()
        for nom, lettre in pieces.items():
            couleur = "blanc" if lettre.isupper() else "noir"
            classe = Pion if lettre.upper() == "P" else Dame
            plateau.placer(nom, classe(couleur))
        return plateau

    @classmethod
    def position_initiale(cls) -> "Plateau":
        """Un pion sur chaque case noire : blancs en lignes 1 à 4, noirs en lignes 7 à 10."""
        raise NotImplementedError("à compléter")

    def placer(self, case: "Case | str", piece: Piece) -> None:
        """Pose une pièce. ValueError si la case est blanche ou déjà occupée."""
        raise NotImplementedError("à compléter")

    def __getitem__(self, case: "Case | str") -> "Piece | None":
        """plateau["c3"] : la pièce sur la case, ou None si elle est vide."""
        raise NotImplementedError("à compléter")

    def __contains__(self, case: "Case | str") -> bool:
        """"c3" in plateau : vrai si la case est occupée."""
        raise NotImplementedError("à compléter")

    def __len__(self) -> int:
        """Le nombre de pièces sur le plateau."""
        raise NotImplementedError("à compléter")

    def __iter__(self):
        """Parcourt les cases occupées, ligne par ligne, de gauche à droite."""
        return iter(sorted(self._pieces, key=ordre))

    def compter(self, couleur: str) -> int:
        return sum(1 for case in self if self[case].couleur == couleur)

    # --- Étape 6
    def prises_possibles(self, couleur: str) -> dict[Case, dict[Case, Case]]:
        """Toutes les prises d'un joueur : {départ: {arrivée: pièce prise}}, seulement pour les
        pièces qui peuvent prendre."""
        raise NotImplementedError("à compléter")

    def coups_possibles(self, couleur: str) -> list[tuple[Case, Case]]:
        """Les coups autorisés, triés. S'il existe des prises, seules les prises comptent."""
        raise NotImplementedError("à compléter")

    def deplacer(self, depart: "Case | str", arrivee: "Case | str") -> "Piece | None":
        """Joue un coup, renvoie la pièce prise ou None. Vérifier d'abord, modifier ensuite."""
        raise NotImplementedError("à compléter")

    # --- Étape 8
    def vers_dict(self) -> dict[str, str]:
        """L'inverse de depuis_dict : {"c3": "P", "f6": "d", ...}, dans l'ordre du plateau."""
        raise NotImplementedError("à compléter")

    # --- Affichage (fourni)
    def __repr__(self) -> str:
        return f"<Plateau : {self.compter('blanc')} blancs, {self.compter('noir')} noirs>"

    def __str__(self) -> str:
        lignes = []
        for ligne in range(TAILLE, 0, -1):
            cases = []
            for colonne in COLONNES:
                case = Case(colonne, ligne)
                piece = self[case]
                cases.append(piece.symbole if piece else "." if case.est_noire else " ")
            lignes.append(f"{ligne:>2}  " + " ".join(cases))
        lignes.append("    " + " ".join(COLONNES))
        return "\n".join(lignes)


# --- Étape 4 : le pion ---------------------------------------------------------------------------
class Pion(Piece):
    LETTRE = "P"
    NOM = "pion"

    def deplacements(self, case, plateau):
        """Une case en diagonale, vers l'avant, si elle est libre."""
        raise NotImplementedError("à compléter")

    def prises(self, case, plateau):
        """Sauter une pièce adverse voisine (avant ou arrière) vers la case libre derrière."""
        raise NotImplementedError("à compléter")

    # --- Étape 6
    def promouvoir(self, case):
        """Sur la dernière ligne (10 pour les blancs, 1 pour les noirs), le pion devient dame."""
        raise NotImplementedError("à compléter")


# --- Étape 5 : la dame ---------------------------------------------------------------------------
# À vous : écrivez ici la classe Dame (énoncé, étape 5).


# --- Étape 7 : la partie -------------------------------------------------------------------------
@dataclass(frozen=True)
class Coup:
    """Un coup joué. Gelé : un coup joué ne change plus."""
    numero: int
    couleur: str
    depart: str
    arrivee: str
    prise: bool = False

    def __str__(self) -> str:
        """Notation des dames : "1. c3-d4" pour un déplacement, "4. d4xf6" pour une prise."""
        raise NotImplementedError("à compléter")


class Partie:
    """Une partie A un plateau et un historique (composition) et sait à qui c'est le tour."""

    def __init__(self, plateau: "Plateau | None" = None):
        self.plateau = plateau if plateau is not None else Plateau.position_initiale()
        self.trait = "blanc"                  # la couleur qui doit jouer
        self.historique: list[Coup] = []

    def jouer(self, depart: str, arrivee: str) -> Coup:
        """Vérifie le trait, joue, note le coup, passe la main à l'adversaire."""
        raise NotImplementedError("à compléter")

    @property
    def gagnant(self) -> "str | None":
        """Celui qui a le trait et ne peut plus jouer a perdu : la couleur gagnante, ou None."""
        raise NotImplementedError("à compléter")

    # --- Étape 8
    def sauvegarder(self, chemin) -> None:
        """Écrit la partie en JSON : {"trait": ..., "pieces": {"c3": "P", ...}}."""
        raise NotImplementedError("à compléter")

    @classmethod
    def charger(cls, chemin) -> "Partie":
        """Constructeur alternatif : recrée une partie écrite par sauvegarder."""
        raise NotImplementedError("à compléter")
