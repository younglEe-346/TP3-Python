"""Jouer aux dames à deux dans le terminal : chaque joueur tape son coup, comme c3 d4."""
from dames import Partie
from exceptions import ErreurDames


def lire_coup(texte: str) -> tuple[str, str]:
    """« c3 d4 », « c3-d4 » ou « d4xf6 » donnent ("c3", "d4"). Sinon ValueError."""
    raise NotImplementedError("à compléter")


def main() -> int:
    raise NotImplementedError("à compléter")


if __name__ == "__main__":
    raise SystemExit(main())
