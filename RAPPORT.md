# TP3: Checkers with objects (le jeu de dames)

A plain-English guide to the lab. It covers what each part does, why it is built that way, and answers to every "Pour réfléchir" question.

---

## 1. The big idea

You build the game of checkers (10 x 10 board) using **classes**.
At the end, two people can play in the terminal:

```
python main.py
blanc > d4 c5
1. d4-c5
noir > e7 d6
...
```

The real goal is not checkers. The goal is to practise **object-oriented programming (OOP)**:

| OOP idea | Where you see it in this lab |
|---|---|
| Frozen dataclass (an unchangeable value) | `Case`, `Coup` |
| Abstract class (a "contract") | `Piece` |
| Inheritance ("is a") | `Pion` is a `Piece`, `Dame` is a `Piece` |
| Polymorphism (same call, different behaviour) | `piece.deplacements(...)` works for both pawn and queen |
| Composition ("has a") | `Plateau` **has** pieces, `Partie` **has** a board |
| Special methods (`__getitem__`, `__len__`...) | `Plateau` behaves like a container |
| Custom exceptions | `CoupInvalideError` |
| Alternative constructors (`@classmethod`) | `Case.depuis_nom`, `Plateau.position_initiale`, `Partie.charger` |

---

## 2. How to run it

```powershell
cd tp3_dames
.venv\Scripts\activate          # turn on the virtual environment
pytest                          # run all the tests  -> 102 passed
python main.py                  # play a game
python -i dames.py              # open a console to try things by hand
```

In the game, type moves like `c3 d4`, `c3-d4` or `c3xe5`.
Extra commands: `sauver` (save to `partie.json`), `reprendre` (load it), `quitter` (quit).

---

## 3. Map of the classes

```
Exception
 └── ErreurDames                 (all game errors)
      └── CoupInvalideError      (a refused move: depart, arrivee, raison)

Case            frozen dataclass: one square, e.g. c3
Coup            frozen dataclass: one move played, e.g. "3. c5xe7"

Piece (ABC)     abstract: has a colour, must define deplacements() and prises()
 ├── Pion       moves 1 square forward diagonally, captures by jumping
 └── Dame       slides any distance diagonally, captures from far away

Plateau         HAS a private dict {Case: Piece}. Enforces the rules of one move.
Partie          HAS a Plateau + a list of Coup. Knows whose turn it is.
```

**Key design choice:** a piece does **not** know where it is.
Only the board knows. So piece methods get the square and the board as arguments:
`pion.deplacements(case, plateau)`.
This means the piece and the board can never disagree about where the piece is.

---

## 4. Step by step: what I wrote and why

### Step 1: `Case` (a square)

`@dataclass(frozen=True)` makes Python write `__init__`, `__repr__`, `__eq__` and `__hash__` for you.

- `__post_init__`: runs right after `__init__`. It checks the column is one letter in `a..j` and the row is between 1 and 10. Otherwise it raises `ValueError`.
  - Trap: `"" in "abcdefghij"` is `True`, so I also check `len(colonne) == 1`.
- `depuis_nom("c3")`: a second way to build a square, from text. `nom[0]` is the column and `int(nom[1:])` is the row. Any failure becomes `ValueError("nom de case invalide : ...")`. `from None` hides the messy original error.
- `est_noire`: column index + row is odd, so the square is dark. Example: a1 is 0 + 1 = 1, so it is dark.
- `decaler(dc, dl)`: the square shifted by `dc` columns and `dl` rows, or `None` if that is off the board. It checks the limits **before** building the `Case`, because building an invalid `Case` would raise an error.
- `__str__`: `"c3"`.

### Step 2: `Piece` (abstract parent)

- `__init__` checks the colour and stores it in `self._couleur`. The `_` means "private, don't touch".
- `couleur` is a `@property` with **no setter**, so it is read-only. `pion.couleur = "blanc"` raises `AttributeError`.
- `sens`: +1 for white (moves up), -1 for black (moves down).
- `symbole`: `self.LETTRE` in upper case for white and lower case for black. Each subclass sets `LETTRE` (`"P"` or `"D"`).
- `est_adverse(autre)`: true if `autre` is a piece of the other colour.
- `__repr__` uses `type(self).__name__`, so it prints `Pion('noir')` or `Dame('noir')` automatically.
- `__str__` gives "pion blanc", "dame blanche" or "dame noire". It uses `FEMININ` to add the feminine ending.

### Step 3: `Plateau` (the board, a container)

The board stores pieces in a **private dict** `self._pieces = {Case: Piece}`.

