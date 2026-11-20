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
        if len(self.colonne) != 1 or self.colonne not in COLONNES:
            raise ValueError(f"colonne invalide : {self.colonne!r}")
        if not 1 <= self.ligne <= TAILLE:
            raise ValueError(f"ligne invalide : {self.ligne!r}")

    @classmethod
    def depuis_nom(cls, nom: str) -> "Case":
        """Case.depuis_nom("c3") donne Case('c', 3) ; un nom mal formé lève ValueError."""
        try:
            return cls(nom[0], int(nom[1:]))
        except (ValueError, IndexError):
            raise ValueError(f"nom de case invalide : {nom!r}") from None

    @property
    def est_noire(self) -> bool:
        """On ne joue que sur les cases noires ; a1 est noire."""
        return (COLONNES.index(self.colonne) + self.ligne) % 2 == 1

    def decaler(self, dc: int, dl: int) -> "Case | None":
        """La case située dc colonnes et dl lignes plus loin, ou None si on sort du plateau."""
        indice = COLONNES.index(self.colonne) + dc
        ligne = self.ligne + dl
        if not (0 <= indice < TAILLE and 1 <= ligne <= TAILLE):
            return None
        return Case(COLONNES[indice], ligne)

    def __str__(self) -> str:
        return f"{self.colonne}{self.ligne}"


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
        if couleur not in Piece.COULEURS:
            raise ValueError(f"couleur invalide : {couleur!r}")
        self._couleur = couleur

    @property
    def couleur(self) -> str:
        """Lecture seule : pas de setter."""
        return self._couleur

    @property
    def sens(self) -> int:
        """Le sens de la marche : +1 (vers la ligne 10) pour les blancs, -1 pour les noirs."""
        return 1 if self._couleur == "blanc" else -1

    @property
    def symbole(self) -> str:
        """La lettre en majuscule pour les blancs, en minuscule pour les noirs."""
        return self.LETTRE.upper() if self._couleur == "blanc" else self.LETTRE.lower()

    def est_adverse(self, autre: "Piece | None") -> bool:
        """Vrai si autre est une pièce de l'autre couleur (faux pour None)."""
        return autre is not None and autre.couleur != self._couleur

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
        return f"{type(self).__name__}({self._couleur!r})"

    def __str__(self) -> str:
        couleur = self._couleur
        if self.FEMININ:
            couleur = "blanche" if couleur == "blanc" else "noire"
        return f"{self.NOM} {couleur}"


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
        plateau = cls()
        for ligne in range(1, TAILLE + 1):
            if ligne <= 4:
                couleur = "blanc"
            elif ligne >= 7:
                couleur = "noir"
            else:
                continue                      # lignes 5 et 6 : vides
            for colonne in COLONNES:
                case = Case(colonne, ligne)
                if case.est_noire:
                    plateau.placer(case, Pion(couleur))
        return plateau

    def placer(self, case: "Case | str", piece: Piece) -> None:
        """Pose une pièce. ValueError si la case est blanche ou déjà occupée."""
        case = en_case(case)
        if not case.est_noire:
            raise ValueError(f"{case} est une case blanche")
        if case in self._pieces:
            raise ValueError(f"{case} est déjà occupée")
        self._pieces[case] = piece

    def __getitem__(self, case: "Case | str") -> "Piece | None":
        """plateau["c3"] : la pièce sur la case, ou None si elle est vide."""
        return self._pieces.get(en_case(case))

    def __contains__(self, case: "Case | str") -> bool:
        """"c3" in plateau : vrai si la case est occupée."""
        return en_case(case) in self._pieces

    def __len__(self) -> int:
        """Le nombre de pièces sur le plateau."""
        return len(self._pieces)

    def __iter__(self):
        """Parcourt les cases occupées, ligne par ligne, de gauche à droite."""
        return iter(sorted(self._pieces, key=ordre))

    def compter(self, couleur: str) -> int:
        return sum(1 for case in self if self[case].couleur == couleur)

    # --- Étape 6
    def prises_possibles(self, couleur: str) -> dict[Case, dict[Case, Case]]:
        """Toutes les prises d'un joueur : {départ: {arrivée: pièce prise}}, seulement pour les
        pièces qui peuvent prendre."""
        resultat = {}
        for case in self:
            piece = self[case]
            if piece.couleur == couleur:
                prises = piece.prises(case, self)
                if prises:
                    resultat[case] = prises
        return resultat

    def coups_possibles(self, couleur: str) -> list[tuple[Case, Case]]:
        """Les coups autorisés, triés. S'il existe des prises, seules les prises comptent."""
        prises = self.prises_possibles(couleur)
        if prises:
            coups = [(depart, arrivee)
                     for depart, arrivees in prises.items() for arrivee in arrivees]
        else:
            coups = [(case, arrivee)
                     for case in self if self[case].couleur == couleur
                     for arrivee in self[case].deplacements(case, self)]
        return sorted(coups, key=lambda coup: (ordre(coup[0]), ordre(coup[1])))

    def deplacer(self, depart: "Case | str", arrivee: "Case | str") -> "Piece | None":
        """Joue un coup, renvoie la pièce prise ou None. Vérifier d'abord, modifier ensuite."""
        depart, arrivee = en_case(depart), en_case(arrivee)
        piece = self[depart]
        # 1. Vérifier d'abord : rien ne bouge tant qu'une règle est violée.
        if piece is None:
            raise CoupInvalideError(depart, arrivee, "aucune pièce sur la case de départ")
        prise = None
        if self.prises_possibles(piece.couleur):
            prises = piece.prises(depart, self)
            if arrivee not in prises:
                raise CoupInvalideError(depart, arrivee, "la prise est obligatoire")
            prise = prises[arrivee]
        elif arrivee not in piece.deplacements(depart, self):
            raise CoupInvalideError(depart, arrivee, "déplacement interdit")
        # 2. Modifier ensuite.
        del self._pieces[depart]
        piece_prise = self._pieces.pop(prise) if prise is not None else None
        self._pieces[arrivee] = piece.promouvoir(arrivee)
        return piece_prise

    # --- Étape 8
    def vers_dict(self) -> dict[str, str]:
        """L'inverse de depuis_dict : {"c3": "P", "f6": "d", ...}, dans l'ordre du plateau."""
        return {str(case): self[case].symbole for case in self}

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
        cases = set()
        for dc in (-1, 1):
            voisine = case.decaler(dc, self.sens)
            if voisine is not None and plateau[voisine] is None:
                cases.add(voisine)
        return cases

    def prises(self, case, plateau):
        """Sauter une pièce adverse voisine (avant ou arrière) vers la case libre derrière."""
        resultat = {}
        for dc, dl in DIAGONALES:
            milieu = case.decaler(dc, dl)
            arrivee = case.decaler(2 * dc, 2 * dl)
            if arrivee is not None and plateau[arrivee] is None \
                    and self.est_adverse(plateau[milieu]):
                resultat[arrivee] = milieu
        return resultat

    # --- Étape 6
    def promouvoir(self, case):
        """Sur la dernière ligne (10 pour les blancs, 1 pour les noirs), le pion devient dame."""
        derniere = TAILLE if self.couleur == "blanc" else 1
        return Dame(self.couleur) if case.ligne == derniere else self


