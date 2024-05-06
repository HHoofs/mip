from __future__ import annotations

from typing import Iterable, Literal, Protocol, Union, overload


Expresionable = Union[int, 'Var', 'LinearExpresion', 'QuadraticExpresion']
Expresion = Union['LinearExpresion', 'QuadraticExpresion']


class IndexedVariable(Protocol):
    def __iter__(self) -> Iterable[Var]:
        ...

    def values(self) -> Iterable[Var]:
        ...

    def sum(self, *args) -> Var: ...


class Var(Protocol):
    """
    Gurobi variable object.  Variables have a number of attributes.
    Some can be set (e.g., v.ub = 0.0), while others can only be queried
    (e.g., print(v.x)). The most commonly used variable attributes are:
        obj: Linear objective coefficient.
        lb: Lower bound.
        ub: Upper bound.
        varName: Variable name.
        vType: Variable type ('C', 'B', 'I', 'S', or 'N').
        x: Solution value.
        rc: Solution reduced cost.
        xn: Solution value in an alternate MIP solution.

    Type "help(GRB.attr)" for a list of all available attributes.

    Note that attribute modifications are handled in a lazy fashion.  You
    won't see the effect of a change until after the next call to Model.update()
    or Model.optimize().
    """
    obj: float
    lb: float
    ub: float
    varname: str
    vtype: Literal['B', 'C', 'I', 'N', 'S']
    x: float
    rc: float
    xn: float

    def __add__(self, x: Union[int, Var], /) -> LinearExpresion: ...

    def __radd__(self, x: Union[int, Var], /) -> LinearExpresion: ...

    def __iadd__(self, x: Union[int, Var], /) -> LinearExpresion: ...

    def __sub__(self, x: Union[int, Var], /) -> LinearExpresion: ...

    def __rsub__(self, x: Union[int, Var], /) -> LinearExpresion: ...

    def __isub__(self, x: Union[int, Var], /) -> LinearExpresion: ...

    def __neg__(self, x: Union[int, Var], /) -> LinearExpresion: ...

    @overload
    def __mul__(self, x: int, /) -> LinearExpresion: ...
    @overload
    def __mul__(self, x: Var, /) -> QuadraticExpresion: ...
    def __mul__(self, x: Union[int, Var], /) -> Expresion: ...

    @overload
    def __imul__(self, x: int, /) -> LinearExpresion: ...
    @overload
    def __imul__(self, x: Var, /) -> QuadraticExpresion: ...
    def __imul__(self, x: Union[int, Var], /) -> Expresion: ...  # type: ignore

    def __rmul__(self, x: int, /) -> LinearExpresion: ...

    def __div__(self, x: int, /) -> LinearExpresion: ...

    def __pow__(self, x: Literal[2], /) -> LinearExpresion: ... 

    # see mypy [issue](https://github.com/python/mypy/issues/2783)
    # for reason over ignore
    @overload   # type: ignore[override]  
    def __eq__(self, x: Union[Var, LinearExpresion], /) -> LinearConstraint: ... 
    @overload  # type: ignore[override]
    def __eq__(self, x: QuadraticExpresion, /) -> QuadraticExpresion: ... 
    def __eq__(self, x: Union[Var, Expresion], /) -> Constraint: ...  # type: ignore[override]

    @overload   # type: ignore[override]  
    def __le__(self, x: Union[Var, LinearExpresion], /) -> LinearConstraint: ... 
    @overload  # type: ignore[override]
    def __le__(self, x: QuadraticExpresion, /) -> QuadraticExpresion: ...  # type: ignore[misc]
    def __le__(self, x: Union[Var, Expresion], /) -> Constraint: ...  # type: ignore[override, misc]

    @overload   # type: ignore[override]  
    def __ge__(self, x: Union[Var, LinearExpresion], /) -> LinearConstraint: ... 
    @overload  # type: ignore[override]
    def __ge__(self, x: QuadraticExpresion, /) -> QuadraticExpresion: ...  # type: ignore[misc]
    def __ge__(self, x: Union[Var, Expresion], /) -> Constraint: ...  # type: ignore[override, misc]


