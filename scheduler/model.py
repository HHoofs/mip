from functools import cached_property
from typing import Set, Dict, Iterable

from gurobipy import Model, GRB, tuplelist, quicksum  # type: ignore

from scheduler.constants import TASKS, QUALIFICATIONS


class SchedulePlaneMaintenance:
    """
    S

    :param planes:
    :param workers:
    :param working_hours:
    """
    def __init__(self,
                 planes: Dict[str, Iterable[str]],
                 workers: Dict[str, Set[QUALIFICATIONS]],
                 working_hours: int = 8):
        self.model: Model = Model('✈')
        self._planes = planes
        self._workers = workers
        self.WORKING_HOURS = working_hours
        self._check_plane_tasks(self.tasks)
        self.task_status, self.worker_status, self.plane_status = \
            None, None, None

    def build(self) -> None:
        self._set_variables()
        self.model.setObjective(self.plane_status.sum(), GRB.MAXIMIZE)  # type: ignore
        self._set_constraints()

    def optimize(self) -> None:
        self.model.optimize()

    @cached_property
    def tasks(self) -> tuplelist:
        return tuplelist([
            (plane_name, task)
            for plane_name, tasks in self._planes.items()
            for task in tasks
        ])

    def _set_variables(self) -> None:
        self.task_status = \
            self.model.addVars(self.tasks,
                               ub=1, vtype=GRB.BINARY, name='tasks')

        self.worker_status = \
            self.model.addVars(self._workers.keys(), self.tasks,
                               ub=1, vtype=GRB.BINARY, name='workers')

        self.plane_status = \
            self.model.addVars(self._planes.keys(),
                               ub=1, vtype=GRB.BINARY, name='planes')

    def _set_constraints(self) -> None:
        self.model.addConstrs(
            (self.task_status[task] >= self.plane_status[plane]
             for plane in self.plane_status
             for task in self.tasks.select(plane, '*')),
            name='plane_tasks_completed')

        self.model.addConstrs(
            (self.task_status[task] <= self.worker_status.sum("*", *task)
             for task in self.task_status),
            name='task_picked_up')

        self.model.addConstrs(
            (quicksum(self.worker_status[(worker, *task)]
                      * TASKS[task[1]].time
                      for task in self.tasks) <= self.WORKING_HOURS
             for worker in self._workers.keys()),
            name='max_working_hours')

        self.model.addConstrs(
            (self.worker_status[worker_task] <= 1
             if TASKS[worker_task[2]].qualifications.issubset(
                self._workers[worker_task[0]])
             else self.worker_status[worker_task] <= 0
             for worker_task in self.worker_status),
            name='qualified_work_only')

    @staticmethod
    def _check_plane_tasks(tasks: tuplelist) -> None:
        if invalid_tasks := [task for task in tasks
                             if task[1] not in TASKS.keys()]:
            raise ValueError(f'Invalid tasks found: {invalid_tasks}')
