# Crude Pipeline Blending Optimization with Pyomo Blending crude oil is not a guessing game. Midstream companies do it to
meet contractual specs and maximize margin. Each barrel blended...

### Crude Pipeline Blending Optimization with Pyomo
Blending crude oil is not a guessing game. Midstream companies do it to
meet contractual specs and maximize margin. Each barrel blended below
spec costs money. Each unnecessary premium barrel blended in gives away
value. A well-built optimization model ensures the right blend goes into
the pipe every day.


<figcaption>Photo by <a
href="https://unsplash.com/@scentspiracy?utm_source=medium&amp;utm_medium=referral"
class="markup--anchor markup--figure-anchor"
data-href="https://unsplash.com/@scentspiracy?utm_source=medium&amp;utm_medium=referral"
rel="photo-creator noopener" target="_blank">Fulvio Ciccolo</a> on <a
href="https://unsplash.com?utm_source=medium&amp;utm_medium=referral"
class="markup--anchor markup--figure-anchor"
data-href="https://unsplash.com?utm_source=medium&amp;utm_medium=referral"
rel="photo-source noopener" target="_blank">Unsplash</a></figcaption>


This article walks through a working example of crude blending using
Pyomo in Python. We use API gravity and sulfur as constraints. The goal
is to minimize cost while meeting product specs. No proprietary data. No
black boxes. Everything runs locally and transparently.

### The Problem
You manage a tank farm with multiple crude streams. Incoming deliveries
vary each week. Your customers expect output that meets a minimum API
gravity and a maximum sulfur level. You want to mix available barrels to
meet that spec at the lowest cost.

You know:

- The available volume of each crude
- Each crude's cost, API gravity, and sulfur
- The target spec and total volume

You want to find the optimal volume of each crude to blend.

### Why Pyomo
Pyomo is a Python-based modeling language for optimization problems. It
supports linear, nonlinear, and mixed-integer formulations. It runs with
open-source solvers like GLPK and CBC. It allows constraints to be
expressed symbolically and solved with minimal boilerplate.

### Define the Data
Assume we have three crude types with these characteristics.


We want to blend 6000 barrels that meet

- Minimum API: 35
- Maximum sulfur: 1.0%

This is a constrained optimization problem.

### Build the Model
The model chooses how much of each crude to blend. The objective is to
minimize cost. Constraints ensure the total volume hits 6000 bbl, API
stays above 35, sulfur stays below 1.0%, and no crude is overdrawn.

Here's the complete code:

If you have never run pyomo, you need to install it plus the GLPK solver
pack.

``` 
!pip install pyomo
!apt install glpk-utils
!pip install glpk
```

```python
import pyomo.environ as pyo

crudes = ['A', 'B', 'C']
cost = {'A': 70, 'B': 80, 'C': 65}
api = {'A': 34, 'B': 40, 'C': 30}
sulfur = {'A': 1.2, 'B': 0.5, 'C': 2.0}
avail = {'A': 5000, 'B': 3000, 'C': 4000}
target_volume = 6000
api_min = 35
sulfur_max = 1.0
model = pyo.ConcreteModel()
model.crudes = pyo.Set(initialize=crudes)
model.vol = pyo.Var(model.crudes, domain=pyo.NonNegativeReals)
model.cost = pyo.Objective(expr=sum(model.vol[c] * cost[c] for c in model.crudes),
                           sense=pyo.minimize)
model.total_volume = pyo.Constraint(expr=sum(model.vol[c] for c in model.crudes) == target_volume)
model.sulfur_limit = pyo.Constraint(
    expr=sum(model.vol[c] * sulfur[c] for c in model.crudes) <= sulfur_max * target_volume)
model.api_limit = pyo.Constraint(
    expr=sum(model.vol[c] * api[c] for c in model.crudes) >= api_min * target_volume)
model.avail_limits = pyo.ConstraintList()
for c in model.crudes:
    model.avail_limits.add(model.vol[c] <= avail[c])
solver = pyo.SolverFactory('glpk')
result = solver.solve(model)
if (result.solver.status == pyo.SolverStatus.ok) and (result.solver.termination_condition == pyo.TerminationCondition.optimal):
    for c in crudes:
        print(f"Crude {c}: {model.vol[c]():.1f} bbl")
    total_cost = sum(model.vol[c]() * cost[c] for c in crudes)
    blend_api = sum(model.vol[c]() * api[c] for c in crudes) / target_volume
    blend_sulfur = sum(model.vol[c]() * sulfur[c] for c in crudes) / target_volume
    print(f"Total cost: ${total_cost:,.2f}")
    print(f"Blended API: {blend_api:.2f}")
    print(f"Blended sulfur: {blend_sulfur:.2f}%")
else:
    print("No optimal solution found.")
```

### Results
This runs fast. It returns the exact number of barrels to pull from each
tank. It also shows the total cost, API, and sulfur. You can change the
input specs, rerun the model, and re-optimize.

The output might look like this:

``` 
Crude A: 4285.7 bbl
Crude B: 1714.3 bbl
Crude C: 0.0 bbl
Total cost: $437,142.86
Blended API: 35.71
Blended sulfur: 1.00%
```