class LinearExpresion(Protocol):
    def clear(self) -> None:
        """
        Set a linear expression to zero
        """
        ...

    def copy(self) -> LinearExpresion:
        """
        Copy a linear expression
        """
        ...

    def remove(self, which: int | Var) -> None:
        """
        Remove a term from the expression.

        Args:
            which: Term to remove.  Can be an int, in which case the term at
                index 'which' is removed, or a Var, in which case all terms that
                involve the Var 'which' are removed.
        """
        ...

    def size(self) -> int:
        """
        Return the number of terms in a linear expression.
        """
        ...

    @overload
    def getCoeff(self, i:  slice) -> list[float]: ...
    @overload
    def getCoeff(self, i: int) -> float: ...
    def getCoeff(self, i: int | slice) -> float | list[float]:
        """
        Return the coefficient for the term at index 'i'.

        Args:
            i: Index of term whose coefficient is requested
        """
        ...

    def getConstant(self) -> float:
        """
        Return the constant terms from a linear expression.
        """
        ...

    def getValue(self) -> float:
        """
        Compute the value of the expression, using the current solution.
        """
        ...

    @overload
    def getVar(self, i: slice) -> list[Var]: ...
    @overload
    def getVar(self, i: int) -> Var: ...
    def getVar(self, i: int | slice) -> Var | list[Var]:
        """
        Return the variable for the term at index 'i'.

        Args:
            i: Index of term whose coefficient is requested
        """
    
    def add(self, arg1: LinearExpresion, mult: float = 1.0) -> None:
        """
        Add a linear multiple of one expression into another.
    
        Args:
            arg1: The expression to add
            mult: The linear multiplier
        """
        ...

    def addConstant(self, constant: float) -> None:
        """
        Add a constant into a linear expression.

        Args:
            constant: The value to add
        """
        ...

    @overload
    def addTerms(self, newcoefs: list[float], newvars: list[Var]) -> None: ...
    @overload
    def addTerms(self, newcoefs: float, newvars: Var) -> None: ...
    def addTerms(self, newcoefs: list[float] | float, newvars: list[Var] | Var) -> None:
        """
        Add a list of terms into a linear expression.

        Args:
            newcoefs: The coefficients for the new terms
            newvars: The variables for the new terms
        """
        ...

    def __add__(self, x: Union[LinearExpresion, Var, float], /) -> LinearExpresion: ...

    def __radd__(self, x: Union[Var, float], /) -> LinearExpresion: ...

    def __iadd__(self, x: Union[LinearExpresion, Var, float], /) -> LinearExpresion: ...

    def __sub__(self, x: Union[LinearExpresion, Var, float], /) -> LinearExpresion: ...

    def __rsub__(self, x: Union[Var, float], /) -> LinearExpresion: ...

    def __isub__(self, x:  Union[LinearExpresion, Var, float], /) -> LinearExpresion: ...

    def __neg__(self) -> LinearExpresion: ...

    @overload
    def __mul__(self, x: float, /) -> LinearExpresion: ...
    @overload
    def __mul__(self, x: Union[LinearExpresion, Var], /) -> QuadraticExpresion: ...
    def __mul__(self, x: Union[LinearExpresion, Var, float], /) -> Expresion: ...

    @overload
    def __imul__(self, x: float, /) -> LinearExpresion: ...
    @overload
    def __imul__(self, x: Union[LinearExpresion, Var], /) -> QuadraticExpresion: ...
    def __imul__(self, x: Union[LinearExpresion, Var, float], /) -> Expresion: ...  # type: ignore

    @overload
    def __rmul__(self, x: float, /) -> LinearExpresion: ...
    @overload
    def __rmul__(self, x: Var, /) -> QuadraticExpresion: ...
    def __rmul__(self, x: Union[Var, float], /) -> Expresion: ...

    def __div__(self, x: int, /) -> LinearExpresion: ...

    def __pow__(self, x: Literal[2], /) -> QuadraticExpresion: ...

    @overload   # type: ignore[override]  
    def __eq__(self, x: Union[Var, LinearExpresion], /) -> LinearConstraint: ... 
    @overload  # type: ignore[override]
    def __eq__(self, x: QuadraticExpresion, /) -> QuadraticExpresion: ... 
    def __eq__(self, x: Union[Var, Expresion], /) -> Constraint: ...  # type: ignore[override]

    @overload   # type: ignore[override]  
    def __le__(self, x: Union[Var, LinearExpresion], /) -> LinearConstraint: ... 
    @overload  # type: ignore[override]
    def __le__(self, x: QuadraticExpresion, /) -> QuadraticExpresion: ...  # type: ignore[misc]
    def __le__(self, x: Union[Var, Expresion], /) -> Constraint: ...  # type: ignore[override, misc]

    @overload   # type: ignore[override]  
    def __ge__(self, x: Union[Var, LinearExpresion], /) -> LinearConstraint: ... 
    @overload  # type: ignore[override]
    def __ge__(self, x: QuadraticExpresion, /) -> QuadraticExpresion: ...  # type: ignore[misc]
    def __ge__(self, x: Union[Var, Expresion], /) -> Constraint: ...  # type: ignore[override, misc]


