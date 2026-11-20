"""Étape 5 : la dame, une classe que vous écrivez entièrement.

La fixture Dame (dans conftest.py) fournit votre classe, ou fait échouer le test si elle n'existe pas encore.
"""
from conftest import noms
from dames import Case, Piece, Pion, Plateau


def deplacements(plateau, nom):
    return noms(plateau[nom].deplacements(Case.depuis_nom(nom), plateau))


def prises(plateau, nom):
    return {str(arrivee): str(prise)
            for arrivee, prise in plateau[nom].prises(Case.depuis_nom(nom), plateau).items()}


def test_une_dame_est_une_piece(Dame):
    assert issubclass(Dame, Piece)
    assert not issubclass(Dame, Pion)


def test_affichage(Dame):
    assert str(Dame("blanc")) == "dame blanche"
    assert str(Dame("noir")) == "dame noire"
    assert repr(Dame("noir")) == "Dame('noir')"
    assert Dame("blanc").symbole == "D" and Dame("noir").symbole == "d"


def test_depuis_dict_cree_des_dames(Dame):
    plateau = Plateau.depuis_dict({"e5": "d", "c3": "D"})
    assert isinstance(plateau["e5"], Dame) and plateau["e5"].couleur == "noir"
    assert isinstance(plateau["c3"], Dame) and plateau["c3"].couleur == "blanc"


def test_deplacements_plateau_vide(Dame):
    assert len(deplacements(Plateau.depuis_dict({"e5": "D"}), "e5")) == 17
    assert len(deplacements(Plateau.depuis_dict({"a1": "D"}), "a1")) == 9


def test_deplacements_bloques(Dame):
    plateau = Plateau.depuis_dict({"e5": "D", "g7": "p", "c3": "P"})
    assert deplacements(plateau, "e5") == {"f6", "d6", "c7", "b8", "a9", "f4", "g3", "h2", "i1", "d4"}


def test_prise_a_distance(Dame):
    plateau = Plateau.depuis_dict({"a1": "D", "d4": "p"})
    assert prises(plateau, "a1") == {"e5": "d4", "f6": "d4", "g7": "d4", "h8": "d4", "i9": "d4", "j10": "d4"}


def test_prise_arretee_par_un_obstacle(Dame):
    plateau = Plateau.depuis_dict({"a1": "D", "d4": "p", "g7": "P"})
    assert prises(plateau, "a1") == {"e5": "d4", "f6": "d4"}


def test_pas_deux_pieces_d_affilee(Dame):
    assert prises(Plateau.depuis_dict({"a1": "D", "d4": "p", "e5": "p"}), "a1") == {}


def test_pas_de_prise_de_sa_couleur(Dame):
    assert prises(Plateau.depuis_dict({"a1": "D", "d4": "P"}), "a1") == {}


def test_prises_dans_plusieurs_directions(Dame):
    plateau = Plateau.depuis_dict({"e5": "D", "g7": "p", "b2": "p", "c7": "P"})
    assert prises(plateau, "e5") == {"h8": "g7", "i9": "g7", "j10": "g7", "a1": "b2"}


def test_polymorphisme(Dame):
    plateau = Plateau.depuis_dict({"c3": "P", "e5": "D"})
    nombres = {str(case): len(plateau[case].deplacements(case, plateau)) for case in plateau}
    assert nombres == {"c3": 2, "e5": 14}
