"""Étape 2 : les pièces."""
import pytest

from dames import Piece, Pion


class Reine(Piece):
    """Une pièce inventée pour les tests, au nom féminin."""
    LETTRE = "R"
    NOM = "reine"
    FEMININ = True

    def deplacements(self, case, plateau):
        return set()

    def prises(self, case, plateau):
        return {}


def test_couleur():
    assert Pion("blanc").couleur == "blanc"
    assert Pion("noir").couleur == "noir"


@pytest.mark.parametrize("couleur", ["vert", "Blanc", ""])
def test_couleur_invalide(couleur):
    with pytest.raises(ValueError, match="couleur invalide"):
        Pion(couleur)


def test_couleur_en_lecture_seule():
    pion = Pion("blanc")
    with pytest.raises(AttributeError):
        pion.couleur = "noir"


def test_sens():
    assert Pion("blanc").sens == 1
    assert Pion("noir").sens == -1


def test_symbole():
    assert Pion("blanc").symbole == "P"
    assert Pion("noir").symbole == "p"
    assert Reine("noir").symbole == "r"


def test_est_adverse():
    blanc = Pion("blanc")
    assert blanc.est_adverse(Pion("noir"))
    assert not blanc.est_adverse(Pion("blanc"))
    assert not blanc.est_adverse(None)


def test_affichage():
    assert str(Pion("blanc")) == "pion blanc"
    assert str(Pion("noir")) == "pion noir"
    assert repr(Pion("noir")) == "Pion('noir')"


def test_accord_au_feminin():
    assert str(Reine("blanc")) == "reine blanche"
    assert str(Reine("noir")) == "reine noire"
    assert repr(Reine("blanc")) == "Reine('blanc')"


def test_piece_abstraite():
    with pytest.raises(TypeError):
        Piece("blanc")
