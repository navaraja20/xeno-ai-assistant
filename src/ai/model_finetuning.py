"""
AI Model Fine-tuning System for XENO
Enables personalized AI responses through custom model training
"""

import json
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import pickle


@dataclass
class TrainingExample:
    """Single training example"""
    input_text: str
    output_text: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    user_rating: Optional[int] = None  # 1-5 rating


@dataclass
class FineTuneConfig:
    """Fine-tuning configuration"""
    model_name: str
    base_model: str = "gpt-3.5-turbo"
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 10
    validation_split: float = 0.2
    min_examples: int = 50


class PersonalizationEngine:
    """Learns user preferences and communication style"""
    
    def __init__(self, user_id: str, data_dir: str = "data/personalization"):
        self.user_id = user_id
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.user_dir = os.path.join(data_dir, user_id)
        os.makedirs(self.user_dir, exist_ok=True)
        
        # User preferences
        self.preferences: Dict[str, Any] = {
            "communication_style": "professional",  # casual, professional, friendly
            "detail_level": "medium",  # brief, medium, detailed
            "response_format": "conversational",  # conversational, structured, bullet-points
            "tone": "neutral",  # formal, neutral, friendly, humorous
            "preferred_time_format": "12h",  # 12h, 24h
            "timezone": "UTC",
            "language": "en",
            "expertise_level": {}  # topic: level (beginner, intermediate, expert)
        }
        
        # Load existing preferences
        self.load_preferences()
        
        # Interaction history for learning
        self.interactions: List[Dict[str, Any]] = []
        self.load_interactions()
    
    def update_preference(self, key: str, value: Any):
        """Update user preference"""
        if "." in key:
            # Handle nested keys like "expertise_level.python"
            parts = key.split(".")
            current = self.preferences
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            self.preferences[key] = value
        
        self.save_preferences()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        if "." in key:
            parts = key.split(".")
            current = self.preferences
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return default
            return current if current is not None else default
        else:
            return self.preferences.get(key, default)
    
    def record_interaction(
        self,
        query: str,
        response: str,
        context: Dict[str, Any],
        user_feedback: Optional[int] = None
    ):
        """Record user interaction for learning"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "context": context,
            "feedback": user_feedback
        }
        
        self.interactions.append(interaction)
        
        # Keep only last 1000 interactions
        if len(self.interactions) > 1000:
            self.interactions = self.interactions[-1000:]
        
        self.save_interactions()
        
        # Learn from interaction
        self.learn_from_interaction(interaction)
    
    def learn_from_interaction(self, interaction: Dict[str, Any]):
        """Learn preferences from interaction"""
        query = interaction["query"].lower()
        feedback = interaction.get("feedback")
        
        # Learn communication style from user's query
        if any(word in query for word in ["brief", "short", "quick", "summary"]):
            self.update_preference("detail_level", "brief")
        elif any(word in query for word in ["detailed", "explain", "elaborate"]):
            self.update_preference("detail_level", "detailed")
        
        # Learn from feedback
        if feedback and feedback >= 4:
            # Good feedback - reinforce current settings
            pass
        elif feedback and feedback <= 2:
            # Bad feedback - maybe adjust style
            # This would be more sophisticated in production
            pass
    
    def get_personalized_prompt_prefix(self) -> str:
        """Generate personalized prompt prefix based on preferences"""
        style = self.get_preference("communication_style")
        detail = self.get_preference("detail_level")
        tone = self.get_preference("tone")
        format_pref = self.get_preference("response_format")
        
        prefix = f"Respond in a {tone} tone with a {style} style. "
        
        if detail == "brief":
            prefix += "Keep responses concise and to the point. "
        elif detail == "detailed":
            prefix += "Provide detailed explanations with examples. "
        
        if format_pref == "structured":
            prefix += "Use clear structure with headings and sections. "
        elif format_pref == "bullet-points":
            prefix += "Use bullet points and numbered lists. "
        
        return prefix
    
    def analyze_expertise_level(self, topic: str) -> str:
        """Analyze user's expertise level in topic"""
        # Look at past interactions about this topic
        topic_interactions = [
            i for i in self.interactions
            if topic.lower() in i["query"].lower()
        ]
        
        if not topic_interactions:
            return "beginner"
        
        # Simple heuristic: if user asks basic questions, they're a beginner
        basic_keywords = ["what is", "how to", "explain", "tutorial", "guide"]
        advanced_keywords = ["optimize", "advanced", "architecture", "best practices"]
        
        basic_count = sum(
            1 for i in topic_interactions
            if any(kw in i["query"].lower() for kw in basic_keywords)
        )
        advanced_count = sum(
            1 for i in topic_interactions
            if any(kw in i["query"].lower() for kw in advanced_keywords)
        )
        
        if advanced_count > basic_count:
            return "advanced"
        elif basic_count > advanced_count * 2:
            return "beginner"
        else:
            return "intermediate"
    
    def save_preferences(self):
        """Save preferences to disk"""
        prefs_file = os.path.join(self.user_dir, "preferences.json")
        with open(prefs_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)
    
    def load_preferences(self):
        """Load preferences from disk"""
        prefs_file = os.path.join(self.user_dir, "preferences.json")
        if os.path.exists(prefs_file):
            with open(prefs_file, 'r') as f:
                loaded_prefs = json.load(f)
                self.preferences.update(loaded_prefs)
    
    def save_interactions(self):
        """Save interactions to disk"""
        interactions_file = os.path.join(self.user_dir, "interactions.json")
        with open(interactions_file, 'w') as f:
            json.dump(self.interactions, f, indent=2)
    
    def load_interactions(self):
        """Load interactions from disk"""
        interactions_file = os.path.join(self.user_dir, "interactions.json")
        if os.path.exists(interactions_file):
            with open(interactions_file, 'r') as f:
                self.interactions = json.load(f)


