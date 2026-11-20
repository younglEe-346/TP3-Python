"""Étape 7 : la partie et le programme principal."""
from dataclasses import FrozenInstanceError

import pytest

import main
from dames import Coup, Partie, Plateau
from exceptions import CoupInvalideError


def test_coup_affichage():
    assert str(Coup(1, "blanc", "c3", "d4")) == "1. c3-d4"
    assert str(Coup(4, "noir", "d4", "f6", True)) == "4. d4xf6"


def test_coup_gele():
    with pytest.raises(FrozenInstanceError):
        Coup(1, "blanc", "c3", "d4").numero = 2


def test_jouer():
    partie = Partie()
    coup = partie.jouer("d4", "e5")
    assert coup == Coup(1, "blanc", "d4", "e5", False)
    assert partie.trait == "noir"
    assert partie.historique == [coup]


def test_chacun_son_tour():
    partie = Partie()
    with pytest.raises(CoupInvalideError, match="c'est aux blancs de jouer"):
        partie.jouer("g7", "f6")
    assert partie.trait == "blanc" and partie.historique == [] and partie.plateau["g7"] is not None


def test_une_erreur_ne_change_rien():
    partie = Partie()
    partie.jouer("d4", "c5")
    with pytest.raises(CoupInvalideError):
        partie.jouer("g7", "g6")
    assert partie.trait == "noir" and len(partie.historique) == 1


def test_partie_avec_prise():
    partie = Partie()
    partie.jouer("d4", "c5")
    partie.jouer("e7", "d6")
    coup = partie.jouer("c5", "e7")
    assert coup.prise and str(coup) == "3. c5xe7"
    assert partie.plateau.compter("noir") == 19


def test_partie_sur_un_plateau_donne():
    vide = Plateau()
    assert Partie(vide).plateau is vide


def test_gagnant():
    assert Partie().gagnant is None
    assert Partie(Plateau.depuis_dict({"a1": "p"})).gagnant == "noir"
    assert Partie(Plateau.depuis_dict({"a1": "P", "b2": "p", "c3": "p"})).gagnant == "noir"


@pytest.mark.parametrize("texte", ["c3 d4", "c3-d4", "c3xd4", "  c3   d4 "])
def test_lire_coup(texte):
    assert main.lire_coup(texte) == ("c3", "d4")


@pytest.mark.parametrize("texte", ["", "c3", "c3 d4 e5"])
def test_lire_coup_invalide(texte):
    with pytest.raises(ValueError, match="tapez deux cases"):
        main.lire_coup(texte)


def simuler(monkeypatch, saisies):
    reponses = iter(saisies)
    monkeypatch.setattr("builtins.input", lambda invite="": next(reponses))


def test_main_refuse_puis_abandonne(monkeypatch, capsys):
    simuler(monkeypatch, ["d4 e5", "d4 e5", "bonjour", "quitter"])
    assert main.main() == 0
    sortie = capsys.readouterr().out
    assert "1. d4-e5" in sortie
    assert "Refusé : coup d4-e5 refusé : aucune pièce sur la case de départ" in sortie
    assert "Refusé : tapez deux cases" in sortie
    assert sortie.rstrip().endswith("Partie abandonnée.")


def test_main_jusqu_a_la_victoire(monkeypatch, capsys):
    monkeypatch.setattr(main, "Partie", lambda: Partie(Plateau.depuis_dict({"c3": "P", "d4": "p"})))
    simuler(monkeypatch, ["c3 e5"])
    assert main.main() == 0
    assert capsys.readouterr().out.rstrip().endswith("Les blancs gagnent !")
