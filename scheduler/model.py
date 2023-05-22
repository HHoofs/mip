import re
from collections import defaultdict
from functools import cached_property
from typing import Set, Dict, Iterable, List, Tuple

from gurobipy import Model, GRB, tuplelist, quicksum, tupledict  # type: ignore

from scheduler.constants import TASKS, QUALIFICATIONS


class SchedulePlaneMaintenance:
    """
    :param planes:
    :param workers:
    :param working_hours:
    """
    RE_BRACKETS = re.compile(r'\[(.*?)\]')

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
            self._create_variables()

    def build(self) -> None:
        """
        Build mip model, using following steps:
            1. Set objective of model (as many planes completed as possible)
            2. Set constraints of model
        """
        self.model.setObjective(self.plane_status.sum(), GRB.MAXIMIZE)
        self._set_constraints()

    def optimize(self) -> None:
        """
        Optimize mip model
        """
        self.model.optimize()

    @cached_property
    def tasks(self) -> tuplelist:
        """
        Retrieve isolated tasks based on hierarchical tasks for each plane

        :return: tasks to perform
        """
        return tuplelist([
            (plane_name, task)
            for plane_name, tasks in self._planes.items()
            for task in tasks
        ])

    def worker_schedule(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Retrieve schedule for all workers following the solution
        of the model

        :return: Tasks (per plane) for each worker to perform
        """
        self.check_if_model_is_optimal()

        schedule = defaultdict(lambda: defaultdict(list))  # type: ignore

        assigned_tasks = \
            [self.RE_BRACKETS.search(task.varName).group(1).split(',')
             for task in self.worker_status.select()
             if task.X]
        for task in assigned_tasks:
            schedule[task[0]][task[1]].append(task[2])

        return {worker: dict(tasks)
                for worker, tasks
                in schedule.items()}

    def completed_planes(self) -> Set[str]:
        """
        Retrieve all planes that are completed following
        the solution of the model

        :return: Planes completed after scheduled work is performed
        """
        self.check_if_model_is_optimal()
        return {self.RE_BRACKETS.search(plane.varName).group(1)
                for plane
                in self.plane_status.select()
                if plane.X}

    def _create_variables(self) -> Tuple[tupledict, tupledict, tupledict]:
        """
        Create all variables of the mip model
        """
        # y
        task_status = \
            self.model.addVars(self.tasks,
                               ub=1, vtype=GRB.BINARY, name='tasks')

        # x
        worker_status = \
            self.model.addVars(self._workers.keys(), self.tasks,
                               ub=1, vtype=GRB.BINARY, name='workers')

        # z
        plane_status = \
            self.model.addVars(self._planes.keys(),
                               ub=1, vtype=GRB.BINARY, name='planes')

        return task_status, worker_status, plane_status

    def _set_constraints(self) -> None:
        """
        Apply all mathematical constraints to mip model
        """
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
             else self.worker_status[worker_task] == 0
             for worker_task in self.worker_status),
            name='qualified_work_only')

    @staticmethod
    def _check_plane_tasks(tasks: tuplelist) -> None:
        """
        Checks if all tasks assigned to each plane can be found
        in the tasks mapping which include the necessary qualifications
        and time needed for each task

        :param tasks: all tasks to perform on the planes
        """
        if invalid_tasks := [task for task in tasks
                             if task[1] not in TASKS.keys()]:
            raise ValueError(f'Invalid tasks found: {invalid_tasks}')

    def check_if_model_is_optimal(self) -> None:
        """
        Checks if model status is optimal.

        :raises: ValueError if current status of model is not optimal
        """
        if self.model.status != GRB.OPTIMAL:
            raise ValueError(f'Model has a status that is not optimal '
                             f'(current status: {self.model.status})')