# --- Étape 5 : la dame ---------------------------------------------------------------------------
class Dame(Piece):
    LETTRE = "D"
    NOM = "dame"
    FEMININ = True

    def deplacements(self, case, plateau):
        """Autant de cases libres qu'elle veut, dans les quatre diagonales."""
        cases = set()
        for dc, dl in DIAGONALES:
            suivante = case.decaler(dc, dl)
            while suivante is not None and plateau[suivante] is None:
                cases.add(suivante)
                suivante = suivante.decaler(dc, dl)
        return cases

    def prises(self, case, plateau):
        """Prise à distance : des cases libres, une pièce adverse, puis n'importe quelle case
        libre derrière elle (jusqu'au prochain obstacle ou au bord)."""
        resultat = {}
        for dc, dl in DIAGONALES:
            suivante = case.decaler(dc, dl)
            while suivante is not None and plateau[suivante] is None:   # cases libres
                suivante = suivante.decaler(dc, dl)
            if suivante is None or not self.est_adverse(plateau[suivante]):
                continue                                                 # bord ou pièce amie
            prise = suivante
            suivante = prise.decaler(dc, dl)
            while suivante is not None and plateau[suivante] is None:   # arrivées possibles
                resultat[suivante] = prise
                suivante = suivante.decaler(dc, dl)
        return resultat


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
        separateur = "x" if self.prise else "-"
        return f"{self.numero}. {self.depart}{separateur}{self.arrivee}"


class Partie:
    """Une partie A un plateau et un historique (composition) et sait à qui c'est le tour."""

    def __init__(self, plateau: "Plateau | None" = None):
        self.plateau = plateau if plateau is not None else Plateau.position_initiale()
        self.trait = "blanc"                  # la couleur qui doit jouer
        self.historique: list[Coup] = []

    def jouer(self, depart: str, arrivee: str) -> Coup:
        """Vérifie le trait, joue, note le coup, passe la main à l'adversaire."""
        piece = self.plateau[depart]
        if piece is not None and piece.couleur != self.trait:
            joueur = "blancs" if self.trait == "blanc" else "noirs"
            raise CoupInvalideError(depart, arrivee, f"c'est aux {joueur} de jouer")
        prise = self.plateau.deplacer(depart, arrivee)
        coup = Coup(len(self.historique) + 1, self.trait,
                    str(en_case(depart)), str(en_case(arrivee)), prise is not None)
        self.historique.append(coup)
        self.trait = adversaire(self.trait)
        return coup

    @property
    def gagnant(self) -> "str | None":
        """Celui qui a le trait et ne peut plus jouer a perdu : la couleur gagnante, ou None."""
        if self.plateau.coups_possibles(self.trait):
            return None
        return adversaire(self.trait)

    # --- Étape 8
    def sauvegarder(self, chemin) -> None:
        """Écrit la partie en JSON : {"trait": ..., "pieces": {"c3": "P", ...}}."""
        donnees = {"trait": self.trait, "pieces": self.plateau.vers_dict()}
        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump(donnees, fichier, ensure_ascii=False, indent=2)

    @classmethod
    def charger(cls, chemin) -> "Partie":
        """Constructeur alternatif : recrée une partie écrite par sauvegarder."""
        with open(chemin, encoding="utf-8") as fichier:
            donnees = json.load(fichier)
        partie = cls(Plateau.depuis_dict(donnees["pieces"]))
        partie.trait = donnees["trait"]
        return partie
