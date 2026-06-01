#!/usr/bin/env python3
import argparse, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from compute_kernel import evaluate_blend
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--iterations", type=int, default=50_000)
    a = p.parse_args()
    v = np.array([0.4, 0.35, 0.25])
    c = np.array([70.0, 80.0, 65.0])
    q = np.array([0.5, 0.6, 0.4])
    t0 = time.perf_counter()
    for _ in range(a.iterations):
        evaluate_blend(v, c, q, 0.9, 1.0, 0.45, 0.65)
    py_s = time.perf_counter() - t0
    try:
        import crude_pipeline_blending_optimization_with_pyomo_rs as rs
    except ImportError:
        print("Build: cd rust && maturin develop --release -m py/Cargo.toml")
        print(f"Python {py_s:.3f}s")
        return
    rs_s = rs.bench_kernel_py(v, c, q, 0.9, 1.0, 0.45, 0.65, a.iterations)
    print(f"Python {py_s:.3f}s Rust {rs_s:.3f}s speedup {py_s / rs_s:.1f}x")
    py_out = evaluate_blend(v, c, q, 0.9, 1.0, 0.45, 0.65)
    rs_out = rs.evaluate_blend_py(v, c, q, 0.9, 1.0, 0.45, 0.65)
    np.testing.assert_allclose(py_out[0], rs_out[0], rtol=1e-10)
    print("Correctness: OK")
if __name__ == "__main__":
    main()
