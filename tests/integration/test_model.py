"""
Test suite to control the working of the maintenance scheduler
"""

import random
from itertools import chain
from string import ascii_lowercase

from tails.model import SchedulePlaneMaintenance


def test_missing_skill():
    """
    Tests that a missing skill (`a`) for all workers
    will result that neither of the planes will be
    maintenance ready
    """
    planes = {
        "F16": (
            "A",
            "B",
            "C",
        ),
        "JSF": (
            "D",
            "E",
            "F",
        ),
        "MiG": (
            "G",
            "H",
            "I",
        ),
        "Fokker": {"J", "K", "L", "M", "N", "O", "P", "Q", "R"},
    }

    workers = {
        "Arthur": {q for q in ascii_lowercase if q != "a"},
        "Roy": {q for q in ascii_lowercase if q != "a"},
        "Brown": {q for q in ascii_lowercase if q != "a"},
    }

    tasks = {
        "A": ({"a", "b", "c"}, 2),
        "B": ({"a", "b", "c"}, 2),
        "C": ({"a", "b", "c"}, 2),
        "D": ({"a", "b", "c"}, 2),
        "E": ({"a", "b", "c"}, 2),
        "F": ({"a", "b", "c"}, 2),
        "G": ({"a", "b", "c"}, 2),
        "H": ({"a", "b", "c"}, 2),
        "I": ({"a", "b", "c"}, 2),
        "J": ({"a", "b", "c"}, 2),
        "K": ({"a", "b", "c"}, 2),
        "L": ({"a", "b", "c"}, 2),
        "M": ({"a", "b", "c"}, 2),
        "N": ({"a", "b", "c"}, 2),
        "O": ({"a", "b", "c"}, 2),
        "P": ({"a", "b", "c"}, 2),
        "Q": ({"a", "b", "c"}, 2),
        "R": ({"a", "b", "c"}, 2),
    }

    scheduler = SchedulePlaneMaintenance(planes, workers, tasks)
    _, deployable_planes = scheduler.optimize()
    assert len(deployable_planes) == 0


def test_complex_plane():
    """
    Tests that the most complex planes will be left alone,
    and the more simple planes will be served first
    """
    planes = {
        "F16": (
            "A",
            "B",
            "C",
        ),
        "JSF": (
            "D",
            "E",
            "F",
        ),
        "MiG": (
            "G",
            "H",
            "I",
        ),
        "Fokker": {"J", "K", "L", "M", "N", "O", "P", "Q", "R"},
    }

    workers = {
        "Arthur": {q for q in ascii_lowercase},
        "Roy": {q for q in ascii_lowercase},
        "Brown": {q for q in ascii_lowercase},
    }

    tasks = {
        "A": ({"a", "b", "c"}, 2),
        "B": ({"a", "b", "c"}, 2),
        "C": ({"a", "b", "c"}, 2),
        "D": ({"a", "b", "c"}, 2),
        "E": ({"a", "b", "c"}, 2),
        "F": ({"a", "b", "c"}, 2),
        "G": ({"a", "b", "c"}, 2),
        "H": ({"a", "b", "c"}, 2),
        "I": ({"a", "b", "c"}, 2),
        "J": ({"a", "b", "c"}, 2),
        "K": ({"a", "b", "c"}, 2),
        "L": ({"a", "b", "c"}, 2),
        "M": ({"a", "b", "c"}, 2),
        "N": ({"a", "b", "c"}, 2),
        "O": ({"a", "b", "c"}, 2),
        "P": ({"a", "b", "c"}, 2),
        "Q": ({"a", "b", "c"}, 2),
        "R": ({"a", "b", "c"}, 2),
    }

    scheduler = SchedulePlaneMaintenance(planes, workers, tasks)
    _, deployable_planes = scheduler.optimize()
    assert len(deployable_planes) == 3
    assert "Fokker" not in deployable_planes


def test_2day_task():
    """
    Tests that a 2 day task is not (yet) possible
    """
    planes = {
        "F16": (
            "A",
            "B",
        ),
        "JSF": (
            "C",
            "D",
        ),
        "MiG": ("E",),
    }

    workers = {
        "Arthur": {q for q in ascii_lowercase},
        "Roy": {q for q in ascii_lowercase},
        "Brown": {q for q in ascii_lowercase},
    }

    tasks = {
        "A": ({"a", "b", "c"}, 2),
        "B": ({"a", "b", "c"}, 2),
        "C": ({"a", "b", "c"}, 2),
        "D": ({"a", "b", "c"}, 2),
        "E": ({"a", "b", "c"}, 16),
    }

    scheduler = SchedulePlaneMaintenance(planes, workers, tasks)
    _, deployable_planes = scheduler.optimize()
    assert len(deployable_planes) == 2


def test_large_test_set():
    """
    Test that optimizer works if there are enough skilled workers (10)
    for ten planes with various takss
    """
    _random = random.Random(5)

    planes = {
        "".join(_random.choices(ascii_lowercase, k=10)).title(): tuple(
            (
                "".join(_random.choices(ascii_lowercase, k=3)).upper()
                for i in range(_random.randint(2, 6))
            )
        )
        for _ in range(10)
    }

    workers = {
        "".join(_random.choices(ascii_lowercase, k=5)).title(): {
            t for t in ascii_lowercase if _random.random() > 0.2
        }
        for _ in range(10)
    }

    tasks = {
        task: (
            {t for t in ascii_lowercase if _random.random() > 0.9},
            _random.randint(0, 8),
        )
        for task in chain.from_iterable(planes.values())
    }

    scheduler = SchedulePlaneMaintenance(planes, workers, tasks)
    _, deployable_planes = scheduler.optimize()
    assert len(deployable_planes) == 7
