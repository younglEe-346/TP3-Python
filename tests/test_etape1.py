"""Étape 1 : la case."""
from dataclasses import FrozenInstanceError

import pytest

from dames import Case


def test_creation():
    case = Case("c", 3)
    assert (case.colonne, case.ligne) == ("c", 3)


@pytest.mark.parametrize("colonne", ["k", "z", "", "ab", "C"])
def test_colonne_invalide(colonne):
    with pytest.raises(ValueError, match="colonne invalide"):
        Case(colonne, 3)


@pytest.mark.parametrize("ligne", [0, 11, -1])
def test_ligne_invalide(ligne):
    with pytest.raises(ValueError, match="ligne invalide"):
        Case("c", ligne)


def test_immuable():
    case = Case("c", 3)
    with pytest.raises(FrozenInstanceError):
        case.ligne = 4


def test_egalite_et_hachage():
    assert Case("c", 3) == Case("c", 3)
    assert Case("c", 3) != Case("c", 4)
    assert len({Case("c", 3), Case("c", 3), Case("d", 4)}) == 2
    assert {Case("c", 3): "pion"}[Case("c", 3)] == "pion"


def test_depuis_nom():
    assert Case.depuis_nom("c3") == Case("c", 3)
    assert Case.depuis_nom("j10") == Case("j", 10)


@pytest.mark.parametrize("nom", ["", "c", "z3", "c0", "c11", "3c", "cc"])
def test_depuis_nom_invalide(nom):
    with pytest.raises(ValueError, match="nom de case invalide"):
        Case.depuis_nom(nom)


def test_est_noire():
    assert Case("a", 1).est_noire
    assert Case("c", 3).est_noire
    assert Case("j", 10).est_noire
    assert not Case("b", 1).est_noire
    assert not Case("a", 2).est_noire


def test_decaler():
    assert Case("c", 3).decaler(1, 1) == Case("d", 4)
    assert Case("c", 3).decaler(-2, -2) == Case("a", 1)
    assert Case("c", 3).decaler(0, 0) == Case("c", 3)


def test_decaler_hors_du_plateau():
    assert Case("a", 1).decaler(-1, 1) is None
    assert Case("j", 10).decaler(0, 1) is None
    assert Case("b", 2).decaler(-2, -2) is None


def test_affichage():
    assert str(Case("c", 3)) == "c3"
    assert str(Case("j", 10)) == "j10"
    assert repr(Case("c", 3)) == "Case(colonne='c', ligne=3)"
