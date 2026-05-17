"""Generated from Jupyter notebook: crude_oil_scheduling_optimization

Magics and shell lines are commented out. Run with a normal Python interpreter."""

import numpy as np
import pandas as pd


def main():
    months = ["M+3", "M+4"]
    tanks = ["light", "medium", "heavy"]
    capacity = pd.Series({"light": 80000, "medium": 120000, "heavy": 100000})
    demand = pd.DataFrame(
        {
            "tank": np.repeat(tanks, len(months)),
            "month": months * len(tanks),
            "barrels": [50000, 55000, 70000, 65000, 60000, 60000],
        }
    )
    sources = pd.DataFrame(
        {
            "source": ["foreign", "canada", "domestic"],
            "lead": [3, 2, 1],
            "cost": [62.0, 66.0, 70.0],
            "max_M+3": [120000, 90000, 80000],
            "max_M+4": [120000, 90000, 80000],
        }
    )
    mix = pd.DataFrame(
        {
            "source": [
                "foreign",
                "foreign",
                "foreign",
                "canada",
                "canada",
                "canada",
                "domestic",
                "domestic",
                "domestic",
            ],
            "tank": ["light", "medium", "heavy"] * 3,
            "frac": [0.1, 0.3, 0.6, 0.2, 0.5, 0.3, 0.5, 0.35, 0.15],
        }
    )
    grid = (
        sources.assign(key=1)
        .merge(pd.DataFrame({"month": months, "key": 1}), on="key")
        .drop(columns="key")
    )
    init_inv = pd.Series({"light": 10000, "medium": 20000, "heavy": 15000})
    dem = demand.pivot(index="tank", columns="month", values="barrels").fillna(0)
    R = (
        mix.pivot(index="source", columns="tank", values="frac")
        .reindex(index=sources["source"])
        .fillna(0)
    )
    c = sources.set_index("source")["cost"]
    smax = sources.set_index("source")[["max_M+3", "max_M+4"]].rename(
        columns={"max_M+3": "M+3", "max_M+4": "M+4"}
    )
    import pyoframe as pf

    m = pf.Model(solver="highs")
    m.Order = pf.Variable(grid[["source", "month"]], lb=0)
    orders_tbl = (
        grid.pivot(index="source", columns="month", values="lead")
        .reset_index()[["source", "M+3"]]
        .drop(columns="M+3")
    )
    orders_tbl = grid[["source", "month"]].drop_duplicates()
    arrivals = {}
    for mo in months:
        O_mo = pf.slice(m.Order, {"month": mo})
        arrivals[mo] = (
            (R.reset_index()[["source", "light"]] * O_mo)
            .rename({"light": "val"})
            .assign(tank="light")
            .rename(columns={"val": "qty"})
            .append(
                (R.reset_index()[["source", "medium"]] * O_mo)
                .rename({"medium": "val"})
                .assign(tank="medium")
                .rename(columns={"val": "qty"})
            )
            .append(
                (R.reset_index()[["source", "heavy"]] * O_mo)
                .rename({"heavy": "val"})
                .assign(tank="heavy")
                .rename(columns={"val": "qty"})
            )
        )
    m.minimize = pf.sum(
        grid.merge(c.rename("cost"), on="source").assign(
            expr=lambda df: df["cost"] * m.Order
        )[["expr"]]
    )
    for t in tanks:
        for mo in months:
            coeff = R[t].rename("coef").reset_index().assign(month=mo)
            arr_expr = pf.sum(coeff[["source", "month", "coef"]] * m.Order)
            endinv = init_inv[t] + arr_expr - dem.loc[t, mo]
            setattr(m, f"cap_{t}_{mo}", endinv <= capacity[t])
            setattr(m, f"nn_{t}_{mo}", endinv >= 0)
    for mo in months:
        mm = smax[mo]
        for s in smax.index:
            setattr(
                m,
                f"max_{s}_{mo}",
                pf.slice(m.Order, {"source": s, "month": mo}) <= float(mm.loc[s]),
            )
    m.optimize()
    orders_solution = m.Order.solution.to_pandas().rename(
        columns={"solution": "barrels"}
    )
    print(orders_solution)
    from mip import CBC, Model, minimize, xsum

    mdl = Model(sense=minimize, solver_name=CBC)
    S = list(sources["source"])
    M = months
    T = tanks
    Order = {(s, mo): mdl.add_var(lb=0, name=f"Order[{s},{mo}]") for s in S for mo in M}
    mdl.objective = xsum((c.loc[s] * Order[s, mo] for s in S for mo in M))
    for t in T:
        for mo in M:
            arrivals = xsum((R.loc[s, t] * Order[s, mo] for s in S))
            endinv = init_inv[t] + arrivals - dem.loc[t, mo]
            mdl += (endinv >= 0, f"nn_{t}_{mo}")
            mdl += (endinv <= capacity[t], f"cap_{t}_{mo}")
    for mo in M:
        for s in S:
            mdl += (Order[s, mo] <= float(smax.loc[s, mo]), f"max_{s}_{mo}")
    mdl.optimize()
    orders_mip = []
    for s in S:
        for mo in M:
            orders_mip.append({"source": s, "month": mo, "barrels": Order[s, mo].x})
    orders_mip = pd.DataFrame(orders_mip)
    print(orders_mip)
    import pyoptinterface as poi
    from pyoptinterface import highs

    model = highs.Model()
    S = list(sources["source"])
    M = months
    T = tanks
    Order = {
        (s, mo): model.add_variable(
            lb=0, ub=None, domain=poi.VariableDomain.Continuous, name=f"Order[{s},{mo}]"
        )
        for s in S
        for mo in M
    }
    obj = 0.0
    for s in S:
        for mo in M:
            obj = obj + float(c.loc[s]) * Order[s, mo]
    model.set_objective(obj, poi.ObjectiveSense.Minimize)
    for t in T:
        for mo in M:
            expr = 0.0
            for s in S:
                expr = expr + float(R.loc[s, t]) * Order[s, mo]
            endinv = expr + float(init_inv[t]) - float(dem.loc[t, mo])
            model.add_linear_constraint(endinv >= 0.0, name=f"nn_{t}_{mo}")
            model.add_linear_constraint(
                endinv <= float(capacity[t]), name=f"cap_{t}_{mo}"
            )
    for mo in M:
        for s in S:
            model.add_linear_constraint(
                Order[s, mo] <= float(smax.loc[s, mo]), name=f"max_{s}_{mo}"
            )
    model.set_model_attribute(poi.ModelAttribute.Silent, False)
    model.optimize()
    orders_poi = []
    for s in S:
        for mo in M:
            orders_poi.append(
                {"source": s, "month": mo, "barrels": model.get_value(Order[s, mo])}
            )
    orders_poi = pd.DataFrame(orders_poi)
    print(orders_poi)
    import numpy as np
    import pandas as pd
    import pyoframe as pf

    months = ["M+3", "M+4"]
    tanks = ["light", "medium", "heavy"]
    capacity = pd.Series({"light": 80000, "medium": 120000, "heavy": 100000})
    init_inv = pd.Series({"light": 10000, "medium": 20000, "heavy": 15000})
    demand = pd.DataFrame(
        {
            "tank": np.repeat(tanks, len(months)),
            "month": months * len(tanks),
            "barrels": [50000, 55000, 70000, 65000, 60000, 60000],
        }
    )
    sources = pd.DataFrame(
        {
            "source": ["foreign", "canada", "domestic"],
            "lead": [3, 2, 1],
            "cost": [62.0, 66.0, 70.0],
            "max_M+3": [120000, 90000, 80000],
            "max_M+4": [120000, 90000, 80000],
        }
    )
    mix = pd.DataFrame(
        {
            "source": [
                "foreign",
                "foreign",
                "foreign",
                "canada",
                "canada",
                "canada",
                "domestic",
                "domestic",
                "domestic",
            ],
            "tank": ["light", "medium", "heavy"] * 3,
            "frac": [0.1, 0.3, 0.6, 0.2, 0.5, 0.3, 0.5, 0.35, 0.15],
        }
    )
    dem = demand.pivot(index="tank", columns="month", values="barrels").fillna(0)
    R = (
        mix.pivot(index="source", columns="tank", values="frac")
        .reindex(sources["source"])
        .fillna(0)
    )
    c_tbl = sources[["source", "cost"]]
    smax = sources.set_index("source")[["max_M+3", "max_M+4"]].rename(
        columns={"max_M+3": "M+3", "max_M+4": "M+4"}
    )
    m = pf.Model(solver="highs")
    m.Order_M3 = pf.Variable(sources[["source"]], lb=0)
    m.Order_M4 = pf.Variable(sources[["source"]], lb=0)
    obj_M3 = pf.sum(over=c_tbl, expr=c_tbl["cost"] * m.Order_M3)
    obj_M4 = pf.sum(over=c_tbl, expr=c_tbl["cost"] * m.Order_M4)
    m.minimize = obj_M3 + obj_M4
    for t in tanks:
        coef_tbl = R[t].rename("coef").reset_index()
        arr_M3 = pf.sum(over=coef_tbl, expr=coef_tbl["coef"] * m.Order_M3)
        arr_M4 = pf.sum(over=coef_tbl, expr=coef_tbl["coef"] * m.Order_M4)
        end_M3 = init_inv[t] + arr_M3 - float(dem.loc[t, "M+3"])
        end_M4 = init_inv[t] + arr_M4 - float(dem.loc[t, "M+4"])
        m.add_constraint(end_M3 >= 0, name=f"nn_{t}_M3")
        m.add_constraint(end_M3 <= float(capacity[t]), name=f"cap_{t}_M3")
        m.add_constraint(end_M4 >= 0, name=f"nn_{t}_M4")
        m.add_constraint(end_M4 <= float(capacity[t]), name=f"cap_{t}_M4")
    for s in smax.index:
        m.add_constraint(
            m.Order_M3.loc[{"source": s}] <= float(smax.loc[s, "M+3"]),
            name=f"max_{s}_M3",
        )
        m.add_constraint(
            m.Order_M4.loc[{"source": s}] <= float(smax.loc[s, "M+4"]),
            name=f"max_{s}_M4",
        )
    m.optimize()
    sol_M3 = (
        m.Order_M3.solution.to_pandas()
        .rename(columns={"solution": "barrels"})
        .assign(month="M+3")
    )
    sol_M4 = (
        m.Order_M4.solution.to_pandas()
        .rename(columns={"solution": "barrels"})
        .assign(month="M+4")
    )
    orders = pd.concat([sol_M3, sol_M4], ignore_index=True)
    print(orders)
    cost_s = c_tbl.set_index("source")["cost"]
    obj_M3 = pf.sum(over=["source"], expr=cost_s * m.Order_M3)
    obj_M4 = pf.sum(over=["source"], expr=cost_s * m.Order_M4)
    m.minimize = obj_M3 + obj_M4
    for t in tanks:
        coef_s = R[t]
        arr_M3 = pf.sum(over=["source"], expr=coef_s * m.Order_M3)
        arr_M4 = pf.sum(over=["source"], expr=coef_s * m.Order_M4)
        end_M3 = init_inv[t] + arr_M3 - float(dem.loc[t, "M+3"])
        end_M4 = init_inv[t] + arr_M4 - float(dem.loc[t, "M+4"])
        m.add_constraint(end_M3 >= 0, name=f"nn_{t}_M3")
        m.add_constraint(end_M3 <= float(capacity[t]), name=f"cap_{t}_M3")
        m.add_constraint(end_M4 >= 0, name=f"nn_{t}_M4")
        m.add_constraint(end_M4 <= float(capacity[t]), name=f"cap_{t}_M4")
    import numpy as np
    import pandas as pd
    import pyoframe as pf

    months = ["M+3", "M+4"]
    tanks = ["light", "medium", "heavy"]
    capacity = pd.Series({"light": 80000, "medium": 120000, "heavy": 100000})
    init_inv = pd.Series({"light": 10000, "medium": 20000, "heavy": 15000})
    demand = pd.DataFrame(
        {
            "tank": np.repeat(tanks, len(months)),
            "month": months * len(tanks),
            "barrels": [50000, 55000, 70000, 65000, 60000, 60000],
        }
    )
    sources = pd.DataFrame(
        {
            "source": ["foreign", "canada", "domestic"],
            "lead": [3, 2, 1],
            "cost": [62.0, 66.0, 70.0],
            "max_M+3": [120000, 90000, 80000],
            "max_M+4": [120000, 90000, 80000],
        }
    )
    mix = pd.DataFrame(
        {
            "source": [
                "foreign",
                "foreign",
                "foreign",
                "canada",
                "canada",
                "canada",
                "domestic",
                "domestic",
                "domestic",
            ],
            "tank": ["light", "medium", "heavy"] * 3,
            "frac": [0.1, 0.3, 0.6, 0.2, 0.5, 0.3, 0.5, 0.35, 0.15],
        }
    )
    dem = demand.pivot(index="tank", columns="month", values="barrels").fillna(0)
    R = (
        mix.pivot(index="source", columns="tank", values="frac")
        .reindex(sources["source"])
        .fillna(0)
    )
    cost_s = sources.set_index("source")["cost"]
    smax = sources.set_index("source")[["max_M+3", "max_M+4"]].rename(
        columns={"max_M+3": "M+3", "max_M+4": "M+4"}
    )
    m = pf.Model(solver="highs")
    m.Order_M3 = pf.Variable(sources[["source"]], lb=0)
    m.Order_M4 = pf.Variable(sources[["source"]], lb=0)
    obj_M3 = pf.sum(over=["source"], expr=cost_s * m.Order_M3)
    obj_M4 = pf.sum(over=["source"], expr=cost_s * m.Order_M4)
    m.minimize = obj_M3 + obj_M4
    for t in tanks:
        coef_s = R[t]
        arr_M3 = pf.sum(over=["source"], expr=coef_s * m.Order_M3)
        arr_M4 = pf.sum(over=["source"], expr=coef_s * m.Order_M4)
        end_M3 = init_inv[t] + arr_M3 - float(dem.loc[t, "M+3"])
        end_M4 = init_inv[t] + arr_M4 - float(dem.loc[t, "M+4"])
        setattr(m, f"nn_{t}_M3", end_M3 >= 0)
        setattr(m, f"cap_{t}_M3", end_M3 <= float(capacity[t]))
        setattr(m, f"nn_{t}_M4", end_M4 >= 0)
        setattr(m, f"cap_{t}_M4", end_M4 <= float(capacity[t]))
    for s in smax.index:
        setattr(
            m, f"max_{s}_M3", m.Order_M3.loc[{"source": s}] <= float(smax.loc[s, "M+3"])
        )
        setattr(
            m, f"max_{s}_M4", m.Order_M4.loc[{"source": s}] <= float(smax.loc[s, "M+4"])
        )
    m.optimize()
    sol_M3 = (
        m.Order_M3.solution.to_pandas()
        .rename(columns={"solution": "barrels"})
        .assign(month="M+3")
    )
    sol_M4 = (
        m.Order_M4.solution.to_pandas()
        .rename(columns={"solution": "barrels"})
        .assign(month="M+4")
    )
    orders = pd.concat([sol_M3, sol_M4], ignore_index=True)
    print(orders)
    m = pf.Model(solver="highs")
    m.Order_M3 = pf.Variable(sources[["source"]], lb=0)
    m.Order_M4 = pf.Variable(sources[["source"]], lb=0)
    obj_M3 = pf.sum(over=["source"], expr=cost_s * m.Order_M3)
    obj_M4 = pf.sum(over=["source"], expr=cost_s * m.Order_M4)
    m.minimize = obj_M3 + obj_M4
    for t in tanks:
        coef_s = R[t]
        arr_M3 = pf.sum(over=["source"], expr=coef_s * m.Order_M3)
        arr_M4 = pf.sum(over=["source"], expr=coef_s * m.Order_M4)
        end_M3 = init_inv[t] + arr_M3 - float(dem.loc[t, "M+3"])
        end_M4 = init_inv[t] + arr_M4 - float(dem.loc[t, "M+4"])
        setattr(m, f"nn_{t}_M3", end_M3 >= 0)
        setattr(m, f"cap_{t}_M3", end_M3 <= float(capacity[t]))
        setattr(m, f"nn_{t}_M4", end_M4 >= 0)
        setattr(m, f"cap_{t}_M4", end_M4 <= float(capacity[t]))
    m.max_M3 = m.Order_M3 <= smax["M+3"]
    m.max_M4 = m.Order_M4 <= smax["M+4"]
    m.optimize()
    sol_M3 = (
        m.Order_M3.solution.to_pandas()
        .rename(columns={"solution": "barrels"})
        .assign(month="M+3")
    )
    sol_M4 = (
        m.Order_M4.solution.to_pandas()
        .rename(columns={"solution": "barrels"})
        .assign(month="M+4")
    )
    orders = pd.concat([sol_M3, sol_M4], ignore_index=True)
    print(orders)


def main() -> None:
    main()


if __name__ == "__main__":
    main()
