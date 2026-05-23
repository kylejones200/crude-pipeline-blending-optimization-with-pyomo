use crude_pipeline_blending_optimization_with_pyomo_core::evaluate_blend;
fn main() {
    let v=[0.4,0.35,0.25]; let c=[70.,80.,65.]; let q=[0.5,0.6,0.4];
    for _ in 0..100_000 { let _=evaluate_blend(&v,&c,&q,0.9,1.0,0.45,0.65); }
}
