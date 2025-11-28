# AI Model Fine-tuning & Personalization

## Overview

The AI Model Fine-tuning system enables XENO to learn from user interactions and provide personalized responses. It implements privacy-preserving federated learning, allowing model training without sending raw data to servers.

## Features

### 1. Personalization Engine
- **Communication Style Learning**: Automatically adapts to user preferences (professional, casual, friendly, technical)
- **Detail Level Adjustment**: Learns optimal response length (brief, medium, detailed)
- **Tone Customization**: Matches user's preferred tone (formal, neutral, friendly, humorous)
- **Expertise Detection**: Analyzes user's knowledge level per topic
- **Context Memory**: Maintains long-term memory of user context

### 2. Custom Model Training
- **Intent Classification**: Trains custom intent classifiers on user data
- **Response Generation**: Fine-tunes response templates for personalization
- **Incremental Learning**: Continuously improves from user interactions
- **A/B Testing**: Tests different model variants for optimization

### 3. Federated Learning
- **Privacy-Preserving**: Trains models locally without sending raw data
- **Differential Privacy**: Adds noise to gradients for privacy protection
- **Secure Aggregation**: Aggregates model updates from multiple users securely
- **Local Training**: Keeps sensitive data on user's device

### 4. Model Versioning
- **Version Control**: Tracks all model versions with metadata
- **Performance Metrics**: Records accuracy, latency, user satisfaction
- **Rollback Support**: Can revert to previous versions if needed
- **Version Comparison**: Compares metrics between versions

### 5. Performance Tracking
- **Real-time Metrics**: Tracks accuracy, latency, quality, satisfaction
- **Trend Analysis**: Identifies improving, degrading, or stable metrics
- **A/B Testing**: Compares variant performance scientifically
- **Historical Data**: Maintains performance history for analysis

## Architecture

### Components

```
src/ai/
├── model_finetuning.py       # Main personalization engine
├── federated_learning.py      # Privacy-preserving training
└── model_versioning.py        # Version control & performance

src/ui/
└── model_finetuning_ui.py     # PyQt6 interface
```

### Data Flow

```
User Interaction
    ↓
Personalization Engine (learns preferences)
    ↓
Custom Model Trainer (trains locally)
    ↓
Federated Trainer (privacy-preserving aggregation)
    ↓
Model Version Control (version management)
    ↓
Performance Tracker (metrics & optimization)
```

## Usage

### Personalization Engine

```python
from src.ai.model_finetuning import PersonalizationEngine

# Initialize for user
engine = PersonalizationEngine(user_id="john_doe")

# Update preferences
engine.update_preference("communication_style", "professional")
engine.update_preference("detail_level", "detailed")
engine.update_preference("expertise_level.python", "advanced")

# Get personalized prompt prefix
prefix = engine.get_personalized_prompt_prefix()
# "Respond in a neutral tone with a professional style.
#  Provide detailed explanations with examples."

# Record interaction for learning
engine.record_interaction(
    query="How do I optimize database queries?",
    response="To optimize database queries...",
    context={"topic": "database", "intent": "optimization"},
    user_feedback=5  # 1-5 rating
)

# Analyze expertise
level = engine.analyze_expertise_level("python")
# Returns: "advanced"
```

### Custom Model Training

```python
from src.ai.model_finetuning import CustomModelTrainer

# Initialize trainer
trainer = CustomModelTrainer(user_id="john_doe")

# Add training examples
trainer.add_training_example(
    input_text="Schedule a meeting with team",
    output_text="I'll schedule a meeting. What time works best?",
    context={"intent": "schedule_meeting"},
    rating=5
)

# Train intent classifier
result = trainer.train_intent_classifier()
# {
#     "success": True,
#     "accuracy": 0.95,
#     "examples_used": 150
# }

# Predict intent
intent = trainer.predict_intent("Set up a call with Sarah")
# Returns: "schedule_meeting"
```

### Federated Learning

```python
from src.ai.federated_learning import FederatedTrainer, PersonalizedModelManager

# Create federated model
manager = PersonalizedModelManager()

model_id = manager.create_model(
    model_id="response_model_v1",
    base_params=base_model_weights,
    privacy_enabled=True  # Enable differential privacy
)

# Train locally on user data
result = manager.train_local_model(
    user_id="john_doe",
    model_id=model_id,
    local_data=user_interactions
)
# {
#     "success": True,
#     "pending_updates": 4,
#     "privacy_enabled": True
# }

# Aggregate updates (server-side, when 5+ users contributed)
result = manager.update_global_model(
    model_id=model_id,
    min_updates=5
)
# {
#     "success": True,
#     "new_version": 2,
#     "round": 1,
#     "model_updated": True
# }
```