class QuadraticExpresion(Protocol):
    def clear(self) -> None:
        """
        Set a quadratic expression to zero
        """
        ...

    def copy(self) -> QuadraticExpresion:
        """
        Copy a quadratic expression
        """
        ...

    def remove(self, which: int | Var) -> None:
        """
        Remove a term from the expression.

        Args:
            which: Term to remove.  Can be an int, in which case the term at
                index 'which' is removed, or a Var, in which case all terms that
                involve the Var 'which' are removed.
        """
        ...

    def size(self) -> int:
        """
        Return the number of terms in a linear expression.
        """
        ...

    def getCoeff(self, i: int | slice) -> float | list[float]:
        """
        Return the coefficient for the term at index 'i'.

        Args:
            i: Index of term whose coefficient is requested
        """
        ...

    def getLinExpr(self) -> LinearExpresion:
        """
        Return the linear portion of a quadration expression.
        """
        ...

    def getValue(self) -> float:
        """
        Compute the value of the expression, using the current solution.
        """
        ...

    def getVar(self, i: int | slice) -> Var | list[Var]:
        """
        Return the variable for the term at index 'i'.

        Args:
            i: Index of term whose coefficient is requested
        """
    
    def add(self, arg1: LinearExpresion, mult: float = 1.0) -> None:
        """
        Add a linear multiple of one expression into another.
    
        Args:
            arg1: The expression to add
            mult: The linear multiplier
        """
        ...

    def addConstant(self, constant: float) -> None:
        """
        Add a constant into a linear expression.

        Args:
            constant: The value to add
        """
        ...

    @overload
    def addTerms(self, newcoefs: Iterable[float], newvars: Iterable[Var]) -> None: ...
    @overload
    def addTerms(self, newcoefs: float, newvars: Var) -> None: ...
    def addTerms(self, newcoefs: Iterable[float] | float, newvars: Iterable[Var] | Var) -> None:
        """
        Add a list of terms into a linear expression.

        Args:
            newcoefs: The coefficients for the new terms
            newvars: The variables for the new terms
        """
        ...

    @overload
    def getVar1(self, i: slice) -> list[Var]: ...
    @overload
    def getVar1(self, i: int) -> Var: ...
    def getVar1(self, i: slice | int) -> Var | list[Var]: 
        """
        Return the first variable for the quadratic term at index 'i'.

        Args:
            i (slice | int): Index of quadratic term whose variable is requested

        """
        ...

    @overload
    def getVar2(self, i: slice) -> list[Var]: ...
    @overload
    def getVar2(self, i: int) -> Var: ...
    def getVar2(self, i: int | slice) -> Var | list[Var]: 
        """
        Return the second variable for the quadratic term at index 'i'.

        Args:
            i (slice | int): Index of quadratic term whose variable is requested

        """
        ...

    def __add__(self, x: Expresionable, /) -> QuadraticExpresion: ...

    def __radd__(self, x: Expresionable, /) -> QuadraticExpresion: ...

    def __iadd__(self, x: Expresionable, /) -> QuadraticExpresion: ...

    def __sub__(self, x: Expresionable, /) -> QuadraticExpresion: ...

    def __rsub__(self, x: Expresionable, /) -> QuadraticExpresion: ...

    def __isub__(self, x: Expresionable, /) -> QuadraticExpresion: ...

    def __neg__(self, x: Expresionable, /) -> QuadraticExpresion: ...

    def __mul__(self, x: Expresionable, /) -> QuadraticExpresion: ...

    def __rmul__(self, x: Expresionable, /) -> QuadraticExpresion: ...

    def __imul__(self, x: Expresionable, /) -> QuadraticExpresion: ...

    def __div__(self, x: float, /) -> QuadraticExpresion: ...

    def __eq__(self, x: Union[Var, Expresion], /) -> QuadraticConstraint: ...  # type: ignore[override]
 
    def __le__(self, x: Union[Var, Expresion], /) -> QuadraticConstraint: ...  # type: ignore[override, misc]

    def __ge__(self, x: Union[Var, Expresion], /) -> QuadraticConstraint: ...  # type: ignore[override, misc]


