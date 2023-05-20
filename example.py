from gurobipy import multidict, tuplelist, Model


names, lower, upper = multidict({'x': [0, 1], 'y': [1, 2], 'z': [0, 3] })

print(names)
print(lower)

# tuple list let you select
l = tuplelist([(1, 2), (1, 3), (2, 3), (2, 4)])
print(l.select('*',3)) # first is free, second should be three
print(l.select('*', [2, 4])) # first is free, second should be 2 or 4

# The problem is that the latter statement considers every member in the list,
# which can be quite inefficient for large lists.
# The select method builds internal data structures that make these selections quite efficient.

[(x,y) for x in range(4) for y in range(4) if x < y]


# Note that the for statements are executed left-to-right,
# and values from one can be used in the next, so a more efficient way to write the above is:
[(x, y) for x in range(4) for y in range(x + 1, 4)]

l = list([(1, 2), (1, 3), (2, 3), (2, 4)])
m = Model("assignment")
d = m.addVars(l, name="d")
m.update()

print(sum(d.select(1, '*')))
print(d.sum(1,'*'))


print(d[1,3])
d[3, 4] = 0.3

print(d[3, 4])