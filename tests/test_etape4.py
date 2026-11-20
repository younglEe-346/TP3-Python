"""Étape 4 : le pion."""
from conftest import noms
from dames import Case, Plateau


def deplacements(plateau, nom):
    return noms(plateau[nom].deplacements(Case.depuis_nom(nom), plateau))


def prises(plateau, nom):
    return {str(arrivee): str(prise)
            for arrivee, prise in plateau[nom].prises(Case.depuis_nom(nom), plateau).items()}


def test_pion_blanc_monte():
    assert deplacements(Plateau.depuis_dict({"c3": "P"}), "c3") == {"b4", "d4"}


def test_pion_noir_descend():
    assert deplacements(Plateau.depuis_dict({"f6": "p"}), "f6") == {"e5", "g5"}


def test_bord_du_plateau():
    assert deplacements(Plateau.depuis_dict({"a3": "P"}), "a3") == {"b4"}
    assert deplacements(Plateau.depuis_dict({"c9": "P"}), "c9") == {"b10", "d10"}


def test_cases_occupees():
    plateau = Plateau.depuis_dict({"c3": "P", "b4": "P", "d4": "p"})
    assert deplacements(plateau, "c3") == set()


def test_prise_en_avant():
    assert prises(Plateau.depuis_dict({"c3": "P", "d4": "p"}), "c3") == {"e5": "d4"}


def test_prise_en_arriere():
    assert prises(Plateau.depuis_dict({"e5": "P", "d4": "p"}), "e5") == {"c3": "d4"}


def test_deux_prises_possibles():
    plateau = Plateau.depuis_dict({"e5": "p", "d4": "P", "f4": "P"})
    assert prises(plateau, "e5") == {"c3": "d4", "g3": "f4"}


def test_case_derriere_occupee():
    assert prises(Plateau.depuis_dict({"c3": "P", "d4": "p", "e5": "p"}), "c3") == {}


def test_pas_de_prise_de_sa_couleur():
    assert prises(Plateau.depuis_dict({"c3": "P", "d4": "P"}), "c3") == {}


def test_pas_de_prise_hors_du_plateau():
    assert prises(Plateau.depuis_dict({"b2": "P", "a3": "p"}), "b2") == {}


def test_neuf_coups_au_depart():
    plateau = Plateau.position_initiale()
    total = sum(len(plateau[case].deplacements(case, plateau)) for case in plateau
                if plateau[case].couleur == "blanc")
    assert total == 9