### Model Versioning

```python
from src.ai.model_versioning import ModelVersionControl, PerformanceTracker

# Initialize version control
vcs = ModelVersionControl()

# Create new version
version = vcs.create_version(
    model_name="intent_classifier",
    model_data=trained_model,
    created_by="john_doe",
    description="Improved accuracy with 200 more examples",
    metrics={"accuracy": 0.95, "latency": 0.12}
)

# Get latest version
latest = vcs.get_version("intent_classifier")

# Rollback to previous version
vcs.rollback("intent_classifier", target_version=2)

# Compare versions
comparison = vcs.compare_versions("intent_classifier", 2, 3)
# {
#     "metric_changes": {
#         "accuracy": {
#             "v1": 0.92,
#             "v2": 0.95,
#             "change": 0.03,
#             "change_percent": 3.26
#         }
#     }
# }

# Track performance
tracker = PerformanceTracker()

tracker.record_metric(
    model_name="intent_classifier",
    metric_name="accuracy",
    value=0.95,
    context={"dataset": "production"}
)

# Get trend
trend = tracker.get_trend("intent_classifier", "accuracy")
# Returns: "improving", "degrading", or "stable"
```

### Contextual Memory

```python
from src.ai.model_finetuning import ContextualMemory

# Initialize memory
memory = ContextualMemory(user_id="john_doe")

# Store facts (semantic memory)
memory.store_fact("preferences", "favorite_language", "Python")
memory.store_fact("work", "role", "Senior Developer")

# Retrieve facts
language = memory.retrieve_fact("preferences", "favorite_language")
# Returns: "Python"

# Store episodes (episodic memory)
memory.store_episode(
    event_type="meeting",
    description="Weekly team standup",
    context={"attendees": ["Alice", "Bob"], "duration": "30min"}
)

# Retrieve episodes
recent_meetings = memory.retrieve_episodes(
    event_type="meeting",
    limit=5
)

# Store workflows (procedural memory)
memory.store_workflow(
    "morning_routine",
    [
        "Check email",
        "Review calendar",
        "Read news",
        "Plan day"
    ]
)

# Retrieve workflow
routine = memory.retrieve_workflow("morning_routine")
# Returns: ["Check email", "Review calendar", ...]
```

### A/B Testing

```python
from src.ai.model_versioning import ABTestingManager

# Initialize A/B testing
ab_manager = ABTestingManager()

# Create test
test = ab_manager.create_test(
    test_name="response_style_test",
    model_a="professional_v1",
    model_b="friendly_v1",
    traffic_split=0.5,  # 50/50 split
    metrics=["user_satisfaction", "engagement"]
)

# Assign user to variant
variant = ab_manager.assign_variant("response_style_test", "john_doe")
# Returns: "variant_a" or "variant_b" (consistent for same user)

# Record results
ab_manager.record_result(
    test_name="response_style_test",
    variant="variant_a",
    metrics={"user_satisfaction": 4.2, "engagement": 0.85}
)

# Analyze test
analysis = ab_manager.analyze_test("response_style_test")
# {
#     "metrics": {
#         "user_satisfaction": {
#             "variant_a_mean": 4.2,
#             "variant_b_mean": 4.5,
#             "difference": 0.3,
#             "percent_change": 7.14,
#             "winner": "variant_b"
#         }
#     }
# }

# End test and declare winner
ab_manager.end_test("response_style_test", winner="variant_b")
```

## Privacy Features

### Differential Privacy

```python
from src.ai.federated_learning import DifferentialPrivacy

# Initialize with privacy budget
dp = DifferentialPrivacy(epsilon=1.0, delta=1e-5)

# Add noise to data
noisy_data = dp.add_noise(sensitive_data, sensitivity=1.0)

# Clip gradients to bound sensitivity
clipped = dp.clip_gradients(gradients, max_norm=1.0)
```

### Privacy Analysis

```python
from src.ai.federated_learning import PrivacyAnalyzer

analyzer = PrivacyAnalyzer()

# Compute privacy budget
budget = analyzer.compute_privacy_budget(epsilon=1.0, num_queries=100)
# {
#     "per_query_epsilon": 1.0,
#     "total_queries": 100,
#     "total_epsilon": 3.16,
#     "privacy_guarantee": "differential_privacy"
# }

# Log privacy operation
analyzer.log_privacy_operation(
    operation="model_training",
    epsilon_used=0.1,
    data_accessed=500
)

# Get privacy report
report = analyzer.get_privacy_report()
# {
#     "total_operations": 25,
#     "total_epsilon_used": 0.85,
#     "privacy_status": "strong"
# }
```

