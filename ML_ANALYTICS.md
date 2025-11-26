# 🤖 XENO Machine Learning & Analytics

## Overview

XENO now includes advanced machine learning and predictive analytics capabilities to make your assistant truly intelligent and proactive.

## Features

### 1. 🎯 Predictive Analytics Engine

Machine learning models that learn from your behavior and make intelligent predictions:

#### Job Success Prediction
- **Predicts** probability of getting an interview/offer for each job
- **Analyzes** 8 key factors:
  - Job title match with your profile
  - Skills alignment (how well your skills match requirements)
  - Experience level fit
  - Location preference score
  - Salary range compatibility
  - Company reputation
  - Industry alignment
  - Job posting freshness

**Example:**
```python
from src.ml.predictive_analytics import PredictiveAnalytics

analytics = PredictiveAnalytics()

job_data = {
    'title': 'Senior Python Developer',
    'company': 'Google',
    'location': 'Remote',
    'required_skills': ['Python', 'Django', 'AWS'],
    'experience_required': 5,
    'salary_range': '$150k-$200k',
    'industry': 'Technology'
}

probability, importance = analytics.predict_job_success(job_data)
print(f"Success probability: {probability:.1%}")
print(f"Key factors: {importance}")
```

#### Email Priority Prediction
- **Automatically prioritizes** emails from 1-5 based on:
  - Sender importance (VIP contacts, domains)
  - Subject urgency keywords
  - Email freshness
  - Attachment presence
  - Thread length
  - Past interaction frequency

**Example:**
```python
email_data = {
    'sender': 'ceo@important-client.com',
    'subject': 'URGENT: Project deadline today',
    'body_length': 500,
    'has_attachments': True,
    'time_received': datetime.now(),
    'thread_length': 5,
    'previous_interactions': 15
}

priority, reason = analytics.predict_email_priority(email_data)
print(f"Priority: {priority}/5 - {reason}")
```

#### Optimal Work Time Prediction
- **Suggests best time** to work on different tasks based on historical productivity
- **Analyzes patterns** across:
  - Hour of day
  - Day of week
  - Task type (coding, email, meetings, creative work)
  - Personal productivity rhythms

**Example:**
```python
best_time, score = analytics.predict_optimal_work_time('coding')
print(f"Best time for coding: {best_time.strftime('%A, %I:%M %p')}")
print(f"Expected productivity: {score:.1%}")
```

### 2. 📊 Advanced Analytics Dashboard

Beautiful, interactive visualizations powered by matplotlib, seaborn, and plotly:

#### Available Charts

1. **Email Response Analysis**
   - Response time distribution histogram
   - Daily average response time trend
   - Identifies if you're getting faster/slower

2. **Productivity Heatmap**
   - 7x24 grid showing quality scores by day/hour
   - Instantly see your peak productivity times
   - Color-coded from yellow (low) to red (high)

3. **Job Search Analytics**
   - Application funnel visualization
   - Activity breakdown (viewed/saved/applied/interviews/offers)
   - Conversion rate tracking

4. **Time Allocation Pie Chart**
   - Visual breakdown of hours spent per task type
   - Coding vs Email vs Meetings vs Creative work

5. **Productivity Trends**
   - Quality score trends over time
   - Work duration trends
   - Spot patterns and improvements

6. **ML Predictions Dashboard**
   - Model training status
   - Training data size
   - Personalized recommendations

#### Using the Dashboard

```python
from src.ml.analytics_dashboard import AnalyticsDashboard
from src.ml.analytics_collector import AnalyticsCollector

collector = AnalyticsCollector()
dashboard = AnalyticsDashboard(collector)

# Generate all charts
figures = dashboard.create_comprehensive_report()

# Or create specific charts
email_chart = dashboard.create_email_response_chart()
heatmap = dashboard.create_productivity_heatmap()
job_chart = dashboard.create_job_search_analytics()

# Save as images
dashboard.save_report(Path("analytics_reports"))
```

### 3. 📈 Analytics Data Collector

Automatically tracks all your activities to train ML models:

#### Tracked Activities

**Email Activities:**
- Email opened (with time to open)
- Email replied (response time, response length)
- Email archived
- Email starred

**Job Activities:**
- Job viewed (with dwell time)
- Job applied
- Job saved
- Application outcomes (interview, offer, rejection)

**Productivity:**
- Task sessions (type, duration, quality self-rating)
- Peak productivity hours
- Task completion patterns

**GitHub:**
- Repository interactions
- Commit frequency
- Code review activity

#### Recording Data

```python
from src.ml.analytics_collector import AnalyticsCollector

collector = AnalyticsCollector()

# Log email activity
collector.log_email_replied('email_123', time_since_received=3600, response_length=500)

# Log job outcome
collector.log_job_outcome('job_456', outcome='interview', notes='Phone screen scheduled')

# Log productivity session
collector.log_productivity_session(task_type='coding', duration=7200, quality=8)
```

## Architecture

### Machine Learning Models

#### 1. Job Success Model
- **Algorithm:** Random Forest Classifier
- **Features:** 8 numerical features extracted from job postings
- **Output:** Binary classification (0-1 probability)
- **Training:** Automatic retraining every 10 applications

