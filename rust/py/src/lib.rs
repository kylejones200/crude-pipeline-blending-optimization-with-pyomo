use crude_pipeline_blending_optimization_with_pyomo_core::evaluate_blend;
use numpy::PyReadonlyArray1;
use pyo3::prelude::*;

#[pyfunction]
fn evaluate_blend_py(
    volumes: PyReadonlyArray1<f64>,
    unit_costs: PyReadonlyArray1<f64>,
    qualities: PyReadonlyArray1<f64>,
    min_volume: f64,
    max_volume: f64,
    min_quality: f64,
    max_quality: f64,
) -> PyResult<(f64, f64, bool, f64)> {
    let r = evaluate_blend(
        volumes.as_slice()?, unit_costs.as_slice()?, qualities.as_slice()?,
        min_volume, max_volume, min_quality, max_quality,
    );
    Ok((r.total_cost, r.total_volume, r.feasible, r.violation))
}

#[pyfunction]
#[pyo3(signature = (volumes, unit_costs, qualities, min_volume, max_volume, min_quality, max_quality, iterations=50_000))]
fn bench_kernel_py(
    volumes: PyReadonlyArray1<f64>, unit_costs: PyReadonlyArray1<f64>, qualities: PyReadonlyArray1<f64>,
    min_volume: f64, max_volume: f64, min_quality: f64, max_quality: f64, iterations: usize,
) -> PyResult<f64> {
    let v = volumes.as_slice()?.to_vec();
    let c = unit_costs.as_slice()?.to_vec();
    let q = qualities.as_slice()?.to_vec();
    let start = std::time::Instant::now();
    for _ in 0..iterations { let _ = evaluate_blend(&v, &c, &q, min_volume, max_volume, min_quality, max_quality); }
    Ok(start.elapsed().as_secs_f64())
}

#[pymodule]
fn crude_pipeline_blending_optimization_with_pyomo_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(evaluate_blend_py, m)?)?;
    m.add_function(wrap_pyfunction!(bench_kernel_py, m)?)?;
    Ok(())
}
