"""
Unit Tests for Predictive Analytics Module
Tests PredictiveAnalytics functionality
"""
import pytest
import numpy as np
from datetime import datetime
from src.ml.predictive_analytics import PredictiveAnalytics


class TestPredictiveAnalytics:
    """Test suite for PredictiveAnalytics class"""
    
    @pytest.fixture
    def engine(self):
        """Fixture to create a fresh PredictiveAnalytics instance"""
        return PredictiveAnalytics()
    
    def test_initialization(self, engine):
        """Test that engine initializes correctly"""
        assert engine is not None
        assert hasattr(engine, 'job_success_model')
        assert hasattr(engine, 'email_priority_model')
    
    def test_predict_job_success(self, engine):
        """Test job success prediction"""
        job_data = {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'San Francisco',
            'salary_range': '$100k-$150k',
            'required_skills': ['Python', 'Django'],
            'experience_required': 3,
            'company_size': 'medium',
            'industry': 'Technology'
        }
        
        probability, importance = engine.predict_job_success(job_data)
        
        assert 0.0 <= probability <= 1.0
        assert isinstance(importance, dict)
    
    def test_predict_email_priority(self, engine):
        """Test email priority prediction"""
        email_data = {
            'sender': 'boss@company.com',
            'subject': 'Urgent: Project Deadline',
            'body_length': 500,
            'has_attachments': True,
            'time_received': datetime.now().isoformat()
        }
        
        priority, reason = engine.predict_email_priority(email_data)
        
        assert 1 <= priority <= 5
        assert isinstance(reason, str)
    
    def test_multiple_predictions(self, engine):
        """Test that engine can make multiple types of predictions"""
        job_data = {'title': 'Developer', 'company': 'Tech', 'location': 'NYC',
                    'salary_range': '$80k-$120k', 'required_skills': ['Python'],
                    'experience_required': 2, 'company_size': 'small', 'industry': 'Tech'}
        email_data = {'sender': 'test@test.com', 'subject': 'Test', 'body_length': 100,
                     'has_attachments': False, 'time_received': datetime.now().isoformat()}
        
        job_prob, _ = engine.predict_job_success(job_data)
        email_priority, _ = engine.predict_email_priority(email_data)
        
        assert job_prob is not None
        assert email_priority is not None


class TestProductivityPrediction:
    """Test suite for productivity prediction"""
    
    @pytest.fixture
    def engine(self):
        """Fixture to create a fresh PredictiveAnalytics instance"""
        return PredictiveAnalytics()
    
    def test_has_productivity_model(self, engine):
        """Test that engine has productivity model attribute"""
        assert hasattr(engine, 'work_time_model')
        assert hasattr(engine, 'productivity_data')
    
    def test_train_with_productivity_data(self, engine):
        """Test training with productivity data"""
        # Add productivity data
        for hour in range(9, 18):
            data = {
                'hour': hour,
                'day_of_week': 1,
                'productivity_score': 0.7 + (hour % 3) * 0.1
            }
            engine.productivity_data.append(data)
        
        assert len(engine.productivity_data) >= 9


@pytest.mark.integration
def test_predictive_analytics_with_real_data():
    """Integration test: PredictiveAnalytics with realistic data"""
    engine = PredictiveAnalytics()
    
    # Test job prediction
    job_data = {
        'title': 'Senior Software Engineer',
        'company': 'Google',
        'location': 'Mountain View, CA',
        'salary_range': '$150k-$200k',
        'required_skills': ['Python', 'Machine Learning', 'Docker'],
        'experience_required': 5,
        'company_size': 'large',
        'industry': 'Technology'
    }
    
    probability, importance = engine.predict_job_success(job_data)
    assert 0.0 <= probability <= 1.0
    assert len(importance) > 0
    
    # Test email prediction
    email_data = {
        'sender': 'ceo@company.com',
        'subject': 'Critical: System Down',
        'body_length': 300,
        'has_attachments': True,
        'time_received': datetime.now().isoformat()
    }
    
    priority, reason = engine.predict_email_priority(email_data)
    assert 1 <= priority <= 5
    assert len(reason) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
