from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple, Set, Dict, Tuple, Iterable


class QUALIFICATIONS(Enum):
    FAA_01 = 1
    FAA_02 = 2
    FAA_03 = 3
    FAA_11 = 4
    FAA_12 = 5
    FAA_21 = 6
    FAA_22 = 7
    FAA_23 = 8
    FAA_24 = 9
    FAA_25 = 10


class Task(NamedTuple):
    qualifications: Set[QUALIFICATIONS]
    time: int


TASKS: Dict[str, Task] = {
    'fuselage': Task({QUALIFICATIONS[f'FAA_{q}'] for q in ['01', '02', '03']}, 3),
    'cockpit': Task({QUALIFICATIONS[f'FAA_{q}'] for q in ['01', '11', '21']}, 2),
    'wings': Task({QUALIFICATIONS[f'FAA_{q}'] for q in ['11', '12']}, 2),
    'tail': Task({QUALIFICATIONS[f'FAA_{q}'] for q in ['21', '22', '23', '24']}, 4),
    'engine': Task({QUALIFICATIONS[f'FAA_{q}'] for q in ['11', '21', '23']}, 5),
    'propeller': Task({QUALIFICATIONS[f'FAA_{q}'] for q in ['03', '11', '12']}, 1),
    'landing_gear': Task({QUALIFICATIONS[f'FAA_{q}'] for q in ['11', '12', '21', '25']}, 2),
}


@dataclass
class Plane:
    tasks: Tuple[str]

    def __post_init__(self):
        if invalid_tasks := [task for task in self.tasks if task not in TASKS.keys()]:
            raise ValueError(f'Invalid tasks found: {invalid_tasks}')


@dataclass
class Worker:
    qualifications: Set[QUALIFICATIONS]


class SchedulePlaneMaintenance():
    def __init__(self, planes: Iterable[Plane], workers: Iterable[Worker],
                 working_hours: int = 8):
        self.planes = planes
        self.workers = workers
        self.working_hours = working_hours

    def _set_up_variables(self):
