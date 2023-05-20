from gurobipy import GRB, Model, tuplelist, max_, multidict
from pprint import pprint

# Base data
PLANES = ['F-16', 'JSF', 'MiG']  # V
WORKERS = ['Arthur', 'Roy', 'Brown']   # M
TASKS = ['wings', 'propellers', 'tail']  # T
QUALIFICATIONS = ['screwdriver', 'hammer', 'welding']  # Q

tasks = tuplelist([
    ('F-16a', 'wings'), ('F-16a', 'propellers'),
    ('F-16b', 'wings'), ('F-16b', 'propellers'),
    ('F-16c', 'wings'), ('F-16c', 'propellers'),
    ('F-16d', 'wings'), ('F-16d', 'propellers'),
    ('F-16e', 'wings'), ('F-16e', 'propellers'),
    ('F-16f', 'wings'),
    ('JSF', 'propellers'),
    ('MiGa', 'wings'), ('MiGa', 'propellers'),  ('MiGa', 'tail'),
    ('MiGb', 'wings'), ('MiGb', 'propellers'),  ('MiGb', 'tail'),
    ('MiGc', 'tail'),
])

workers_q = {
    'Arthur': {'screwdriver', 'hammer'},
    'Roy': {'hammer', 'welding'},
    'Brown': {'screwdriver', 'hammer', 'welding'},
}

tasks_q = {
    'wings': {'screwdriver', 'hammer'},
    'propellers': {'hammer', 'welding'},
    'tail': {'welding', 'screwdriver'},
}

planes = {plane for plane, task in tasks}


m = Model('netflow')

y = m.addVars(tasks, ub=1, vtype=GRB.BINARY, name="y")
x = m.addVars([worker for worker in WORKERS], tasks, ub=1, vtype=GRB.BINARY, name='x')
z = m.addVars(planes, ub=1, vtype=GRB.BINARY, name='z')

m.setObjective(z.sum(), GRB.MAXIMIZE)

m.addConstrs((y[task] >= z[plane] for plane in planes for task in tasks.select(plane,'*')), 'plane_tasks_completed')
m.addConstrs((y[task] <= x.sum("*", *task) for task in tasks), 'task_picked_up')
m.addConstrs((x.sum(worker, '*', '*') * 4 <= 8 for worker in WORKERS), 'worker_max_hours')
m.addConstrs(
    (x[_x] <= 1
     if tasks_q[_x[2]].issubset(workers_q[_x[0]])
     else x[_x] <= 0
     for _x in x),
    'qualified_work_only'
)

m.optimize()


print('Worker Picked Up Task')
pprint(x)
print()
print('Picked Up Task')
pprint(y)
print()
pprint('Completed Airplanes')
pprint(z)