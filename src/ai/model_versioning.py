"""
Model Versioning and Performance Tracking
Manages model versions and tracks performance metrics
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import hashlib
import shutil


@dataclass
class ModelVersion:
    """Model version metadata"""
    version_id: str
    model_name: str
    version_number: int
    created_at: str
    created_by: str
    description: str
    parameters_hash: str
    metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"  # active, deprecated, archived


@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    metric_name: str
    value: float
    timestamp: str
    context: Dict[str, Any] = field(default_factory=dict)


class ModelVersionControl:
    """Manages model versions"""
    
    def __init__(self, repo_dir: str = "data/model_repo"):
        self.repo_dir = repo_dir
        os.makedirs(repo_dir, exist_ok=True)
        
        self.versions: Dict[str, List[ModelVersion]] = {}
        self.load_versions()
    
    def create_version(
        self,
        model_name: str,
        model_data: Any,
        created_by: str,
        description: str,
        metrics: Dict[str, float] = None
    ) -> ModelVersion:
        """Create new model version"""
        if model_name not in self.versions:
            self.versions[model_name] = []
        
        # Generate version number
        version_number = len(self.versions[model_name]) + 1
        
        # Create version ID
        version_id = f"{model_name}_v{version_number}"
        
        # Compute parameters hash
        params_hash = self._hash_model(model_data)
        
        # Create version
        version = ModelVersion(
            version_id=version_id,
            model_name=model_name,
            version_number=version_number,
            created_at=datetime.now().isoformat(),
            created_by=created_by,
            description=description,
            parameters_hash=params_hash,
            metrics=metrics or {}
        )
        
        # Save model data
        self._save_model_data(version_id, model_data)
        
        # Add to versions
        self.versions[model_name].append(version)
        self.save_versions()
        
        return version
    
    def get_version(
        self,
        model_name: str,
        version_number: Optional[int] = None
    ) -> Optional[ModelVersion]:
        """Get specific version (latest if version not specified)"""
        if model_name not in self.versions:
            return None
        
        versions = self.versions[model_name]
        
        if not versions:
            return None
        
        if version_number is None:
            # Return latest active version
            active_versions = [v for v in versions if v.status == "active"]
            return active_versions[-1] if active_versions else None
        else:
            # Return specific version
            for v in versions:
                if v.version_number == version_number:
                    return v
            return None
    
    def list_versions(
        self,
        model_name: str,
        status: Optional[str] = None
    ) -> List[ModelVersion]:
        """List all versions of model"""
        if model_name not in self.versions:
            return []
        
        versions = self.versions[model_name]
        
        if status:
            versions = [v for v in versions if v.status == status]
        
        return sorted(versions, key=lambda v: v.version_number)
    
    def deprecate_version(self, model_name: str, version_number: int):
        """Mark version as deprecated"""
        version = self.get_version(model_name, version_number)
        if version:
            version.status = "deprecated"
            self.save_versions()
    
    def rollback(
        self,
        model_name: str,
        target_version: int
    ) -> Optional[ModelVersion]:
        """Rollback to previous version"""
        version = self.get_version(model_name, target_version)
        
        if not version:
            return None
        
        # Mark all newer versions as deprecated
        for v in self.versions[model_name]:
            if v.version_number > target_version:
                v.status = "deprecated"
        
        # Activate target version
        version.status = "active"
        self.save_versions()
        
        return version
    
    def compare_versions(
        self,
        model_name: str,
        version1: int,
        version2: int
    ) -> Dict[str, Any]:
        """Compare two versions"""
        v1 = self.get_version(model_name, version1)
        v2 = self.get_version(model_name, version2)
        
        if not v1 or not v2:
            return {"error": "Version not found"}
        
        comparison = {
            "version1": {
                "number": v1.version_number,
                "created_at": v1.created_at,
                "metrics": v1.metrics
            },
            "version2": {
                "number": v2.version_number,
                "created_at": v2.created_at,
                "metrics": v2.metrics
            },
            "metric_changes": {}
        }
        
        # Compare metrics
        all_metrics = set(v1.metrics.keys()) | set(v2.metrics.keys())
        
        for metric in all_metrics:
            val1 = v1.metrics.get(metric, 0)
            val2 = v2.metrics.get(metric, 0)
            
            comparison["metric_changes"][metric] = {
                "v1": val1,
                "v2": val2,
                "change": val2 - val1,
                "change_percent": ((val2 - val1) / val1 * 100) if val1 != 0 else 0
            }
        
        return comparison
    
    def _hash_model(self, model_data: Any) -> str:
        """Compute hash of model parameters"""
        # Convert to string and hash
        model_str = str(model_data)
        return hashlib.sha256(model_str.encode()).hexdigest()[:16]
    
    def _save_model_data(self, version_id: str, model_data: Any):
        """Save model data to disk"""
        import pickle
        
        model_file = os.path.join(self.repo_dir, f"{version_id}.pkl")
        
        with open(model_file, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model_data(self, version_id: str) -> Optional[Any]:
        """Load model data from disk"""
        import pickle
        
        model_file = os.path.join(self.repo_dir, f"{version_id}.pkl")
        
        if not os.path.exists(model_file):
            return None
        
        with open(model_file, 'rb') as f:
            return pickle.load(f)
    
    def save_versions(self):
        """Save version metadata"""
        versions_file = os.path.join(self.repo_dir, "versions.json")
        
        data = {}
        for model_name, versions in self.versions.items():
            data[model_name] = [
                {
                    "version_id": v.version_id,
                    "model_name": v.model_name,
                    "version_number": v.version_number,
                    "created_at": v.created_at,
                    "created_by": v.created_by,
                    "description": v.description,
                    "parameters_hash": v.parameters_hash,
                    "metrics": v.metrics,
                    "metadata": v.metadata,
                    "status": v.status
                }
                for v in versions
            ]
        
        with open(versions_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_versions(self):
        """Load version metadata"""
        versions_file = os.path.join(self.repo_dir, "versions.json")
        
        if not os.path.exists(versions_file):
            return
        
        with open(versions_file, 'r') as f:
            data = json.load(f)
        
        for model_name, versions in data.items():
            self.versions[model_name] = [
                ModelVersion(**v)
                for v in versions
            ]


class PerformanceTracker:
    """Tracks model performance over time"""
    
    def __init__(self, tracking_dir: str = "data/performance"):
        self.tracking_dir = tracking_dir
        os.makedirs(tracking_dir, exist_ok=True)
        
        self.metrics: Dict[str, List[PerformanceMetric]] = {}
        self.load_metrics()
    
    def record_metric(
        self,
        model_name: str,
        metric_name: str,
        value: float,
        context: Dict[str, Any] = None
    ):
        """Record performance metric"""
        key = f"{model_name}_{metric_name}"
        
        if key not in self.metrics:
            self.metrics[key] = []
        
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now().isoformat(),
            context=context or {}
        )
        
        self.metrics[key].append(metric)
        
        # Keep only last 1000 metrics
        if len(self.metrics[key]) > 1000:
            self.metrics[key] = self.metrics[key][-1000:]
        
        self.save_metrics()
    
    def get_metric_history(
        self,
        model_name: str,
        metric_name: str,
        limit: int = 100
    ) -> List[PerformanceMetric]:
        """Get metric history"""
        key = f"{model_name}_{metric_name}"
        
        if key not in self.metrics:
            return []
        
        return self.metrics[key][-limit:]
    
    def get_metric_statistics(
        self,
        model_name: str,
        metric_name: str
    ) -> Dict[str, float]:
        """Get metric statistics"""
        history = self.get_metric_history(model_name, metric_name, limit=1000)
        
        if not history:
            return {}
        
        values = [m.value for m in history]
        
        import numpy as np
        
        return {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "median": np.median(values),
            "count": len(values)
        }
    
    def get_trend(
        self,
        model_name: str,
        metric_name: str,
        window: int = 10
    ) -> str:
        """Get metric trend (improving, degrading, stable)"""
        history = self.get_metric_history(model_name, metric_name, limit=100)
        
        if len(history) < window * 2:
            return "insufficient_data"
        
        recent = [m.value for m in history[-window:]]
        previous = [m.value for m in history[-window*2:-window]]
        
        import numpy as np
        
        recent_mean = np.mean(recent)
        previous_mean = np.mean(previous)
        
        # Calculate percent change
        change = (recent_mean - previous_mean) / previous_mean * 100
        
        if change > 5:
            return "improving"
        elif change < -5:
            return "degrading"
        else:
            return "stable"
    
    def save_metrics(self):
        """Save metrics to disk"""
        metrics_file = os.path.join(self.tracking_dir, "metrics.json")
        
        data = {}
        for key, metrics in self.metrics.items():
            data[key] = [
                {
                    "metric_name": m.metric_name,
                    "value": m.value,
                    "timestamp": m.timestamp,
                    "context": m.context
                }
                for m in metrics
            ]
        
        with open(metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_metrics(self):
        """Load metrics from disk"""
        metrics_file = os.path.join(self.tracking_dir, "metrics.json")
        
        if not os.path.exists(metrics_file):
            return
        
        with open(metrics_file, 'r') as f:
            data = json.load(f)
        
        for key, metrics in data.items():
            self.metrics[key] = [
                PerformanceMetric(**m)
                for m in metrics
            ]


class ABTestingManager:
    """Manages A/B testing of model versions"""
    
    def __init__(self):
        self.active_tests: Dict[str, Dict[str, Any]] = {}
        self.test_results: Dict[str, List[Dict[str, Any]]] = {}
    
    def create_test(
        self,
        test_name: str,
        model_a: str,
        model_b: str,
        traffic_split: float = 0.5,
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """Create A/B test"""
        test = {
            "test_name": test_name,
            "model_a": model_a,
            "model_b": model_b,
            "traffic_split": traffic_split,
            "metrics": metrics or ["accuracy", "latency"],
            "started_at": datetime.now().isoformat(),
            "status": "running",
            "results_a": [],
            "results_b": []
        }
        
        self.active_tests[test_name] = test
        
        return test
    
    def assign_variant(self, test_name: str, user_id: str) -> str:
        """Assign user to test variant"""
        if test_name not in self.active_tests:
            return "control"
        
        test = self.active_tests[test_name]
        
        # Use hash of user_id for consistent assignment (not for security)
        # Using SHA256 for better collision resistance
        hash_value = int(hashlib.sha256(user_id.encode()).hexdigest()[:16], 16)
        
        if (hash_value % 100) < (test["traffic_split"] * 100):
            return "variant_a"
        else:
            return "variant_b"
    
    def record_result(
        self,
        test_name: str,
        variant: str,
        metrics: Dict[str, float]
    ):
        """Record test result"""
        if test_name not in self.active_tests:
            return
        
        test = self.active_tests[test_name]
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        if variant == "variant_a":
            test["results_a"].append(result)
        else:
            test["results_b"].append(result)
    
    def analyze_test(self, test_name: str) -> Dict[str, Any]:
        """Analyze A/B test results"""
        if test_name not in self.active_tests:
            return {"error": "Test not found"}
        
        test = self.active_tests[test_name]
        
        results_a = test["results_a"]
        results_b = test["results_b"]
        
        if not results_a or not results_b:
            return {"error": "Insufficient data"}
        
        import numpy as np
        
        analysis = {
            "test_name": test_name,
            "sample_size_a": len(results_a),
            "sample_size_b": len(results_b),
            "metrics": {}
        }
        
        # Analyze each metric
        for metric_name in test["metrics"]:
            values_a = [r["metrics"].get(metric_name, 0) for r in results_a]
            values_b = [r["metrics"].get(metric_name, 0) for r in results_b]
            
            mean_a = np.mean(values_a)
            mean_b = np.mean(values_b)
            
            analysis["metrics"][metric_name] = {
                "variant_a_mean": mean_a,
                "variant_b_mean": mean_b,
                "difference": mean_b - mean_a,
                "percent_change": ((mean_b - mean_a) / mean_a * 100) if mean_a != 0 else 0,
                "winner": "variant_b" if mean_b > mean_a else "variant_a"
            }
        
        return analysis
    
    def end_test(self, test_name: str, winner: str):
        """End A/B test and declare winner"""
        if test_name in self.active_tests:
            test = self.active_tests[test_name]
            test["status"] = "completed"
            test["ended_at"] = datetime.now().isoformat()
            test["winner"] = winner
            
            # Archive test results
            if test_name not in self.test_results:
                self.test_results[test_name] = []
            
            self.test_results[test_name].append(test)
            del self.active_tests[test_name]
