from string import ascii_uppercase, ascii_lowercase

from scheduler.model import SchedulePlaneMaintenance


def test_missing_skill():
    planes = {
        'F16': ('A', 'B', 'C', ),
        'JSF': ('D', 'E', 'F', ),
        'MiG': ('G', 'H', 'I', ),
        'Fokker': {'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R'},
    }

    workers = {
        'Arthur': {q for q in ascii_lowercase if q != 'a'},
        'Roy': {q for q in ascii_lowercase if q != 'a'},
        'Brown': {q for q in ascii_lowercase if q != 'a'},
    }

    tasks = {
        'A': ({'a', 'b', 'c'}, 2),
        'B': ({'a', 'b', 'c'}, 2),
        'C': ({'a', 'b', 'c'}, 2),
        'D': ({'a', 'b', 'c'}, 2),
        'E': ({'a', 'b', 'c'}, 2),
        'F': ({'a', 'b', 'c'}, 2),
        'G': ({'a', 'b', 'c'}, 2),
        'H': ({'a', 'b', 'c'}, 2),
        'I': ({'a', 'b', 'c'}, 2),
        'J': ({'a', 'b', 'c'}, 2),
        'K': ({'a', 'b', 'c'}, 2),
        'L': ({'a', 'b', 'c'}, 2),
        'M': ({'a', 'b', 'c'}, 2),
        'N': ({'a', 'b', 'c'}, 2),
        'O': ({'a', 'b', 'c'}, 2),
        'P': ({'a', 'b', 'c'}, 2),
        'Q': ({'a', 'b', 'c'}, 2),
        'R': ({'a', 'b', 'c'}, 2),
    }

    scheduler = SchedulePlaneMaintenance(planes,
                                         workers,
                                         tasks)
    _, deployable_planes = scheduler.optimize()
    assert len(deployable_planes) == 0

def test_complex_plane():
    planes = {
        'F16': ('A', 'B', 'C', ),
        'JSF': ('D', 'E', 'F', ),
        'MiG': ('G', 'H', 'I', ),
        'Fokker': {'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R'},
    }

    workers = {
        'Arthur': {q for q in ascii_lowercase},
        'Roy': {q for q in ascii_lowercase},
        'Brown': {q for q in ascii_lowercase},
    }

    tasks = {
        'A': ({'a', 'b', 'c'}, 2),
        'B': ({'a', 'b', 'c'}, 2),
        'C': ({'a', 'b', 'c'}, 2),
        'D': ({'a', 'b', 'c'}, 2),
        'E': ({'a', 'b', 'c'}, 2),
        'F': ({'a', 'b', 'c'}, 2),
        'G': ({'a', 'b', 'c'}, 2),
        'H': ({'a', 'b', 'c'}, 2),
        'I': ({'a', 'b', 'c'}, 2),
        'J': ({'a', 'b', 'c'}, 2),
        'K': ({'a', 'b', 'c'}, 2),
        'L': ({'a', 'b', 'c'}, 2),
        'M': ({'a', 'b', 'c'}, 2),
        'N': ({'a', 'b', 'c'}, 2),
        'O': ({'a', 'b', 'c'}, 2),
        'P': ({'a', 'b', 'c'}, 2),
        'Q': ({'a', 'b', 'c'}, 2),
        'R': ({'a', 'b', 'c'}, 2),
    }

    scheduler = SchedulePlaneMaintenance(planes,
                                         workers,
                                         tasks)
    worker_schedule, deployable_planes = scheduler.optimize()
    assert len(deployable_planes) == 3
    assert 'Fokker' not in deployable_planes
