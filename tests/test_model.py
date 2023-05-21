from scheduler.constants import QUALIFICATIONS, TASKS
from scheduler.model import SchedulePlaneMaintenance


def test_missing_skill():
    planes = {
        'F16': ('engine', 'cockpit', 'wings', ),
        'JSF': ('engine', 'cockpit', 'wings', ),
        'MiG': ('engine', 'cockpit', 'wings', ),
    }

    workers = {
        'Arthur': {q for q in QUALIFICATIONS if q.name != 'FAA_11'},
        'Roy': {q for q in QUALIFICATIONS if q.name != 'FAA_11'},
        'Brown': {q for q in QUALIFICATIONS if q.name != 'FAA_11'},
    }

    scheduler = SchedulePlaneMaintenance(planes, workers, working_hours=12)
    scheduler.build()
    scheduler.optimize()
    assert scheduler.plane_status.sum().getValue() == 0


def test_complex_plane():
    planes = {
        'F16': ('engine', 'cockpit', 'wings', ),
        'JSF': ('engine', 'cockpit', 'wings', ),
        'MiG': ('engine', 'cockpit', 'wings', ),
        'Fokker': TASKS.keys(),
    }

    workers = {
        'Arthur': {q for q in QUALIFICATIONS},
        'Roy': {q for q in QUALIFICATIONS},
        'Brown': {q for q in QUALIFICATIONS},
    }

    scheduler = SchedulePlaneMaintenance(planes, workers, working_hours=12)
    scheduler.build()
    scheduler.optimize()
    assert scheduler.plane_status.sum().getValue() == 3
    assert scheduler.plane_status['Fokker'].X == 0