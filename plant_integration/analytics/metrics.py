"""Analytical utilities for evaluating recycling performance."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Dict, Iterable, List, Tuple

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

