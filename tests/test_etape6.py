"""Étape 6 : jouer un coup."""
import pytest

from dames import Case, Pion, Plateau
from exceptions import CoupInvalideError, ErreurDames


def test_erreur_coup_invalide():
    err = CoupInvalideError("c3", "d4", "déplacement interdit")
    assert (err.depart, err.arrivee, err.raison) == ("c3", "d4", "déplacement interdit")
    assert str(err) == "coup c3-d4 refusé : déplacement interdit"
    assert isinstance(err, ErreurDames)


def test_coups_possibles_au_depart():
    coups = Plateau.position_initiale().coups_possibles("blanc")
    assert [f"{depart}-{arrivee}" for depart, arrivee in coups] == \
        ["b4-a5", "b4-c5", "d4-c5", "d4-e5", "f4-e5", "f4-g5", "h4-g5", "h4-i5", "j4-i5"]
    assert len(Plateau.position_initiale().coups_possibles("noir")) == 9


def test_prises_possibles():
    plateau = Plateau.depuis_dict({"c3": "P", "d4": "p", "g3": "P"})
    assert plateau.prises_possibles("blanc") == {Case("c", 3): {Case("e", 5): Case("d", 4)}}
    assert plateau.prises_possibles("noir") == {Case("d", 4): {Case("b", 2): Case("c", 3)}}


def test_la_prise_est_obligatoire_dans_les_coups():
    plateau = Plateau.depuis_dict({"c3": "P", "d4": "p", "g3": "P"})
    assert plateau.coups_possibles("blanc") == [(Case("c", 3), Case("e", 5))]


def test_deplacer_simple():
    plateau = Plateau.position_initiale()
    assert plateau.deplacer("d4", "e5") is None
    assert plateau["d4"] is None
    assert isinstance(plateau["e5"], Pion) and plateau["e5"].couleur == "blanc"
    assert len(plateau) == 40


def test_deplacer_avec_prise():
    plateau = Plateau.depuis_dict({"c3": "P", "d4": "p"})
    prise = plateau.deplacer("c3", "e5")
    assert isinstance(prise, Pion) and prise.couleur == "noir"
    assert "d4" not in plateau and "c3" not in plateau
    assert plateau["e5"].couleur == "blanc"
    assert len(plateau) == 1


def test_case_de_depart_vide():
    with pytest.raises(CoupInvalideError, match="aucune pièce"):
        Plateau.position_initiale().deplacer("e5", "f6")


def test_deplacement_interdit_ne_change_rien():
    plateau = Plateau.position_initiale()
    with pytest.raises(CoupInvalideError, match="déplacement interdit"):
        plateau.deplacer("d4", "d5")
    assert plateau["d4"] is not None and plateau["d5"] is None and len(plateau) == 40


def test_prise_obligatoire_ne_change_rien():
    plateau = Plateau.depuis_dict({"c3": "P", "d4": "p", "g3": "P"})
    with pytest.raises(CoupInvalideError, match="la prise est obligatoire"):
        plateau.deplacer("g3", "h4")
    assert "g3" in plateau and "h4" not in plateau and len(plateau) == 3


def test_promouvoir(Dame):
    pion = Pion("blanc")
    assert isinstance(pion.promouvoir(Case("d", 10)), Dame)
    assert pion.promouvoir(Case("d", 8)) is pion
    assert isinstance(Pion("noir").promouvoir(Case("g", 1)), Dame)
    assert Pion("noir").promouvoir(Case("d", 10)).__class__ is Pion


def test_promotion_en_jouant(Dame):
    plateau = Plateau.depuis_dict({"c9": "P", "f2": "p", "c7": "P"})
    plateau.deplacer("c9", "d10")
    plateau.deplacer("f2", "g1")
    plateau.deplacer("c7", "d8")
    assert isinstance(plateau["d10"], Dame) and plateau["d10"].couleur == "blanc"
    assert isinstance(plateau["g1"], Dame) and plateau["g1"].couleur == "noir"
    assert isinstance(plateau["d8"], Pion)


def test_prise_par_une_dame(Dame):
    plateau = Plateau.depuis_dict({"a1": "D", "d4": "p"})
    prise = plateau.deplacer("a1", "g7")
    assert isinstance(prise, Pion)
    assert len(plateau) == 1 and isinstance(plateau["g7"], Dame)
