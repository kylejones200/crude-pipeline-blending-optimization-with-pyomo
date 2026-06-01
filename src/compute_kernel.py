import numpy as np

def evaluate_blend(volumes, unit_costs, qualities, min_volume, max_volume, min_quality, max_quality):
    volumes = np.asarray(volumes, dtype=float)
    total_volume = volumes.sum()
    total_cost = float(np.dot(volumes, unit_costs))
    blend_q = float(np.dot(volumes, qualities) / total_volume) if total_volume > 0 else 0.0
    violation = 0.0
    if total_volume < min_volume: violation += min_volume - total_volume
    if total_volume > max_volume: violation += total_volume - max_volume
    if blend_q < min_quality: violation += min_quality - blend_q
    if blend_q > max_quality: violation += blend_q - max_quality
    violation += float(np.sum(np.maximum(0, -volumes)))
    return total_cost, total_volume, violation <= 1e-9, violation
