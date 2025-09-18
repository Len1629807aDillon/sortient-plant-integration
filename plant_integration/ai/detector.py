"""Advanced AI detection pipelines for material identification."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from ..data.structures import MaterialClass, MaterialObservation


@dataclass(slots=True)
class DetectionModelArtifacts:
    """Container for AI artifacts required during inference."""

    classifier: BaseEstimator
    scaler: StandardScaler
    feature_names: List[str]


@dataclass(slots=True)
class DetectionResult:
    """Result produced by :class:`MaterialDetector` for a single sample."""

    observation: MaterialObservation
    logits: np.ndarray
    top_classes: List[Tuple[MaterialClass, float]]


class MaterialDetector:
    """Implements the detection pipeline orchestrating pre-processing and inference."""

    def __init__(self, artifacts: DetectionModelArtifacts) -> None:
        self._artifacts = artifacts

    @classmethod
    def from_training_data(
        cls,
        feature_matrix: np.ndarray,
        labels: Iterable[str],
        feature_names: Optional[List[str]] = None,
        **rf_kwargs: object,
    ) -> "MaterialDetector":
        """Train a detector from scratch using classical machine learning."""

        scaler = StandardScaler()
        x = scaler.fit_transform(feature_matrix)
        classifier = RandomForestClassifier(
            n_estimators=rf_kwargs.get("n_estimators", 200),
            max_depth=rf_kwargs.get("max_depth", None),
            n_jobs=-1,
            class_weight="balanced_subsample",
            random_state=rf_kwargs.get("random_state", 42),
        )
        classifier.fit(x, list(labels))
        artifacts = DetectionModelArtifacts(
            classifier=classifier,
            scaler=scaler,
            feature_names=feature_names or [f"f_{i}" for i in range(feature_matrix.shape[1])],
        )
        return cls(artifacts)

    @property
    def feature_names(self) -> List[str]:
        """Return the names of features consumed by the detector."""

        return self._artifacts.feature_names

    def predict(self, sample: np.ndarray, metadata: Optional[dict] = None) -> DetectionResult:
        """Predict material class for a single sample."""

        scaled = self._artifacts.scaler.transform(sample.reshape(1, -1))
        proba = self._artifacts.classifier.predict_proba(scaled)[0]
        classes = self._artifacts.classifier.classes_
        top_indices = np.argsort(proba)[::-1][:3]
        top_classes = [(MaterialClass(classes[i]), float(proba[i])) for i in top_indices]
        observation = MaterialObservation(
            observation_id=metadata.get("observation_id") if metadata else f"obs-{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            material_class=MaterialClass(classes[np.argmax(proba)]),
            confidence=float(np.max(proba)),
            contamination_score=float(metadata.get("contamination_score", 0.0) if metadata else 0.0),
            location_coordinates=metadata.get("location_coordinates", {"x": 0.0, "y": 0.0, "z": 0.0})
            if metadata
            else {"x": 0.0, "y": 0.0, "z": 0.0},
            spectral_signature=metadata.get("spectral_signature", sample.tolist()) if metadata else sample.tolist(),
            metadata=metadata or {},
        )
        return DetectionResult(observation=observation, logits=proba, top_classes=top_classes)

    def save(self, path: Path) -> None:
        """Persist artifacts for later use."""

        np.savez_compressed(
            path,
            classifier=np.array([self._artifacts.classifier], dtype=object),
            scaler=np.array([self._artifacts.scaler], dtype=object),
            feature_names=np.array(self._artifacts.feature_names),
        )

    @classmethod
    def load(cls, path: Path) -> "MaterialDetector":
        """Restore detector artifacts."""

        archive = np.load(path, allow_pickle=True)
        artifacts = DetectionModelArtifacts(
            classifier=archive["classifier"][0],
            scaler=archive["scaler"][0],
            feature_names=archive["feature_names"].tolist(),
        )
        return cls(artifacts)