## UI Components

The PyQt6 interface provides 5 main tabs:

### 1. Personalization Tab
- Communication style selector (Professional, Casual, Friendly, Technical)
- Detail level (Brief, Medium, Detailed)
- Response format (Conversational, Structured, Bullet Points)
- Tone selection (Formal, Neutral, Friendly, Humorous)
- Learning preferences toggles
- Expertise level configuration per topic

### 2. Training Tab
- Model selection (GPT-3.5, GPT-4, Custom)
- Training configuration (learning rate, epochs, batch size)
- Training data import
- Progress monitoring
- Training log

### 3. Performance Tab
- Live performance metrics table
- A/B testing management
- Trend visualization
- Metric statistics

### 4. Versions Tab
- Version history table
- Rollback controls
- Version comparison tool
- Model restoration

### 5. Privacy Tab
- Federated learning toggle
- Differential privacy settings
- Privacy budget (epsilon) slider
- Privacy report
- GDPR data export/deletion

## Best Practices

### 1. Data Collection
- Only collect necessary interaction data
- Obtain user consent for learning
- Implement data retention policies
- Provide easy data deletion

### 2. Model Training
- Start with at least 50 training examples
- Use validation split (20%) for evaluation
- Monitor overfitting with validation metrics
- Retrain periodically with new data

### 3. Privacy Protection
- Always enable differential privacy in production
- Use epsilon ≤ 1.0 for strong privacy
- Train models locally when possible
- Don't send raw user data to servers

### 4. Version Management
- Tag versions with meaningful descriptions
- Track metrics for every version
- Keep at least 3 recent versions
- Test thoroughly before promoting

### 5. Performance Monitoring
- Track user satisfaction continuously
- Set up alerts for metric degradation
- Run A/B tests before major changes
- Analyze trends weekly

## Integration with XENO

The fine-tuning system integrates with:

1. **ML Engine** (Priority 1): Uses predictive models as base
2. **Analytics** (Priority 2): Feeds performance data to dashboards
3. **Voice & NLP** (Priority 6): Personalizes voice responses
4. **Integration Hub** (Priority 7): Learns workflow preferences
5. **Team Features** (Priority 5): Adapts to team communication styles

## Data Storage

```
data/
├── personalization/
│   └── {user_id}/
│       ├── preferences.json          # User preferences
│       └── interactions.json         # Interaction history
├── models/
│   └── {user_id}/
│       ├── training_data.json        # Training examples
│       ├── intent_classifier.pkl     # Trained models
│       └── response_generator.pkl
├── memory/
│   └── {user_id}/
│       └── memory.json               # Contextual memory
├── model_repo/
│   ├── versions.json                 # Version metadata
│   └── {version_id}.pkl              # Model snapshots
├── performance/
│   └── metrics.json                  # Performance metrics
└── federated/
    └── {model_id}/                   # Federated model data
```

## Future Enhancements

1. **Transformer Fine-tuning**: Fine-tune actual LLM models (GPT, BERT)
2. **Active Learning**: Intelligently select examples for labeling
3. **Multi-modal Learning**: Learn from images, voice, text together
4. **Cross-user Learning**: Learn patterns across users (with privacy)
5. **Reinforcement Learning**: Use RLHF for better alignment
6. **Automated Hyperparameter Tuning**: Optimize training parameters
7. **Model Compression**: Reduce model size for faster inference
8. **Online Learning**: Update models in real-time

## Security Considerations

- All model data encrypted at rest
- Secure communication channels for federated learning
- Access control for model versions
- Audit logging of all training operations
- Regular security reviews
- Compliance with GDPR, CCPA, SOC2

## Performance Tips

1. **Training Speed**: Use GPU if available, batch training examples
2. **Memory Usage**: Clear old interactions regularly, limit history size
3. **Model Size**: Use model compression for faster inference
4. **Privacy Cost**: Higher epsilon = faster training, lower privacy
5. **Aggregation**: Wait for more updates = better global model

## Troubleshooting

### "Need at least 50 training examples"
- Collect more user interactions
- Import historical data
- Use pre-labeled datasets

### "Model accuracy not improving"
- Check training data quality
- Increase training epochs
- Adjust learning rate
- Add more diverse examples

### "High latency for predictions"
- Use model compression
- Cache frequent predictions
- Profile bottlenecks
- Consider simpler models

### "Privacy budget exceeded"
- Lower epsilon value
- Reduce number of queries
- Use local-only training
- Reset privacy budget

## License

Part of XENO Personal Assistant - Enterprise Edition
