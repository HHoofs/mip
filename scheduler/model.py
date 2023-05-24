import re
from collections import defaultdict
from functools import cached_property
from typing import Set, Dict, Iterable, List, Tuple

from gurobipy import Model, GRB, tuplelist, quicksum, tupledict  # type: ignore

from scheduler.constants import TASKS, QUALIFICATIONS


class SchedulePlaneMaintenance:
    """
    Class that schedules the maintenance of planes
    given a set of (required) tasks for each plane.
    These tasks are picked up by a set of workers
    given their qualifications and time required
    for each task.

    The scheduler has two stages.The model is build
    after which it can be optimized to retrieve
    the optimal solution.

    The schedule is optimized to maxime the number
    of planes without any remaining task.

    :param planes: Planes with their associated tasks to be performed
    :param workers: Workers with their associated qualifications
    :param working_hours: Maximum time that workers can spend on their tasks

    Example
    -------
    In this example a single plane with a single
    task is maintained by one of two workers.
    One worker has all qualifications and
    can therefore perform each possible task
    whilst the other is unqualified for all tasks.
    The former will therefore perform the single
    vacant task for the plane to be maintained.

    >>> scheduler = SchedulePlaneMaintenance(
    ...                 planes={'F16': ['wings']},
    ...                 workers={'Pat': set(QUALIFICATIONS),
    ...                          'Mat': {}})
    >>> scheduler.build()
    >>> scheduler.optimize()
    >>> scheduler.completed_planes()
    {'F16'}
    >>> scheduler.worker_schedule()
    {'Pat': {'F16': ['wings']}}

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

        # Retrieve assigned task (val == 1)
        # and split into worker, plane, task
        assigned_tasks = \
            [re_task.group(1).split(',')
             for task in self.worker_status.select()
             if task.X and (re_task := self.RE_BRACKETS.search(task.varName))]
        for task in assigned_tasks:
            schedule[task[0]][task[1]].append(task[2])

        # convert to simple dict for (pretty) printing
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
        return {re_plane.group(1)
                for plane
                in self.plane_status.select()
                if plane.X and (re_plane := self.RE_BRACKETS.search(plane.varName))}

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
        Apply the mathematical constraints to mip model
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
