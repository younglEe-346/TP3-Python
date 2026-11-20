"""Étape 8 (à la maison) : sauvegarder et recharger une partie."""
import json

from dames import Partie, Plateau


def test_vers_dict():
    plateau = Plateau.depuis_dict({"e5": "p", "a1": "P"})
    assert plateau.vers_dict() == {"a1": "P", "e5": "p"}
    assert list(plateau.vers_dict()) == ["a1", "e5"]


def test_aller_retour():
    depart = Plateau.position_initiale()
    assert Plateau.depuis_dict(depart.vers_dict()).vers_dict() == depart.vers_dict()


def test_sauvegarder(tmp_path):
    partie = Partie()
    partie.jouer("d4", "e5")
    partie.sauvegarder(tmp_path / "partie.json")
    donnees = json.loads((tmp_path / "partie.json").read_text(encoding="utf-8"))
    assert donnees["trait"] == "noir"
    assert donnees["pieces"]["e5"] == "P" and "d4" not in donnees["pieces"]
    assert len(donnees["pieces"]) == 40


def test_charger(tmp_path):
    partie = Partie()
    partie.jouer("d4", "e5")
    partie.sauvegarder(tmp_path / "partie.json")
    reprise = Partie.charger(tmp_path / "partie.json")
    assert isinstance(reprise, Partie)
    assert reprise.trait == "noir"
    assert reprise.plateau.vers_dict() == partie.plateau.vers_dict()
    reprise.jouer("e7", "d6")             # la partie continue normalement


def test_les_dames_survivent(tmp_path, Dame):
    partie = Partie(Plateau.depuis_dict({"c9": "P", "h4": "p"}))
    partie.jouer("c9", "d10")
    partie.sauvegarder(tmp_path / "partie.json")
    reprise = Partie.charger(tmp_path / "partie.json")
    assert isinstance(reprise.plateau["d10"], Dame)
    assert reprise.trait == "noir"
