from functools import cached_property
from typing import Set, Dict, Iterable

from gurobipy import Model, GRB, tuplelist, quicksum

from main import QUALIFICATIONS
from scheduler.constants import TASKS


class SchedulePlaneMaintenance():
    def __init__(self,
                 planes: Dict[str, Iterable[str]],
                 workers: Dict[str, Set[QUALIFICATIONS]],
                 working_hours: int = 8):
        self.model = None
        self._planes = planes
        self._workers = workers
        self.WORKING_HOURS = working_hours
        self._check_plane_tasks()

    def build(self) -> None:
        self.model = Model('✈')

        task_status, worker_status, plane_status = self._set_variables()
        self.model.setObjective(plane_status.sum(), GRB.MAXIMIZE)
        self._set_constraints(task_status, worker_status, plane_status)

    def optimize(self) -> None:
        self.model.optimize()

    @cached_property
    def tasks(self):
        return tuplelist([
            (plane_name, task)
            for plane_name, tasks in self._planes.items()
            for task in tasks
        ])

    def statuses(self, *args):
        for var_type in args:
            yield [var for var in self.model.getVars()
                   if var.varName.startswith(var_type)]

    def _set_variables(self):
        task_status = self.model.addVars(self.tasks,
                                         ub=1, vtype=GRB.BINARY, name='tasks')

        worker_tasks = self.model.addVars(self._workers.keys(), self.tasks,
                                          ub=1, vtype=GRB.BINARY, name='workers')

        plane_status = self.model.addVars(self._planes.keys(),
                                          ub=1, vtype=GRB.BINARY, name='planes')

        return task_status, worker_tasks, plane_status

    def _set_constraints(self, task_status, worker_status, plane_status):
        self.model.addConstrs(
            (task_status[task] >= plane_status[plane]
             for plane in plane_status
             for task in self.tasks.select(plane, '*')),
            name='plane_tasks_completed')

        self.model.addConstrs(
            (task_status[task] <= worker_status.sum("*", *task)
             for task in task_status),
            name='task_picked_up')

        self.model.addConstrs(
            (quicksum(worker_status[(worker, *task)]
                      * TASKS[task[1]].time
                      for task in self.tasks) <= self.WORKING_HOURS
             for worker in self._workers.keys()),
            name='max_working_hours')

        self.model.addConstrs(
            (worker_status[worker_task] <= 1
             if TASKS[worker_task[2]].qualifications.issubset(
                self.workers[worker_task[0]])
             else worker_status[worker_task] <= 0
             for worker_task in worker_status),
            name='qualified_work_only')

    def _check_plane_tasks(self):
        if invalid_tasks := [task for task in self.tasks
                             if task[1] not in TASKS.keys()]:
            raise ValueError(f'Invalid tasks found: {invalid_tasks}')