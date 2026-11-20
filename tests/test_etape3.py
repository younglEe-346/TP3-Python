"""Étape 3 : le plateau."""
import pytest

from dames import Case, Pion, Plateau


def test_plateau_vide():
    plateau = Plateau()
    assert len(plateau) == 0
    assert plateau["c3"] is None
    assert "c3" not in plateau


def test_placer_et_lire():
    plateau = Plateau()
    pion = Pion("blanc")
    plateau.placer("c3", pion)
    assert plateau["c3"] is pion
    assert plateau[Case("c", 3)] is pion
    assert "c3" in plateau and Case("c", 3) in plateau
    assert "d4" not in plateau
    assert len(plateau) == 1


def test_case_blanche_refusee():
    with pytest.raises(ValueError, match="case blanche"):
        Plateau().placer("b1", Pion("blanc"))


def test_case_occupee_refusee():
    plateau = Plateau()
    plateau.placer("c3", Pion("blanc"))
    with pytest.raises(ValueError, match="déjà occupée"):
        plateau.placer("c3", Pion("noir"))
    assert plateau["c3"].couleur == "blanc"


def test_nom_invalide():
    with pytest.raises(ValueError):
        Plateau()["z9"]


def test_depuis_dict():
    plateau = Plateau.depuis_dict({"c3": "P", "f6": "p"})
    assert len(plateau) == 2
    assert plateau["f6"].couleur == "noir"


def test_iteration_dans_l_ordre():
    plateau = Plateau.depuis_dict({"c3": "P", "b2": "p", "a1": "P"})
    assert [str(case) for case in plateau] == ["a1", "b2", "c3"]


def test_position_initiale():
    plateau = Plateau.position_initiale()
    assert len(plateau) == 40
    assert plateau.compter("blanc") == 20 and plateau.compter("noir") == 20
    assert isinstance(plateau["a1"], Pion) and plateau["a1"].couleur == "blanc"
    assert isinstance(plateau["j10"], Pion) and plateau["j10"].couleur == "noir"
    assert all(plateau[case].couleur == "blanc" for case in plateau if case.ligne <= 4)
    assert all(plateau[case].couleur == "noir" for case in plateau if case.ligne >= 7)
    assert not any(5 <= case.ligne <= 6 for case in plateau)


def test_affichage():
    lignes = str(Plateau.position_initiale()).splitlines()
    assert lignes[0] == "10    p   p   p   p   p"
    assert lignes[6] == " 4    P   P   P   P   P"
    assert lignes[-1] == "    a b c d e f g h i j"
    assert repr(Plateau.position_initiale()) == "<Plateau : 20 blancs, 20 noirs>"
