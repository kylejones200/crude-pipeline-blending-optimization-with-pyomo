//! Simple blend cost evaluation with linear constraint checks (not full MIP).

#[derive(Debug, Clone, PartialEq)]
pub struct BlendEvaluation {
    pub total_cost: f64,
    pub total_volume: f64,
    pub feasible: bool,
    pub violation: f64,
}

/// Weighted blend cost with min/max volume and quality bounds.
pub fn evaluate_blend(
    volumes: &[f64],
    unit_costs: &[f64],
    qualities: &[f64],
    min_volume: f64,
    max_volume: f64,
    min_quality: f64,
    max_quality: f64,
) -> BlendEvaluation {
    assert_eq!(volumes.len(), unit_costs.len());
    assert_eq!(volumes.len(), qualities.len());

    let total_volume: f64 = volumes.iter().sum();
    let total_cost: f64 = volumes.iter().zip(unit_costs).map(|(v, c)| v * c).sum();

    let mut violation = 0.0;
    if total_volume < min_volume {
        violation += min_volume - total_volume;
    }
    if total_volume > max_volume {
        violation += total_volume - max_volume;
    }

    let blend_quality = if total_volume > 0.0 {
        volumes
            .iter()
            .zip(qualities)
            .map(|(v, q)| v * q)
            .sum::<f64>()
            / total_volume
    } else {
        0.0
    };

    if blend_quality < min_quality {
        violation += min_quality - blend_quality;
    }
    if blend_quality > max_quality {
        violation += blend_quality - max_quality;
    }

    for &v in volumes {
        if v < 0.0 {
            violation += -v;
        }
    }

    BlendEvaluation {
        total_cost,
        total_volume,
        feasible: violation <= 1e-9,
        violation,
    }
}
