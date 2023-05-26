from pprint import pprint
from string import ascii_lowercase

from scheduler.model import SchedulePlaneMaintenance

if __name__ == '__main__':
    planes = {
        'F16': ('F16-wings', 'F16-propellers',),
        'JSF': ('JSF-propellers',),
        'MiG': ('MiG-tail', 'MiG-cockpit',)
    }

    workers = {
        'Arthur': {q for q in ascii_lowercase},
        'Roy': {q for q in ascii_lowercase},
        'Brown': {q for q in ascii_lowercase},
    }

    tasks = {
        'F16-wings': ({'a', 'b', 'c'}, 2),
        'F16-propellers': ({'a', 'b', 'c'}, 2),
        'JSF-propellers': ({'a', 'b', 'c'}, 2),
        'MiG-tail': ({'a', 'b', 'c'}, 2),
        'MiG-cockpit': ({'a', 'b', 'c'}, 2),
    }

    scheduler = SchedulePlaneMaintenance(planes, workers, tasks)
    worker_schedule, deployable_planes = scheduler.optimize()
    pprint(worker_schedule)
    pprint(deployable_planes)