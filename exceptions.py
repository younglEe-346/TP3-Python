"""Les erreurs métier du jeu de dames."""


class ErreurDames(Exception):
    """Classe mère de toutes les erreurs du jeu."""


class CoupInvalideError(ErreurDames):
    """Un coup refusé : on garde la case de départ, la case d'arrivée et la raison."""

    def __init__(self, depart, arrivee, raison: str):
        self.depart = depart
        self.arrivee = arrivee
        self.raison = raison
        super().__init__(f"coup {depart}-{arrivee} refusé : {raison}")
