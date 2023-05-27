from typing import Set, Dict, Iterable, Tuple, Mapping

from gurobipy import Model, GRB, quicksum  # type: ignore


class SchedulePlaneMaintenance:
    """
    Class that schedules the maintenance of planes given a set of (required)
    tasks for each plane. These tasks are picked up by a set of workers given
    their qualifications and time required for each task.

    To retrieve the most optimal schedule the model can be optimized.
    The schedule is optimized to maximize the number of planes without any
    remaining task. The output of this model are the deployable planes
    and work schedule following this optimized schedule.

    :param planes: Planes with their associated tasks to be performed
    :param workers: Workers with their associated qualifications
    :param tasks: Task speciation’s, including the required
        qualifications and time for each task to be completed

    Note
    ----
    The qualifications from the tasks and the workers should originate from
    the same set of strings. An incorrect qualification can result in
    unresolved tasks and therefore undeployable planes. The same goes for
    the name of the tasks for each plane and the task names within the
    tasks specifications.

    Example
    -------
    In this example a single plane with a single task is maintained by one of
    two workers. One worker has the required qualifications and can therefore
    perform the task at hand whilst the other is unqualified for this task.
    The former will therefore perform the single vacant task for the plane to
    be maintained.

    >>> scheduler = SchedulePlaneMaintenance(
    ...                 planes={'F16': ['wings']},
    ...                 workers={'Pat': {'a'},
    ...                          'Mat': {'b'}},
    ...                 tasks={'wings': ({'a'}, 1)})
    >>> scheduler.optimize()
    ({'Pat': {'wings'}, 'Mat': set()}, {'F16'})

    """
    # Fixed number of working hours
    WORKING_HOURS = 8

    def __init__(self,
                 planes: Mapping[str, Iterable[str]],
                 workers: Mapping[str, Set[str]],
                 tasks: Mapping[str, Tuple[Set[str], int]]):
        self.model: Model = Model('🛦')
        self._planes = planes
        self._workers = workers
        self._tasks = tasks
        self._build_model()

    def _build_model(self) -> None:
        """
        Build mip model, with the following steps:
            1. Create variables
            2. Set constraints
            3. Set objective (as many deployable planes as possible)
        """
        # y
        task_status = \
            self.model.addVars(self._tasks.keys(),
                               ub=1, vtype=GRB.BINARY, name='tasks')

        # x
        worker_status = \
            self.model.addVars(self._workers.keys(), self._tasks.keys(),
                               ub=1, vtype=GRB.BINARY, name='workers')

        # z
        plane_status = \
            self.model.addVars(self._planes.keys(),
                               ub=1, vtype=GRB.BINARY, name='planes')

        # First constraint
        self.model.addConstrs(
            (plane_status[plane] <= task_status[task]
             for plane in plane_status
             for task in self._planes[plane]),
            name='plane_tasks_completed')

        # Second constraint
        self.model.addConstrs(
            (task_status[task] <= worker_status.sum("*", task)
             for task in task_status),
            name='task_picked_up')

        # Third constraint
        self.model.addConstrs(
            (quicksum(worker_status[(worker, task)]
                      * self._tasks[task][1]  # retrieve time of task
                      for task in task_status) <= self.WORKING_HOURS
             for worker, _ in worker_status),
            name='max_working_hours')

        # Fourth constraint
        self.model.addConstrs(
            (worker_status[(worker, task)] <= 1
             if self._tasks[task][0].issubset(  # retrieve task qualifications
                self._workers[worker])  # compare with worker qualifications
             else worker_status[(worker, task)] <= 0
             for worker, task in worker_status),
            name='qualified_work_only')

        # Set objective to maximize number of planes with all tasks completed
        self.model.setObjective(plane_status.sum(), GRB.MAXIMIZE)

    def optimize(self) -> Tuple[Dict[str, Set[str]], Set[str]]:
        """
        Optimize model and retrieve optimal schedule for each worker

        :return: Tasks for each worker to perform (empty set if no tasks are
            assigned to this worker) and names of the deployable planes if
            these tasks are carried out
        """
        self.model.optimize()

        worker_schedule = \
            {worker:
                {task for task in self._tasks.keys()
                 # check if tasks is assigned to this worker ( == 1)
                 if self.model.getVarByName(f'workers[{worker},{task}]').X}
             for worker in self._workers.keys()}

        deployable_planes = \
            {plane for plane in self._planes.keys()
             if self.model.getVarByName(f'planes[{plane}]').X}

        return worker_schedule, deployable_planes