class Constraint(Protocol):
    ...


class LinearConstraint(Constraint, Protocol):
    """
    Gurobi constraint object.  Constraints have a number of attributes.
    Some can be set (e.g., c.rhs = 0.0), while others can only be queried
    (e.g., print(c.pi)).  The most commonly used constraint attributes are:
        sense: Constraint sense ('<', '>', or '=').
        rhs: Right-hand side value.
        constrName: Constraint name.
        pi: Dual value in current solution
        slack: Slack in current solution.

    Type "help(GRB.attr)" for a list of all available attributes.

    Note that attribute modifications are handled in a lazy fashion.  You
    won't see the effect of a change until after the next call to Model.update()
    or Model.optimize().
    """
    sense: Literal['<', '>', '=']
    rhs: float
    constrname: str
    pi: float
    slack: float
    


class QuadraticConstraint(Constraint, Protocol):
    """
    Gurobi quadratic constraint object. Quadratic constraints have a
    number of attributes. Some can be set (e.g., c.QCRHS = 0.0), while
    others can only be queried (e.g., print(c.QCPi)). The most commonly
    used quadratic constraint attributes are:
        QCSense: Constraint sense ('<', '>', or '=')
        QCRHS: Right-hand side value
        QCName: Constraint name
        QCPi: Dual value in current solution (if available)
        QCSlack: Slack in current solution
    Type "help(GRB.attr)" for a list of all available attributes.
    Note that attribute modifications are handled in a lazy fashion. You
    won't see the effect of a change until after the next call to
    Model.update() or Model.optimize().
    """
    qcsense: Literal['<', '>', '=']
    qcrhs: float
    qcname: str
    qcpi: float
    qcslack: float
    


@overload  # type: ignore[no-overload-impl]
def sum(iterable: Iterable[Union[LinearExpresion, Var, float]]) -> LinearExpresion: ...
@overload
def sum(iterable: Iterable[Expresionable]) -> Expresion: ...


print(sum([1,2,3]))


a: Var # = cast(Literal[3], Var)
b: Var # = cast(Literal[3], Var)
c = (a, b, a * b)
exp = a + 2

reveal_type(b + exp)
reveal_type(a + b)
reveal_type(a * b)
reveal_type(c)
d = sum(c)
reveal_type(d)

import gurobipy as gp
from gurobipy import GRB
m = gp.Model("mip1") 
x = m.addVar(vtype=GRB.BINARY, name="x")
y = m.addVar(vtype=GRB.BINARY, name="y")
z = m.addVar(vtype=GRB.BINARY, name="z")