"""Jouer aux dames à deux dans le terminal : chaque joueur tape son coup, comme c3 d4."""
from dames import Partie
from exceptions import ErreurDames

FICHIER = "partie.json"


def lire_coup(texte: str) -> tuple[str, str]:
    """« c3 d4 », « c3-d4 » ou « d4xf6 » donnent ("c3", "d4"). Sinon ValueError."""
    morceaux = texte.replace("-", " ").replace("x", " ").split()
    if len(morceaux) != 2:
        raise ValueError("tapez deux cases, par exemple c3 d4")
    return morceaux[0], morceaux[1]


def main() -> int:
    partie = Partie()
    print(partie.plateau)
    while partie.gagnant is None:
        texte = input(f"{partie.trait} > ").strip()
        if texte == "quitter":
            print("Partie abandonnée.")
            return 0
        # Bonus de l'étape 8 : sauver / reprendre
        if texte == "sauver":
            partie.sauvegarder(FICHIER)
            print(f"Partie sauvée dans {FICHIER}.")
            continue
        if texte == "reprendre":
            try:
                partie = Partie.charger(FICHIER)
            except OSError:
                print(f"Refusé : pas de fichier {FICHIER}")
                continue
            print(partie.plateau)
            continue
        try:
            coup = partie.jouer(*lire_coup(texte))
        except (ErreurDames, ValueError) as erreur:
            print(f"Refusé : {erreur}")
            continue
        print(coup)
        print(partie.plateau)
    gagnant = "blancs" if partie.gagnant == "blanc" else "noirs"
    print(f"Les {gagnant} gagnent !")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