- `placer(case, piece)` refuses a light square or an occupied square.
- `plateau["c3"]` calls `__getitem__` and returns the piece or `None`.
- `"c3" in plateau` calls `__contains__`.
- `len(plateau)` calls `__len__`.
- All of them accept `"c3"` or `Case("c", 3)` because they go through `en_case()`.
- `position_initiale()` places white pawns on the dark squares of rows 1-4 and black pawns on rows 7-10, which makes 40 pieces.

### Step 4: `Pion` (pawn)

- `deplacements`: the 2 squares diagonally **forward** (`self.sens`) that exist and are empty.
- `prises`: in all 4 diagonals (forward **and** backward), if the neighbour is an enemy and the square behind it is empty, the pawn can capture. It returns a dict `{landing square: captured square}`.

### Step 5: `Dame` (queen). I wrote the whole class.

```python
class Dame(Piece):
    LETTRE = "D"; NOM = "dame"; FEMININ = True
```

- `deplacements`: in each diagonal, keep stepping while the square is empty. Each empty square is a valid move, like a bishop in chess.
- `prises`:
  1. Step over empty squares.
  2. If you hit an **enemy** piece, every empty square right behind it (until the next obstacle or the edge) is a valid landing square.
  3. If you hit a friendly piece or two pieces in a row, there is no capture in that direction.

If `Dame` forgot to define `deplacements` or `prises`, `Dame("blanc")` would fail with `TypeError: Can't instantiate abstract class`. That is the "contract" of the abstract class.

### Step 6: playing a move

- `CoupInvalideError(depart, arrivee, raison)` stores the 3 values and calls `super().__init__("coup c3-d4 refusé : ...")` so the message prints nicely.
- `prises_possibles(couleur)` returns `{start: {landing: captured}}` for every piece that can capture.
- `coups_possibles(couleur)` lists all legal moves. **If any capture exists, only captures are allowed** (the forced-capture rule). The list is sorted.
- `Pion.promouvoir(case)` turns the pawn into a `Dame` when it reaches the last row.
- `deplacer(depart, arrivee)` follows the rule **"check first, then change"**:
  1. Check that there is a piece on the start square.
  2. Check the forced capture. If the player can capture, this move must be a capture.
  3. Otherwise, check that the move is allowed.
  4. Only then change the board: remove the piece from the start, remove the captured piece, and place `piece.promouvoir(arrivee)` on the landing square.

### Step 7: `Coup`, `Partie`, `main.py`

- `Coup.__str__`: `"1. c3-d4"` for a normal move, `"4. d4xf6"` for a capture.
- `Partie.jouer`:
  1. Check that it is your turn.
  2. Ask the board to move.
  3. Record the `Coup`.
  4. Give the turn to the other player.
- `Partie.gagnant`: if the player to move has **no legal move**, the other player wins. Otherwise it returns `None`.
- `main.py`:
  - `lire_coup` turns `"c3-d4"` into `("c3", "d4")`.
  - `main()` is the game loop: show the board, ask for a move, print `Refusé : ...` on an error, and announce the winner at the end.

### Step 8: saving (homework)

- `vers_dict()` is the opposite of `depuis_dict`: `{"a1": "P", "c1": "P", ...}`.
- `sauvegarder(chemin)` writes `{"trait": ..., "pieces": ...}` as JSON.
- `charger(chemin)` (a `@classmethod`) reads the JSON and rebuilds a `Partie`.
- Bonus: `sauver` and `reprendre` commands in `main.py`, plus 3 tests of my own in `tests/test_mes_tests.py`.

---

## 5. Answers to the "Pour réfléchir" questions

### Step 0
**a)** Dataclasses: `Case` and `Coup`. Inheritance: `Pion(Piece)`, `Dame(Piece)`, `Piece(ABC)`, `ErreurDames(Exception)`, `CoupInvalideError(ErreurDames)`.
**b)** `@abstractmethod` marks `deplacements` and `prises`. Every kind of piece must write both.

### Step 1
**a)** `__eq__` (says the two squares are equal) and `__hash__` (gives them the same hash). A set uses both to spot duplicates. **`@dataclass` wrote them**, not me.
**b)** A dict finds a key by its hash. If a key could change after insertion, its hash would change and the dict would lose it. With `eq=True` but not frozen, the dataclass even sets `__hash__ = None`, so the object cannot be a key at all. `frozen=True` makes it safe to hash.
**c)** `depuis_nom` **creates** the object, so no `self` exists yet. It receives the class (`cls`) and calls `cls(...)`. Bonus: with `cls`, a subclass would get an object of the subclass.

### Step 2
**a)** Python looks for `LETTRE` on the object, then on its class `Pion`, where it finds `"P"`. It stops there. `Piece.LETTRE` would always give `"?"`, the parent's value, so every piece would print `?`.
**b)** `__str__` only reads `self.NOM` and `self.FEMININ`. These are looked up on the **real class of the object** when the code runs. So any new subclass (like `Reine`) works, as long as it sets those attributes.

