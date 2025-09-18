"""Analytical utilities for evaluating recycling performance."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np


@dataclass(slots=True)
class ThroughputWindow:
    """Represents throughput observations over a sliding window."""

    timestamps: List[float]
    counts: List[int]

    def throughput_per_hour(self) -> float:
        """Compute throughput per hour."""

        if not self.timestamps or not self.counts:
            return 0.0
        duration = max(self.timestamps) - min(self.timestamps)
        if duration <= 0:
            return float(sum(self.counts)) * 3600.0
        total_items = sum(self.counts)
        return (total_items / duration) * 3600.0


@dataclass(slots=True)
class AccuracyBreakdown:
    """Stores accuracy metrics for the detection pipeline."""

    per_class_accuracy: Dict[str, float]
    macro_avg: float
    weighted_avg: float


def compute_confusion_matrix(
    y_true: Iterable[str], y_pred: Iterable[str], labels: Iterable[str]
) -> Tuple[np.ndarray, Dict[str, int]]:
    """Compute a confusion matrix and mapping from label to index."""

    labels = list(labels)
    index_map = {label: i for i, label in enumerate(labels)}
    matrix = np.zeros((len(labels), len(labels)), dtype=int)
    for truth, pred in zip(y_true, y_pred):
        matrix[index_map[truth], index_map[pred]] += 1
    return matrix, index_map


def compute_accuracy_breakdown(matrix: np.ndarray, labels: List[str]) -> AccuracyBreakdown:
    """Compute macro and weighted accuracy from a confusion matrix."""

    per_class_accuracy: Dict[str, float] = {}
    weights: List[int] = []
    for idx, label in enumerate(labels):
        true_positive = matrix[idx, idx]
        total = matrix[idx].sum()
        acc = true_positive / total if total > 0 else 0.0
        per_class_accuracy[label] = acc
        weights.append(total)
    macro_avg = mean(per_class_accuracy.values()) if per_class_accuracy else 0.0
    total_samples = sum(weights)
    weighted_avg = (
        sum(per_class_accuracy[label] * weight for label, weight in zip(labels, weights)) / total_samples
        if total_samples
        else 0.0
    )
    return AccuracyBreakdown(
        per_class_accuracy=per_class_accuracy,
        macro_avg=macro_avg,
        weighted_avg=weighted_avg,
    )


def compute_oee(availability: float, performance: float, quality: float) -> float:
    """Calculate Overall Equipment Effectiveness."""

    return availability * performance * quality


def compute_recovery_rate(recovered: int, total: int) -> float:
    """Calculate material recovery rate."""

    if total == 0:
        return 0.0
    return recovered / total


@dataclass(slots=True)
class PredictiveMaintenanceInsight:
    """Summary for predictive maintenance models."""

    component_id: str
    failure_probability: float
    time_to_failure_hours: float
    recommended_action: str


@dataclass(slots=True)
class OeeBreakdown:
    """Detailed view of availability, performance, and quality contributions."""

    availability: float
    performance: float
    quality: float
    oee: float


def moving_average(values: Sequence[float], window: int) -> List[float]:
    """Compute a simple moving average for trend analysis."""

    if window <= 0:
        raise ValueError("Window must be positive")
    if not values:
        return []
    padded = [values[0]] * (window - 1) + list(values)
    averages = []
    for idx in range(window - 1, len(padded)):
        segment = padded[idx - window + 1 : idx + 1]
        averages.append(sum(segment) / window)
    return averages


def throughput_trend(window: ThroughputWindow) -> float:
    """Estimate throughput trend as percentage change across the window."""

    if len(window.counts) < 2:
        return 0.0
    first = window.counts[0]
    last = window.counts[-1]
    if first == 0:
        return 0.0
    return (last - first) / first


def compute_oee_breakdown(availability: float, performance: float, quality: float) -> OeeBreakdown:
    """Return an :class:`OeeBreakdown` with computed aggregate."""

    oee_value = compute_oee(availability, performance, quality)
    return OeeBreakdown(
        availability=availability,
        performance=performance,
        quality=quality,
        oee=oee_value,
    )


def recommend_maintenance(
    telemetry: Dict[str, float],
    threshold: float = 0.35,
) -> List[PredictiveMaintenanceInsight]:
    """Produce maintenance recommendations based on telemetry heuristics."""

    insights: List[PredictiveMaintenanceInsight] = []
    for component, vibration in telemetry.items():
        probability = float(np.clip(vibration / 10.0, 0.0, 1.0))
        if probability < threshold:
            continue
        hours = float(np.clip(200.0 * (1.0 - probability), 8.0, 200.0))
        action = "schedule lubrication" if vibration < 6.0 else "dispatch technician"
        insights.append(
            PredictiveMaintenanceInsight(
                component_id=component,
                failure_probability=probability,
                time_to_failure_hours=hours,
                recommended_action=action,
            )
        )
    return insights

