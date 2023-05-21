import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from pprint import pprint
from typing import NamedTuple, Set, Dict, Tuple, Iterable, List

from gurobipy import Model, GRB, tuplelist, quicksum


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


@dataclass
class Plane:
    name: str
    tasks: Iterable[str]

    def __post_init__(self):
        if invalid_tasks := [task for task in self.tasks
                             if task not in TASKS.keys()]:
            raise ValueError(f'Invalid tasks found: {invalid_tasks}')


@dataclass
class Worker:
    name: str
    qualifications: Set[QUALIFICATIONS]


class SchedulePlaneMaintenance():
    def __init__(self,
                 planes: Iterable[Plane],
                 workers: Iterable[Worker],
                 working_hours: int = 8):
        self.model = None
        self._planes = planes
        self._workers = workers
        self.WORKING_HOURS = working_hours

    def optimize(self) -> None:
        self.model.optimize()

    def build(self) -> None:
        self.model = Model('✈')

        task_status, worker_status, plane_status = self._set_variables()
        self.model.setObjective(plane_status.sum(), GRB.MAXIMIZE)
        self._set_contraints(task_status, worker_status, plane_status)

    def _set_variables(self):
        task_status = self.model.addVars(self.tasks,
                                         ub=1, vtype=GRB.BINARY, name='tasks')

        worker_tasks = self.model.addVars(self.worker_names, self.tasks,
                                          ub=1, vtype=GRB.BINARY, name='workers')

        plane_status = self.model.addVars((plane.name for plane in self._planes),
                                          ub=1, vtype=GRB.BINARY, name='planes')

        return task_status, worker_tasks, plane_status

    def _set_contraints(self, task_status, worker_status, plane_status):

        self.model.addConstrs((task_status[task] >= plane_status[plane]
                               for plane in plane_status
                               for task in self.tasks.select(plane, '*')),
                              'plane_tasks_completed')

        self.model.addConstrs((task_status[task] <= worker_status.sum("*", *task)
                               for task in task_status),
                              'task_picked_up')

        self.model.addConstrs((quicksum(worker_status[(worker, *task)]
                                        * TASKS[task[1]].time
                                        for task in self.tasks) <= self.WORKING_HOURS
                               for worker in self.worker_names),
                              'max_working_hours')

        # self.model.addConstrs((x[_x] <= 1
        #                        if tasks_q[_x[2]].issubset(workers_q[_x[0]])
        #                        else x[_x] <= 0
        #                        for _x in ),
        #                       'qualified_work_only')

    @cached_property
    def tasks(self):
        return tuplelist([
            (plane.name, task)
            for plane in self._planes
            for task in plane.tasks
        ])

    @cached_property
    def worker_names(self) -> List[str]:
        return [worker.name for worker in self._workers]

    def statuses(self, *args):
        for var_type in args:
            return [var for var in self.model.getVars()
                    if var.varName.startswith(var_type)]



if __name__ == '__main__':
    planes = [
        Plane('F16', ('wings', 'propellers')),
        Plane('JSF', ('propellers',)),
        Plane('MiG', ('tail', 'cockpit'))
    ]

    workers = [
        Worker('Arthur', set()),
        Worker('Roy', set()),
        Worker('Brown', set())
    ]
    scheduler = SchedulePlaneMaintenance(planes, workers)
    scheduler.build()
    scheduler.optimize()
    scheduler.statuses_to_dict('workers')