### Step 3
**a)** If `Plateau` inherited from `dict`, every dict method would be public and would skip the rules. For example, `plateau[Case("b", 1)] = pion` (`__setitem__`) would put a piece on a light square. `update()`, `pop()` and `clear()` would also break the rules. With composition, the dict is private and the only way in is `placer`, which checks the rules.
**b)** `for case in self` calls `__iter__`. `self[case]` calls `__getitem__`.

### Step 4
**a)** In the parent class `Piece`. Python looks in `Pion` first, does not find them, then looks in `Piece` (the MRO: `Pion -> Piece -> ABC -> object`).
**b)** A normal move only needs the landing square, so a set is enough. A capture also needs to know **which piece is captured**, so it is a dict `{landing: captured}`. This matters for the queen, which can land far from the piece it takes.

### Step 5
**a)** **Polymorphism / dynamic dispatch.** When the code runs, Python looks up `deplacements` in the class of the actual object. A `Pion` object uses `Pion.deplacements` and a `Dame` object uses `Dame.deplacements`. No `isinstance` is needed.
**b)** No. Apply the "is a" test: a queen is **not** a pawn. She does not move only forward, and she must not inherit the pawn's `promouvoir` (a queen does not become a queen again). Both are pieces, so both inherit from `Piece`.

### Step 6
**a)** Doing all the checks before any change makes the move **all or nothing**. If we removed the piece first and a check then failed, the error would leave the board broken: the piece would be gone for good, and the game would be corrupted.
**b)** A queen uses the default `Piece.promouvoir`, which returns `self`, so a queen stays the same queen. Each class answers the question in its own way, so `deplacer` does not need `isinstance`.

### Step 7
**a)** Because we wrote `__len__`, `bool(Plateau())` is `False` for an empty board. `plateau or Plateau.position_initiale()` would silently swap a deliberately empty board for a full one. `is not None` only checks whether a board was given at all.
**b)** A computed property is **always correct**, because it reads the board as it is right now. A stored attribute would have to be updated after every move, and someone could forget. One source of truth is better than two copies that could disagree.

### Step 8
**a)** `charger` builds a **new** `Partie` from a file. When it is called, no `Partie` object exists yet, so it needs the class (`cls`), not an instance (`self`). Using `cls(...)` also works for subclasses.
**b)** Save the history too: `"historique": [dataclasses.asdict(c) for c in self.historique]`. `asdict` turns each `Coup` into a plain dict. When loading, rebuild each move with `Coup(**d)`.

### Défi: the "rafle" (multi-capture)
The rule belongs to **`Plateau`** (and `Partie` for the input). Only the board sees the whole position. `Pion.prises` and `Dame.prises` can stay as they are, because they already answer "what single capture can I do from here?"

Proposed design:
1. Add `Plateau.rafles(case)`. It explores capture after capture with recursion. It works on a **copy** of the board where the moving piece has left its start square, and where the pieces already jumped stay as **blocking obstacles**. They are removed only at the end and cannot be jumped twice.
2. `deplacer` takes a whole path (`c3 x e5 x g7`). It checks that the path is one of the `rafles`, then removes all the captured pieces at once.
3. `Partie.jouer` and `lire_coup` accept more than 2 squares.

---

## 6. Proof that it works

```
pytest            -> 102 passed (99 official + 3 of mine)
```

Every console example in the PDF gives exactly the expected output. One example is the opening sequence `d4-c5, e7-d6, c5xe7`, followed by the refusal "la prise est obligatoire".

Git history:
```
TP3 : étapes 1 à 8 (...)
Kit de départ du TP3
```

---

## 7. Remember for the exam (cheat sheet)

- **dataclass(frozen=True)**: an unchangeable value object, which is hashable and can be a dict key.
- **`__post_init__`**: where you validate a dataclass.
- **`@classmethod` + `cls`**: an alternative constructor (`depuis_nom`, `position_initiale`, `charger`).
- **`@property` without a setter**: a read-only attribute.
- **ABC + `@abstractmethod`**: a contract. Subclasses must implement the methods or they cannot be created.
- **Inheritance = "is a"** (`Dame` is a `Piece`). **Composition = "has a"** (`Plateau` has pieces).
- **Polymorphism**: the same call does the right thing for each class, with no `isinstance`.
- **Special methods**: `[]` calls `__getitem__`, `in` calls `__contains__`, `len()` calls `__len__`, `for` calls `__iter__`.
- **Check first, then change**: never leave an object half-modified after an error.
- **Custom exceptions**: inherit from a parent error class, call `super().__init__(message)`.