class CustomModelTrainer:
    """Trains custom models on user data"""
    
    def __init__(self, user_id: str, models_dir: str = "data/models"):
        self.user_id = user_id
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        
        self.user_models_dir = os.path.join(models_dir, user_id)
        os.makedirs(self.user_models_dir, exist_ok=True)
        
        self.training_data: List[TrainingExample] = []
        self.models: Dict[str, Any] = {}
    
    def add_training_example(
        self,
        input_text: str,
        output_text: str,
        context: Dict[str, Any],
        rating: Optional[int] = None
    ):
        """Add training example"""
        example = TrainingExample(
            input_text=input_text,
            output_text=output_text,
            context=context,
            user_rating=rating
        )
        
        self.training_data.append(example)
        self.save_training_data()
    
    def train_intent_classifier(self) -> Dict[str, Any]:
        """Train custom intent classifier"""
        if len(self.training_data) < 50:
            return {
                "success": False,
                "error": "Need at least 50 training examples",
                "current_count": len(self.training_data)
            }
        
        # Prepare data
        texts = [ex.input_text for ex in self.training_data]
        labels = [ex.context.get("intent", "unknown") for ex in self.training_data]
        
        # Vectorize text
        vectorizer = TfidfVectorizer(max_features=1000)
        X = vectorizer.fit_transform(texts)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42
        )
        
        # Train classifier
        classifier = MultinomialNB()
        classifier.fit(X_train, y_train)
        
        # Evaluate
        accuracy = classifier.score(X_test, y_test)
        
        # Save model
        model_data = {
            "vectorizer": vectorizer,
            "classifier": classifier,
            "accuracy": accuracy,
            "trained_at": datetime.now().isoformat()
        }
        
        self.models["intent_classifier"] = model_data
        self.save_model("intent_classifier", model_data)
        
        return {
            "success": True,
            "accuracy": accuracy,
            "examples_used": len(self.training_data)
        }
    
    def predict_intent(self, text: str) -> Optional[str]:
        """Predict intent using custom classifier"""
        if "intent_classifier" not in self.models:
            self.load_model("intent_classifier")
        
        if "intent_classifier" not in self.models:
            return None
        
        model_data = self.models["intent_classifier"]
        vectorizer = model_data["vectorizer"]
        classifier = model_data["classifier"]
        
        X = vectorizer.transform([text])
        prediction = classifier.predict(X)[0]
        
        return prediction
    
    def train_response_generator(self) -> Dict[str, Any]:
        """Train response generation model"""
        # In production, this would fine-tune a transformer model
        # For now, we'll create a simple template-based system
        
        if len(self.training_data) < 100:
            return {
                "success": False,
                "error": "Need at least 100 training examples"
            }
        
        # Group examples by intent
        intent_templates: Dict[str, List[str]] = {}
        
        for example in self.training_data:
            intent = example.context.get("intent", "general")
            if intent not in intent_templates:
                intent_templates[intent] = []
            intent_templates[intent].append(example.output_text)
        
        # Save templates
        model_data = {
            "templates": intent_templates,
            "trained_at": datetime.now().isoformat()
        }
        
        self.models["response_generator"] = model_data
        self.save_model("response_generator", model_data)
        
        return {
            "success": True,
            "intents_learned": len(intent_templates),
            "examples_used": len(self.training_data)
        }
    
    def generate_response(self, intent: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate response using trained model"""
        if "response_generator" not in self.models:
            self.load_model("response_generator")
        
        if "response_generator" not in self.models:
            return None
        
        templates = self.models["response_generator"]["templates"]
        
        if intent not in templates:
            return None
        
        # Select most appropriate template (simple random for now)
        import random
        template = random.choice(templates[intent])
        
        # Fill in context variables
        for key, value in context.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        return template
    
    def save_training_data(self):
        """Save training data to disk"""
        data_file = os.path.join(self.user_models_dir, "training_data.json")
        
        data = [
            {
                "input_text": ex.input_text,
                "output_text": ex.output_text,
                "context": ex.context,
                "timestamp": ex.timestamp,
                "user_rating": ex.user_rating
            }
            for ex in self.training_data
        ]
        
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_training_data(self):
        """Load training data from disk"""
        data_file = os.path.join(self.user_models_dir, "training_data.json")
        
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            self.training_data = [
                TrainingExample(**example)
                for example in data
            ]
    
    def save_model(self, model_name: str, model_data: Any):
        """Save model to disk"""
        model_file = os.path.join(self.user_models_dir, f"{model_name}.pkl")
        
        with open(model_file, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, model_name: str):
        """Load model from disk"""
        model_file = os.path.join(self.user_models_dir, f"{model_name}.pkl")
        
        if os.path.exists(model_file):
            with open(model_file, 'rb') as f:
                self.models[model_name] = pickle.load(f)


class ContextualMemory:
    """Maintains long-term memory of user context"""
    
    def __init__(self, user_id: str, memory_dir: str = "data/memory"):
        self.user_id = user_id
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        
        self.user_memory_dir = os.path.join(memory_dir, user_id)
        os.makedirs(self.user_memory_dir, exist_ok=True)
        
        # Different types of memory
        self.semantic_memory: Dict[str, Any] = {}  # Facts about user
        self.episodic_memory: List[Dict[str, Any]] = []  # Past events
        self.procedural_memory: Dict[str, Any] = {}  # User's workflows
        
        self.load_memory()
    
    def store_fact(self, category: str, key: str, value: Any):
        """Store fact in semantic memory"""
        if category not in self.semantic_memory:
            self.semantic_memory[category] = {}
        
        self.semantic_memory[category][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "confidence": 1.0
        }
        
        self.save_memory()
    
    def retrieve_fact(self, category: str, key: str) -> Optional[Any]:
        """Retrieve fact from semantic memory"""
        if category in self.semantic_memory:
            fact_data = self.semantic_memory[category].get(key)
            if fact_data:
                return fact_data["value"]
        return None
    
    def store_episode(
        self,
        event_type: str,
        description: str,
        context: Dict[str, Any]
    ):
        """Store episode in episodic memory"""
        episode = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description,
            "context": context
        }
        
        self.episodic_memory.append(episode)
        
        # Keep only last 500 episodes
        if len(self.episodic_memory) > 500:
            self.episodic_memory = self.episodic_memory[-500:]
        
        self.save_memory()
    
    def retrieve_episodes(
        self,
        event_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve episodes from memory"""
        episodes = self.episodic_memory
        
        if event_type:
            episodes = [e for e in episodes if e["event_type"] == event_type]
        
        return episodes[-limit:]
    
    def store_workflow(self, workflow_name: str, steps: List[str]):
        """Store user workflow in procedural memory"""
        self.procedural_memory[workflow_name] = {
            "steps": steps,
            "created_at": datetime.now().isoformat(),
            "use_count": 0
        }
        
        self.save_memory()
    
    def retrieve_workflow(self, workflow_name: str) -> Optional[List[str]]:
        """Retrieve workflow steps"""
        workflow = self.procedural_memory.get(workflow_name)
        if workflow:
            workflow["use_count"] += 1
            self.save_memory()
            return workflow["steps"]
        return None
    
    def save_memory(self):
        """Save all memory to disk"""
        memory_file = os.path.join(self.user_memory_dir, "memory.json")
        
        memory_data = {
            "semantic": self.semantic_memory,
            "episodic": self.episodic_memory,
            "procedural": self.procedural_memory
        }
        
        with open(memory_file, 'w') as f:
            json.dump(memory_data, f, indent=2)
    
    def load_memory(self):
        """Load memory from disk"""
        memory_file = os.path.join(self.user_memory_dir, "memory.json")
        
        if os.path.exists(memory_file):
            with open(memory_file, 'r') as f:
                memory_data = json.load(f)
            
            self.semantic_memory = memory_data.get("semantic", {})
            self.episodic_memory = memory_data.get("episodic", [])
            self.procedural_memory = memory_data.get("procedural", {})
