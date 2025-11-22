"""
Federated Learning for Privacy-Preserving AI Training
Enables model training without sending raw data to server
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
import hashlib
from dataclasses import dataclass, field


@dataclass
class ModelUpdate:
    """Represents a local model update"""
    model_id: str
    user_id: str
    gradients: Dict[str, np.ndarray]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class DifferentialPrivacy:
    """Implements differential privacy for model updates"""
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.epsilon = epsilon  # Privacy budget
        self.delta = delta  # Privacy parameter
    
    def add_noise(self, data: np.ndarray, sensitivity: float = 1.0) -> np.ndarray:
        """Add Laplace noise for differential privacy"""
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale, data.shape)
        return data + noise
    
    def clip_gradients(
        self,
        gradients: Dict[str, np.ndarray],
        max_norm: float = 1.0
    ) -> Dict[str, np.ndarray]:
        """Clip gradients to bound sensitivity"""
        clipped = {}
        
        for key, grad in gradients.items():
            norm = np.linalg.norm(grad)
            if norm > max_norm:
                clipped[key] = grad * (max_norm / norm)
            else:
                clipped[key] = grad.copy()
        
        return clipped


class SecureAggregation:
    """Secure aggregation of model updates"""
    
    def __init__(self):
        self.pending_updates: Dict[str, List[ModelUpdate]] = {}
    
    def add_update(self, update: ModelUpdate):
        """Add model update for aggregation"""
        model_id = update.model_id
        
        if model_id not in self.pending_updates:
            self.pending_updates[model_id] = []
        
        self.pending_updates[model_id].append(update)
    
    def aggregate_updates(
        self,
        model_id: str,
        min_updates: int = 5
    ) -> Optional[Dict[str, np.ndarray]]:
        """Aggregate updates using secure averaging"""
        if model_id not in self.pending_updates:
            return None
        
        updates = self.pending_updates[model_id]
        
        if len(updates) < min_updates:
            return None
        
        # Average gradients across all users
        aggregated = {}
        gradient_keys = updates[0].gradients.keys()
        
        for key in gradient_keys:
            gradients = [u.gradients[key] for u in updates]
            aggregated[key] = np.mean(gradients, axis=0)
        
        # Clear processed updates
        self.pending_updates[model_id] = []
        
        return aggregated
    
    def get_update_count(self, model_id: str) -> int:
        """Get number of pending updates for model"""
        return len(self.pending_updates.get(model_id, []))


class FederatedTrainer:
    """Manages federated learning process"""
    
    def __init__(
        self,
        model_id: str,
        privacy_enabled: bool = True,
        epsilon: float = 1.0
    ):
        self.model_id = model_id
        self.privacy_enabled = privacy_enabled
        
        # Components
        self.differential_privacy = DifferentialPrivacy(epsilon=epsilon)
        self.secure_aggregation = SecureAggregation()
        
        # Model state
        self.global_model: Dict[str, np.ndarray] = {}
        self.version = 0
        self.training_rounds = 0
        
        # Statistics
        self.stats = {
            "total_updates": 0,
            "total_users": set(),
            "training_history": []
        }
    
    def initialize_model(self, model_params: Dict[str, np.ndarray]):
        """Initialize global model"""
        self.global_model = model_params.copy()
        self.version = 1
    
    def get_global_model(self) -> Dict[str, Any]:
        """Get current global model"""
        return {
            "model_id": self.model_id,
            "version": self.version,
            "parameters": self.global_model,
            "timestamp": datetime.now().isoformat()
        }
    
    def submit_local_update(
        self,
        user_id: str,
        local_gradients: Dict[str, np.ndarray],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit local model update"""
        # Apply privacy if enabled
        if self.privacy_enabled:
            local_gradients = self.differential_privacy.clip_gradients(
                local_gradients,
                max_norm=1.0
            )
            
            # Add noise to gradients
            noisy_gradients = {}
            for key, grad in local_gradients.items():
                noisy_gradients[key] = self.differential_privacy.add_noise(grad)
            
            local_gradients = noisy_gradients
        
        # Create update
        update = ModelUpdate(
            model_id=self.model_id,
            user_id=user_id,
            gradients=local_gradients,
            metadata=metadata
        )
        
        # Add to aggregation
        self.secure_aggregation.add_update(update)
        
        # Update stats
        self.stats["total_updates"] += 1
        self.stats["total_users"].add(user_id)
        
        return {
            "success": True,
            "pending_updates": self.secure_aggregation.get_update_count(self.model_id),
            "privacy_enabled": self.privacy_enabled
        }
    
    def aggregate_and_update(self, min_updates: int = 5) -> Dict[str, Any]:
        """Aggregate updates and update global model"""
        aggregated = self.secure_aggregation.aggregate_updates(
            self.model_id,
            min_updates=min_updates
        )
        
        if aggregated is None:
            return {
                "success": False,
                "reason": "Not enough updates",
                "pending_updates": self.secure_aggregation.get_update_count(self.model_id)
            }
        
        # Update global model
        learning_rate = 0.1
        
        for key in self.global_model.keys():
            if key in aggregated:
                self.global_model[key] -= learning_rate * aggregated[key]
        
        self.version += 1
        self.training_rounds += 1
        
        # Record history
        self.stats["training_history"].append({
            "round": self.training_rounds,
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "updates_used": min_updates
        })
        
        return {
            "success": True,
            "new_version": self.version,
            "round": self.training_rounds,
            "model_updated": True
        }


