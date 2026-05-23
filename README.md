# Crude Pipeline Blending Optimization with Pyomo

Published: 2025-07-14
Medium: [https://medium.com/@kyle-t-jones/crude-pipeline-blending-optimization-with-pyomo-d7f6c725f594](https://medium.com/@kyle-t-jones/crude-pipeline-blending-optimization-with-pyomo-d7f6c725f594)

## Business context

Blending crude oil is not a guessing game. Midstream companies do it to meet contractual specs and maximize margin. Each barrel blended below spec costs money. Each unnecessary premium barrel blended in gives away value. A well-built optimization model ensures the right blend goes into the pipe every day.

This article walks through a working example of crude blending using Pyomo in Python. We use API gravity and sulfur as constraints. The goal is to minimize cost while meeting product specs. No proprietary data. No black boxes. Everything runs locally and transparently.

You manage a tank farm with multiple crude streams. Incoming deliveries vary each week. Your customers expect output that meets a minimum API gravity and a maximum sulfur level. You want to mix available barrels to meet that spec at the lowest cost.

## About

Place the code for this article in this repository.
The original article export is saved as `article.md`.

## Files

Add your `.ipynb`, `.py`, `.yaml`, `.js`, `.ts`, or other project files here.

## Rust performance port

Side-by-side **Python vs Rust** implementation of the numeric hot loop — blend cost evaluation and constraint checks. Reference PyO3 benchmark: **~450×** on a release build (local machine; run `benchmark_rust.py` to reproduce).

| Path | Role |
|------|------|
| `src/compute_kernel.py` | Python/numpy reference kernel |
| `rust/core/` | Pure Rust library |
| `rust/py/` | PyO3 bindings |
| `rust/bench/` | Standalone CLI benchmark |
| `benchmark_rust.py` | Python vs Rust timing + correctness check |

```bash
# Rust-only CLI benchmark
cd rust && cargo run --release -p crude_pipeline_blending_optimization_with_pyomo_bench

# Python vs Rust (PyO3)
pip install maturin numpy
maturin develop --release -m rust/py/Cargo.toml
python benchmark_rust.py
```

Python ML training, solvers, and orchestration stay in Python; Rust targets the numeric hot loops. Stochastic generators validate output shapes; deterministic kernels match at tight floating-point tolerance.


## Disclaimer

Educational/demo code only. Not financial, safety, or engineering advice. Use at your own risk. Verify results independently before any production or operational use.

## License

MIT — see [LICENSE](LICENSE).