from enum import Enum
from typing import NamedTuple, Set, Dict


class QUALIFICATIONS(Enum):
    """
    All valid qualifications for
    a worker or a task
    """
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
    """
    A task should include a required set of qualifications
    and a time duration to complete the task
    """
    qualifications: Set[QUALIFICATIONS]
    time: int


# Mapping of each task and its properties
TASKS: Dict[str, Task] = {
    'fuselage': Task({QUALIFICATIONS[f'FAA_{q}']
                      for q in ['01', '02', '03']}, 3),
    'cockpit': Task({QUALIFICATIONS[f'FAA_{q}']
                     for q in ['01', '11', '21']}, 2),
    'wings': Task({QUALIFICATIONS[f'FAA_{q}']
                   for q in ['11', '12']}, 2),
    'tail': Task({QUALIFICATIONS[f'FAA_{q}']
                  for q in ['21', '22', '23', '24']}, 4),
    'engine': Task({QUALIFICATIONS[f'FAA_{q}']
                    for q in ['11', '21', '23']}, 5),
    'propellers': Task({QUALIFICATIONS[f'FAA_{q}']
                        for q in ['03', '11', '12']}, 1),
    'landing_gear': Task({QUALIFICATIONS[f'FAA_{q}']
                          for q in ['11', '12', '21', '25']}, 2),
}
