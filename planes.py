from pprint import pprint

from scheduler.constants import QUALIFICATIONS
from scheduler.model import SchedulePlaneMaintenance

if __name__ == '__main__':
    planes = {
        'F16': ('wings', 'propellers',),
        'JSF': ('propellers',),
        'MiG': ('tail', 'cockpit',)
    }

    workers = {
        'Arthur': {q for q in QUALIFICATIONS},
        'Roy': {q for q in QUALIFICATIONS},
        'Brown': {q for q in QUALIFICATIONS},
    }

    scheduler = SchedulePlaneMaintenance(planes, workers)
    scheduler.build()
    scheduler.optimize()
    pprint(scheduler.worker_schedule())
    pprint(scheduler.completed_planes())