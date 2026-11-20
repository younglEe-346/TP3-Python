"""Étape 8, bonus : mes propres tests."""
import main
from dames import Partie, Plateau


def test_sauver_puis_reprendre_dans_main(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    saisies = iter(["d4 e5", "sauver", "reprendre", "e7 d6", "quitter"])
    monkeypatch.setattr("builtins.input", lambda invite="": next(saisies))
    assert main.main() == 0
    sortie = capsys.readouterr().out
    assert "Partie sauvée dans partie.json." in sortie
    assert "1. e7-d6" in sortie          # après reprise, la partie repart avec le trait aux noirs
    assert (tmp_path / "partie.json").exists()


def test_exemple_de_l_enonce():
    partie = Partie()
    coups = [str(partie.jouer(d, a)) for d, a in [("d4", "c5"), ("e7", "d6"), ("c5", "e7")]]
    assert coups == ["1. d4-c5", "2. e7-d6", "3. c5xe7"]
    assert partie.plateau.compter("noir") == 19


def test_une_dame_peut_reculer():
    plateau = Plateau.depuis_dict({"e5": "D"})
    assert plateau.deplacer("e5", "a1") is None
    assert plateau.vers_dict() == {"a1": "D"}
