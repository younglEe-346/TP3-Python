"""Outils partagés par les tests."""
import pytest

import dames


@pytest.fixture
def Dame():
    """La classe Dame, que vous écrivez vous-même à l'étape 5."""
    if not hasattr(dames, "Dame"):
        pytest.fail("la classe Dame n'existe pas encore : c'est l'étape 5")
    return dames.Dame


def noms(cases) -> set[str]:
    """Pour comparer facilement : {Case('d', 4), Case('b', 4)} devient {"d4", "b4"}."""
    return {str(case) for case in cases}
