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
    planes_statuses = scheduler.statuses('planes')
    pprint(*planes_statuses)