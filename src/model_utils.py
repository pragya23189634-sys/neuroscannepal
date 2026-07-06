from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    import joblib
except ImportError:
    joblib = None


def train_test_split(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    stratify: Optional[np.ndarray] = None,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if random_state is not None:
        rng = np.random.default_rng(random_state)
    else:
        rng = np.random.default_rng()

    X = np.asarray(X)
    y = np.asarray(y)

    if X.shape[0] != y.shape[0]:
        raise ValueError("X and y must have the same length")

    n_samples = X.shape[0]
    if isinstance(test_size, float):
        if test_size <= 0 or test_size >= 1:
            raise ValueError("test_size must be between 0 and 1")
        n_test = int(np.ceil(n_samples * test_size))
    else:
        n_test = int(test_size)

    if n_test <= 0:
        raise ValueError("test_size must result in at least one sample")

    if stratify is not None:
        stratify = np.asarray(stratify)
        if stratify.shape[0] != n_samples:
            raise ValueError("stratify and X must have the same length")

        test_indices: List[int] = []
        for label in np.unique(stratify):
            label_indices = np.where(stratify == label)[0]
            rng.shuffle(label_indices)
            n_label_test = int(np.ceil(len(label_indices) * n_test / n_samples))
            test_indices.extend(label_indices[:n_label_test].tolist())

        if len(test_indices) > n_test:
            test_indices = test_indices[:n_test]

        remaining_indices = [i for i in range(n_samples) if i not in test_indices]
        if len(test_indices) < n_test:
            extra = [i for i in remaining_indices if i not in test_indices]
            rng.shuffle(extra)
            test_indices.extend(extra[: n_test - len(test_indices)])

        train_indices = [i for i in range(n_samples) if i not in test_indices]
    else:
        indices = np.arange(n_samples)
        rng.shuffle(indices)
        test_indices = indices[:n_test].tolist()
        train_indices = indices[n_test:].tolist()

    X_train = X[train_indices]
    X_test = X[test_indices]
    y_train = y[train_indices]
    y_test = y[test_indices]
    return X_train, X_test, y_train, y_test


class NearestCentroidClassifier:
    def __init__(self) -> None:
        self.centroids: Dict[int, np.ndarray] = {}
        self.classes: np.ndarray = np.array([], dtype=int)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NearestCentroidClassifier":
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y)
        self.classes = np.unique(y)
        for cls in self.classes:
            rows = X[y == cls]
            if len(rows) == 0:
                raise ValueError(f"No samples found for class {cls}")
            self.centroids[int(cls)] = np.mean(rows, axis=0)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        distances = self._distance_matrix(X)
        return np.array([self.classes[np.argmin(row)] for row in distances], dtype=int)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        probs = softmax(-self._distance_matrix(X))
        return probs

    def _distance_matrix(self, X: np.ndarray) -> np.ndarray:
        if X.ndim == 1:
            X = X.reshape(1, -1)
        centroids = np.stack([self.centroids[int(cls)] for cls in self.classes], axis=0)
        X_sq = np.sum(X ** 2, axis=1)[:, None]
        C_sq = np.sum(centroids ** 2, axis=1)[None, :]
        cross = X @ centroids.T
        return X_sq + C_sq - 2 * cross


def softmax(logits: np.ndarray) -> np.ndarray:
    logits = np.asarray(logits, dtype=np.float64)
    shift = logits - np.max(logits, axis=1, keepdims=True)
    exp = np.exp(shift)
    return exp / np.sum(exp, axis=1, keepdims=True)


def accuracy_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.mean(y_true == y_pred))


def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, labels: Optional[Sequence[int]] = None) -> np.ndarray:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if labels is None:
        labels = np.unique(np.concatenate([y_true, y_pred])).tolist()
    else:
        labels = list(labels)

    cm = np.zeros((len(labels), len(labels)), dtype=int)
    label_to_index = {label: idx for idx, label in enumerate(labels)}
    for actual, predicted in zip(y_true, y_pred):
        if actual in label_to_index and predicted in label_to_index:
            cm[label_to_index[actual], label_to_index[predicted]] += 1
    return cm


def classification_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_names: Optional[List[str]] = None,
    zero_division: int = 0,
) -> str:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    labels = np.unique(np.concatenate([y_true, y_pred]))
    if target_names is None:
        target_names = [str(label) for label in labels]
    if len(target_names) != len(labels):
        target_names = [str(label) for label in labels]

    lines = ["", "                precision    recall  f1-score   support", ""]
    for label, name in zip(labels, target_names):
        true_mask = y_true == label
        pred_mask = y_pred == label
        tp = int(np.sum(true_mask & pred_mask))
        fp = int(np.sum(~true_mask & pred_mask))
        fn = int(np.sum(true_mask & ~pred_mask))
        support = int(np.sum(true_mask))

        precision = tp / (tp + fp) if (tp + fp) > 0 else zero_division
        recall = tp / (tp + fn) if (tp + fn) > 0 else zero_division
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else zero_division
        )
        lines.append(
            f"{name:>12} {precision:>9.2f} {recall:>9.2f} {f1:>9.2f} {support:>9}"
        )

    accuracy = accuracy_score(y_true, y_pred)
    lines.extend(["", f"accuracy                         {accuracy:>9.2f} {len(y_true):>9}", ""])
    return "\n".join(lines)


def save_model(model: Any, model_path: Path) -> None:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    if joblib is not None and model_path.suffix == ".joblib":
        joblib.dump(model, model_path)
        return
    with open(model_path, "wb") as fh:
        pickle.dump(model, fh)


def load_model(model_path: Path) -> Any:
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if joblib is not None and model_path.suffix == ".joblib":
        return joblib.load(model_path)
    with open(model_path, "rb") as fh:
        return pickle.load(fh)