#### 2. Email Priority Model
- **Algorithm:** Gradient Boosting Regressor
- **Features:** 8 numerical features from email metadata
- **Output:** Priority score 1-5
- **Training:** Automatic retraining every 20 emails

#### 3. Work Time Model
- **Algorithm:** Gradient Boosting Regressor
- **Features:** Time-based and task-type features
- **Output:** Productivity score 0-1
- **Training:** Automatic retraining every 30 sessions

### Data Flow

```
User Activities → Analytics Collector → Training Data
                                           ↓
                                    ML Models (sklearn)
                                           ↓
                                  Predictions & Insights
                                           ↓
                               Visualization Dashboard
```

### File Structure

```
src/ml/
├── __init__.py
├── predictive_analytics.py      # Core ML engine
├── analytics_collector.py       # Data collection
└── analytics_dashboard.py       # Visualization

data/ml/
├── models.pkl                    # Trained models
├── training_data.json            # Historical data
└── analytics/
    └── activities.json           # User activity log
```

## Getting Started

### Installation

ML dependencies are already included in requirements.txt:
```bash
pip install scikit-learn numpy pandas matplotlib plotly seaborn
```

### Quick Start

```python
# 1. Initialize components
from src.ml.predictive_analytics import PredictiveAnalytics
from src.ml.analytics_collector import AnalyticsCollector
from src.ml.analytics_dashboard import AnalyticsDashboard

analytics = PredictiveAnalytics()
collector = AnalyticsCollector()
dashboard = AnalyticsDashboard(collector, analytics)

# 2. Record some activity
collector.log_email_replied('email_1', 3600, 300)
collector.log_job_applied('job_1', 'Python Developer', 'TechCorp')
collector.log_productivity_session('coding', 7200, 8)

# 3. Get predictions
job_prediction = analytics.predict_job_success({
    'title': 'Python Developer',
    'company': 'Google',
    'location': 'Remote'
})

email_priority = analytics.predict_email_priority({
    'sender': 'boss@company.com',
    'subject': 'URGENT: Meeting in 10 min'
})

work_time = analytics.predict_optimal_work_time('coding')

# 4. Generate visualizations
dashboard.save_report(Path("my_analytics"))
```

## Advanced Features

### Custom Training

Train models with your own data:

```python
# Record job outcomes for better predictions
analytics.record_job_outcome(job_data, got_interview=True, got_offer=False)

# Record email actions
analytics.record_email_action(email_data, action='replied', time_to_action=1800)

# Record productivity
analytics.record_productivity('coding', datetime.now(), productivity_score=0.9)

# Models automatically retrain when enough data is collected
```

### Get Insights

```python
insights = analytics.get_insights()

print(f"Models trained: {insights['models_trained']}")
print(f"Training data size: {insights['training_data_size']}")
print(f"Recommendations:")
for rec in insights['recommendations']:
    print(f"  • {rec}")
```

### Statistics

```python
email_stats = collector.get_email_stats()
job_stats = collector.get_job_stats()
productivity_stats = collector.get_productivity_stats()

print(f"Reply rate: {email_stats['reply_rate']:.1%}")
print(f"Interview rate: {job_stats['application_to_interview_rate']:.1%}")
print(f"Peak hours: {productivity_stats['peak_hours']}")
```

## Privacy & Data

- **All data stored locally** in `data/ml/` and `data/analytics/`
- **No external servers** - ML training happens on your machine
- **You control the data** - delete files to reset
- **Automatic data limits** - keeps last 1000 activities to prevent bloat

## Performance

- **Models trained in seconds** on standard hardware
- **Predictions in milliseconds** - instant results
- **Automatic optimization** - models improve as you use XENO
- **Low memory footprint** - < 50MB for all models

## Roadmap

Future enhancements:
- [ ] Deep learning models for more complex patterns
- [ ] Natural language processing for email/job content
- [ ] Collaborative filtering (if multi-user support added)
- [ ] Real-time prediction API
- [ ] Mobile app integration
- [ ] Export to TensorBoard for advanced analysis

## Tips for Best Results

1. **Let it learn** - More data = better predictions
2. **Record outcomes** - Always log job interview/offer results
3. **Rate your productivity** - Honest self-ratings improve time predictions
4. **Check insights weekly** - Use dashboard to identify patterns
5. **Act on recommendations** - ML learns from your behavior changes

## Troubleshooting

**Models not training?**
- Check data/ml/training_data.json exists
- Ensure minimum data collected (10 jobs, 20 emails, 30 productivity logs)

**Predictions seem off?**
- Models need more data to learn your patterns
- Record actual outcomes to improve accuracy
- Default models are generic - personalization takes time

**Charts not generating?**
- Ensure matplotlib/seaborn installed
- Check analytics data collected
- Look for errors in logs

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Verify data files in `data/ml/` and `data/analytics/`
3. Review this documentation

---

**🚀 With ML & Analytics, XENO evolves from a reactive assistant to a proactive productivity partner!**
