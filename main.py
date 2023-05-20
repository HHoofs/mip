from gurobipy import GRB, Model, tuplelist, max_, multidict

# Base data
PLANES = ['F-16', 'JSF', 'MiG']  # V
WORKERS = ['Arthur', 'Roy', 'Brown']   # M
TASKS = ['wings', 'propellers', 'tail']  # T
QUALIFICATIONS = ['screwdriver', 'hammer', 'welding']  # Q

tasks = tuplelist([
    ('F-16', 'wings'), ('F-16', 'propellers'),
    ('JSF', 'tail'),
    ('MiG', 'wings'), ('MiG', 'tail'),
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
m.addConstrs((x.sum(worker, '*', '*') * 1 <= 8 for worker in WORKERS), 'worker_max_hours')
m.addConstrs(
    (x[_x] <= 1
     if workers_q[_x[0]].issubset(tasks_q[_x[2]])
     else x[_x] <= 0
     for _x in x),
    'qualified_work_only'
)

m.optimize()