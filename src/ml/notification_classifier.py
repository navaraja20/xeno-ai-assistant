"""
ML-Based Notification Priority Classifier
Uses machine learning to predict notification importance
"""

import json
import pickle
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

from src.core.logger import setup_logger
from src.modules.smart_notifications import Notification, NotificationPriority


class NotificationClassifier:
    """ML-based notification importance classifier"""

    def __init__(self, model_dir: str = "data/models"):
        self.logger = setup_logger("notifications.classifier")
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # ML Models
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.classifier: Optional[RandomForestClassifier] = None

        # Feature extractors
        self.importance_keywords = {
            "critical": ["urgent", "asap", "critical", "emergency", "immediately"],
            "high": [
                "important",
                "deadline",
                "meeting",
                "interview",
                "offer",
                "approval",
            ],
            "medium": ["update", "reminder", "scheduled", "notification"],
            "low": ["newsletter", "promotional", "marketing", "subscribe"],
        }

        # Sender importance (learned from user feedback)
        self.sender_importance: Dict[str, float] = {}

        # Load or initialize model
        self._load_or_initialize_model()

    def predict_priority(self, notification: Notification) -> NotificationPriority:
        """Predict notification priority using ML"""

        # Extract features
        features = self._extract_features(notification)

        # Get ML prediction
        if self.classifier is not None and self.vectorizer is not None:
            try:
                text_features = self.vectorizer.transform([features["text"]])
                ml_score = self.classifier.predict_proba(text_features)[0]
            except Exception as e:
                self.logger.error(f"ML prediction error: {e}")
                ml_score = [0.2, 0.2, 0.3, 0.2, 0.1]  # Default uniform
        else:
            ml_score = [0.2, 0.2, 0.3, 0.2, 0.1]

        # Combine with rule-based features
        final_score = self._combine_scores(features, ml_score)

        # Map to priority
        priority_idx = np.argmax(final_score)
        priorities = [
            NotificationPriority.INFO,
            NotificationPriority.LOW,
            NotificationPriority.MEDIUM,
            NotificationPriority.HIGH,
            NotificationPriority.CRITICAL,
        ]

        return priorities[priority_idx]

    def _extract_features(self, notification: Notification) -> Dict[str, any]:
        """Extract features from notification"""

        text = f"{notification.title} {notification.message}"

        features = {
            "text": text,
            "has_urgent_keywords": self._has_keywords(text, "critical"),
            "has_important_keywords": self._has_keywords(text, "high"),
            "has_medium_keywords": self._has_keywords(text, "medium"),
            "has_low_keywords": self._has_keywords(text, "low"),
            "word_count": len(text.split()),
            "has_action": self._has_action_words(text),
            "has_time_reference": self._has_time_reference(text),
            "sender_importance": self._get_sender_importance(notification),
            "type_score": self._get_type_importance(notification),
        }

        return features

    def _has_keywords(self, text: str, category: str) -> bool:
        """Check if text contains keywords from category"""
        text_lower = text.lower()
        keywords = self.importance_keywords.get(category, [])
        return any(keyword in text_lower for keyword in keywords)

    def _has_action_words(self, text: str) -> bool:
        """Check if text contains action words"""
        action_words = [
            "please",
            "action required",
            "respond",
            "review",
            "approve",
            "confirm",
            "complete",
        ]
        text_lower = text.lower()
        return any(word in text_lower for word in action_words)

    def _has_time_reference(self, text: str) -> bool:
        """Check if text has time urgency"""
        time_patterns = [
            r"\btoday\b",
            r"\btomorrow\b",
            r"\basap\b",
            r"\bdeadline\b",
            r"\bby\s+\d",
            r"\bdue\b",
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in time_patterns)

    def _get_sender_importance(self, notification: Notification) -> float:
        """Get learned sender importance (0-1)"""
        sender = notification.data.get("sender", "unknown")
        return self.sender_importance.get(sender, 0.5)

    def _get_type_importance(self, notification: Notification) -> float:
        """Get notification type base importance"""
        type_scores = {
            "email": 0.5,
            "calendar": 0.8,
            "task": 0.6,
            "github": 0.4,
            "linkedin": 0.3,
            "system": 0.7,
            "ai": 0.5,
            "voice": 0.9,
        }
        return type_scores.get(notification.type.value, 0.5)

    def _combine_scores(self, features: Dict[str, any], ml_score: List[float]) -> List[float]:
        """Combine ML and rule-based scores"""

        # Start with ML score
        combined = np.array(ml_score)

        # Boost critical if urgent keywords
        if features["has_urgent_keywords"]:
            combined[4] += 0.3  # CRITICAL
            combined[3] += 0.2  # HIGH

        # Boost high if important keywords
        if features["has_important_keywords"]:
            combined[3] += 0.2  # HIGH
            combined[2] += 0.1  # MEDIUM

        # Reduce priority if low keywords
        if features["has_low_keywords"]:
            combined[0] += 0.2  # INFO
            combined[1] += 0.1  # LOW

        # Boost if action required
        if features["has_action"]:
            combined[3] += 0.15
            combined[2] += 0.1

        # Boost if time reference
        if features["has_time_reference"]:
            combined[4] += 0.2
            combined[3] += 0.15

        # Apply sender importance
        sender_boost = features["sender_importance"] - 0.5
        combined[3] += sender_boost * 0.3
        combined[2] += sender_boost * 0.2

        # Apply type importance
        type_boost = features["type_score"] - 0.5
        combined[3] += type_boost * 0.2
        combined[2] += type_boost * 0.1

        # Normalize to sum to 1
        combined = np.maximum(combined, 0)  # No negative scores
        total = np.sum(combined)
        if total > 0:
            combined = combined / total

        return combined.tolist()

    def train_from_feedback(self, notifications: List[Notification], labels: List[int]):
        """Train/update model from user feedback"""

        if len(notifications) < 10:
            self.logger.warning("Need at least 10 examples to train")
            return

        # Extract features
        texts = [f"{n.title} {n.message}" for n in notifications]

        # Train vectorizer
        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(
                max_features=100, stop_words="english", ngram_range=(1, 2)
            )
            X = self.vectorizer.fit_transform(texts)
        else:
            X = self.vectorizer.transform(texts)

        # Train classifier
        if self.classifier is None:
            self.classifier = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)

        self.classifier.fit(X, labels)

        # Save model
        self._save_model()

        self.logger.info(f"Model trained on {len(notifications)} examples")

    def update_sender_importance(self, sender: str, importance: float):
        """Update sender importance score"""
        self.sender_importance[sender] = max(0.0, min(1.0, importance))
        self._save_sender_scores()

    def _save_model(self):
        """Save ML model to disk"""
        try:
            model_file = self.model_dir / "notification_classifier.pkl"
            with open(model_file, "wb") as f:
                pickle.dump({"vectorizer": self.vectorizer, "classifier": self.classifier}, f)

            self.logger.info("Model saved")
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")

    def _load_model(self):
        """Load ML model from disk"""
        try:
            model_file = self.model_dir / "notification_classifier.pkl"
            if model_file.exists():
                with open(model_file, "rb") as f:
                    data = pickle.load(f)
                    self.vectorizer = data["vectorizer"]
                    self.classifier = data["classifier"]

                self.logger.info("Model loaded")
                return True
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")

        return False

    def _save_sender_scores(self):
        """Save sender importance scores"""
        try:
            scores_file = self.model_dir / "sender_scores.json"
            with open(scores_file, "w") as f:
                json.dump(self.sender_importance, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving sender scores: {e}")

    def _load_sender_scores(self):
        """Load sender importance scores"""
        try:
            scores_file = self.model_dir / "sender_scores.json"
            if scores_file.exists():
                with open(scores_file, "r") as f:
                    self.sender_importance = json.load(f)

                self.logger.info(f"Loaded {len(self.sender_importance)} sender scores")
        except Exception as e:
            self.logger.error(f"Error loading sender scores: {e}")

    def _load_or_initialize_model(self):
        """Load existing model or initialize new one"""
        if not self._load_model():
            self.logger.info("Initializing new classifier")
            # Will be trained on first feedback

        self._load_sender_scores()

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model"""
        if self.classifier is None:
            return {}

        try:
            importances = self.classifier.feature_importances_
            feature_names = self.vectorizer.get_feature_names_out()

            # Get top 20 features
            top_indices = np.argsort(importances)[-20:]
            return {feature_names[i]: float(importances[i]) for i in top_indices}
        except:
            return {}


# Global classifier instance
_classifier: Optional[NotificationClassifier] = None


def get_classifier() -> NotificationClassifier:
    """Get global notification classifier"""
    global _classifier
    if _classifier is None:
        _classifier = NotificationClassifier()
    return _classifier


def classify_notification(notification: Notification) -> NotificationPriority:
    """Quick function to classify notification"""
    return get_classifier().predict_priority(notification)