class PersonalizedModelManager:
    """Manages personalized models for users"""
    
    def __init__(self, data_dir: str = "data/federated"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.trainers: Dict[str, FederatedTrainer] = {}
        self.user_models: Dict[str, Dict[str, Any]] = {}
    
    def create_model(
        self,
        model_id: str,
        base_params: Dict[str, np.ndarray],
        privacy_enabled: bool = True
    ) -> str:
        """Create new federated model"""
        trainer = FederatedTrainer(
            model_id=model_id,
            privacy_enabled=privacy_enabled
        )
        
        trainer.initialize_model(base_params)
        self.trainers[model_id] = trainer
        
        return model_id
    
    def train_local_model(
        self,
        user_id: str,
        model_id: str,
        local_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Train model locally on user data"""
        if model_id not in self.trainers:
            return {"success": False, "error": "Model not found"}
        
        # Simulate local training
        # In production, this would be actual gradient computation
        local_gradients = self._compute_local_gradients(local_data)
        
        # Submit update
        trainer = self.trainers[model_id]
        result = trainer.submit_local_update(
            user_id=user_id,
            local_gradients=local_gradients,
            metadata={
                "data_points": len(local_data),
                "client_version": "1.0"
            }
        )
        
        return result
    
    def _compute_local_gradients(
        self,
        local_data: List[Dict[str, Any]]
    ) -> Dict[str, np.ndarray]:
        """Compute gradients from local data"""
        # Simplified gradient computation
        # In production, this would use actual model training
        
        gradients = {
            "layer1_weights": np.random.randn(10, 10) * 0.01,
            "layer1_bias": np.random.randn(10) * 0.01,
            "layer2_weights": np.random.randn(10, 5) * 0.01,
            "layer2_bias": np.random.randn(5) * 0.01
        }
        
        return gradients
    
    def get_personalized_model(
        self,
        user_id: str,
        model_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get personalized model for user"""
        key = f"{user_id}_{model_id}"
        
        if key in self.user_models:
            return self.user_models[key]
        
        # If no personalized model, return global model
        if model_id in self.trainers:
            return self.trainers[model_id].get_global_model()
        
        return None
    
    def update_global_model(
        self,
        model_id: str,
        min_updates: int = 5
    ) -> Dict[str, Any]:
        """Update global model with aggregated updates"""
        if model_id not in self.trainers:
            return {"success": False, "error": "Model not found"}
        
        trainer = self.trainers[model_id]
        result = trainer.aggregate_and_update(min_updates=min_updates)
        
        return result


class PrivacyAnalyzer:
    """Analyzes privacy guarantees"""
    
    def __init__(self):
        self.privacy_log: List[Dict[str, Any]] = []
    
    def compute_privacy_budget(
        self,
        epsilon: float,
        num_queries: int
    ) -> Dict[str, Any]:
        """Compute remaining privacy budget"""
        # Using composition theorem for differential privacy
        total_epsilon = epsilon * np.sqrt(2 * num_queries * np.log(1/1e-5))
        
        return {
            "per_query_epsilon": epsilon,
            "total_queries": num_queries,
            "total_epsilon": total_epsilon,
            "privacy_guarantee": "differential_privacy"
        }
    
    def log_privacy_operation(
        self,
        operation: str,
        epsilon_used: float,
        data_accessed: int
    ):
        """Log privacy-sensitive operation"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "epsilon_used": epsilon_used,
            "data_accessed": data_accessed
        }
        
        self.privacy_log.append(entry)
    
    def get_privacy_report(self) -> Dict[str, Any]:
        """Generate privacy report"""
        total_epsilon = sum(e["epsilon_used"] for e in self.privacy_log)
        
        return {
            "total_operations": len(self.privacy_log),
            "total_epsilon_used": total_epsilon,
            "operations": self.privacy_log[-10:],  # Last 10 operations
            "privacy_status": "strong" if total_epsilon < 1.0 else "moderate"
        }