### Beyond the Basics
This is only the start. You can extend the model to:

- Track daily decisions over time
- Add pipeline and tank constraints
- Optimize for margin instead of cost
- Add nonlinear behavior (e.g., flash point)
- Use real-time SCADA or terminal feedstock data

### What This Solves
Midstream blending matters. Getting it right means better product value,
fewer off-spec penalties, and better margin control. A model like this,
even in simple form, can save hundreds of thousands per year.

You do not need a digital twin. You need a working model, tied to your
actual feedstock and specs, and running every day.

We can look at some alternative blending options. This graph shows
different cut points and the relative costs at that top. Each od these
blends eets the 6KBD requirement. But these do not all meet the
rewuiqrments for API and Sulphur content.


This small list shows us mixes that satisfy the API and suphlur
constraints but these are more expensive. So the "official" mix on the
upper graph is the winner.


```python
import numpy as np
import matplotlib.pyplot as plt
import numpy as np


# Define alternative blend scenarios
scenarios = {
    "Original": [3000, 2000, 1000],
    "More B, Less A": [2000, 3000, 1000],
    "All A+B": [3500, 2500, 0],
    "All B+C": [0, 4000, 2000],
    "Even Mix": [2000, 2000, 2000],
}

# Cost per barrel
blend_costs = {'A': 70, 'B': 80, 'C': 65}

# Calculate total costs per scenario
scenario_costs = {}
for name, vols in scenarios.items():
    total = (
        vols[0] * blend_costs['A'] +
        vols[1] * blend_costs['B'] +
        vols[2] * blend_costs['C']
    )
    scenario_costs[name] = {"vols": vols, "cost": total}

# Prepare stacked bar chart
labels = list(scenario_costs.keys())
crude_A = [scenario_costs[k]["vols"][0] for k in labels]
crude_B = [scenario_costs[k]["vols"][1] for k in labels]
crude_C = [scenario_costs[k]["vols"][2] for k in labels]
total_costs = [scenario_costs[k]["cost"] for k in labels]

x = np.arange(len(labels))
width = 0.6

fig, ax = plt.subplots(figsize=(10, 6))
p1 = ax.bar(x, crude_A, width, label='Crude A', color='#4CAF50')
p2 = ax.bar(x, crude_B, width, bottom=crude_A, label='Crude B', color='#2196F3')
p3 = ax.bar(x, crude_C, width,
            bottom=np.array(crude_A) + np.array(crude_B),
            label='Crude C', color='#FFC107')

# Annotate total cost
for i, cost in enumerate(total_costs):
    ax.text(x[i], crude_A[i] + crude_B[i] + crude_C[i] + 200,
            f"${cost:,.0f}", ha='center', fontsize=10, fontweight='bold')

ax.set_ylabel('Volume (bbl)')

ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
plt.tight_layout()
plt.savefig('alternative_blends_costs.png')
plt.show()

# Redefine constraint logic
def check_constraints(vols):
    total_vol = sum(vols)
    api = (vols[0]*34 + vols[1]*40 + vols[2]*30) / total_vol
    sulfur = (vols[0]*1.2 + vols[1]*0.5 + vols[2]*2.0) / total_vol
    return api >= 35 and sulfur <= 1.0

# Filter valid scenarios only
valid_scenarios = {}
for name, vols in scenarios.items():
    if sum(vols) == 6000 and check_constraints(vols):
        total = (
            vols[0] * blend_costs['A'] +
            vols[1] * blend_costs['B'] +
            vols[2] * blend_costs['C']
        )
        valid_scenarios[name] = {"vols": vols, "cost": total}

# Prepare data
labels = list(valid_scenarios.keys())
crude_A = [valid_scenarios[k]["vols"][0] for k in labels]
crude_B = [valid_scenarios[k]["vols"][1] for k in labels]
crude_C = [valid_scenarios[k]["vols"][2] for k in labels]
total_costs = [valid_scenarios[k]["cost"] for k in labels]

x = np.arange(len(labels))
width = 0.6

fig, ax = plt.subplots(figsize=(8, 5))
p1 = ax.bar(x, crude_A, width, label='Crude A', color='#4CAF50')
p2 = ax.bar(x, crude_B, width, bottom=crude_A, label='Crude B', color='#2196F3')
p3 = ax.bar(x, crude_C, width,
            bottom=np.array(crude_A) + np.array(crude_B),
            label='Crude C', color='#FFC107')

# Annotate cost
for i, cost in enumerate(total_costs):
    ax.text(x[i], crude_A[i] + crude_B[i] + crude_C[i] + 150,
            f"${cost:,.0f}", ha='center', fontsize=10, fontweight='bold')

ax.set_ylabel('Volume (bbl)')

ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
plt.tight_layout()
plt.savefig('valid_blends_only.png')
plt.show()
```
::::::::By [Kyle Jones](https://medium.com/@kyle-t-jones) on
[July 14, 2025](https://medium.com/p/d7f6c725f594).

[Canonical
link](https://medium.com/@kyle-t-jones/crude-pipeline-blending-optimization-with-pyomo-d7f6c725f594)

Exported from [Medium](https://medium.com) on November 10, 2025.
