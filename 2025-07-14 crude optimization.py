"""Crude blend optimization with Pyomo."""

import pyomo.environ as pyo


def avail_rule(m, c, avail):
    return m.vol[c] <= avail[c]


def main() -> None:
    crudes = ["A", "B", "C"]
    cost = {"A": 70, "B": 80, "C": 65}
    api = {"A": 34, "B": 40, "C": 30}
    sulfur = {"A": 1.2, "B": 0.5, "C": 2.0}
    avail = {"A": 5000, "B": 3000, "C": 4000}
    target_volume = 6000
    model = pyo.ConcreteModel()
    model.crudes = pyo.Set(initialize=crudes)
    model.vol = pyo.Var(model.crudes, domain=pyo.NonNegativeReals)
    model.cost = pyo.Objective(
        expr=sum(model.vol[c] * cost[c] for c in model.crudes), sense=pyo.minimize
    )
    model.total_volume = pyo.Constraint(
        expr=sum(model.vol[c] for c in model.crudes) == target_volume
    )
    model.sulfur = pyo.Constraint(
        expr=sum(model.vol[c] * sulfur[c] for c in model.crudes) <= target_volume
    )
    model.api = pyo.Constraint(
        expr=sum(model.vol[c] * api[c] for c in model.crudes) >= target_volume * 35
    )
    model.avail = pyo.Constraint(
        model.crudes, rule=lambda m, c, avail=avail: avail_rule(m, c, avail)
    )
    result = pyo.SolverFactory("glpk").solve(model)
    if result.solver.termination_condition == pyo.TerminationCondition.optimal:
        for c in crudes:
            print(f"Crude {c}: {pyo.value(model.vol[c]):.1f} bbl")


if __name__ == "__main__":
    main()
