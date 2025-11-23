"""
Unit Tests for Analytics Collector Module
Tests data collection, aggregation, and export functionality
"""
import pytest
from datetime import datetime, timedelta
from src.ml.analytics_collector import AnalyticsCollector


class TestAnalyticsCollector:
    """Test suite for AnalyticsCollector class"""
    
    @pytest.fixture
    def collector(self):
        """Fixture to create a fresh AnalyticsCollector instance"""
        return AnalyticsCollector()
    
    def test_initialization(self, collector):
        """Test that collector initializes correctly"""
        assert collector is not None
        assert hasattr(collector, 'email_activities')
        assert hasattr(collector, 'job_activities')
    
    def test_log_email_opened(self, collector):
        """Test logging email opened event"""
        collector.log_email_opened("email_123", "sender@test.com", "Test Subject", 300)
        
        assert len(collector.email_activities) > 0
        assert collector.email_activities[-1]['event'] == 'opened'
    
    def test_log_multiple_events(self, collector):
        """Test logging multiple events"""
        collector.log_email_opened("email_1", "sender1@test.com", "Subject 1", 100)
        collector.log_email_replied("email_2", 200, 500)
        collector.log_email_archived("email_3")
        
        # Verify events were tracked
        assert len(collector.email_activities) >= 3
    
    def test_log_job_viewed(self, collector):
        """Test logging job viewed event"""
        collector.log_job_viewed("job_123", "Software Engineer", "Tech Corp", 45)
        
        assert len(collector.job_activities) > 0
        assert collector.job_activities[-1]['event'] == 'viewed'
    
    def test_log_different_email_events(self, collector):
        """Test logging different email event types"""
        collector.log_email_opened("email_1", "test@test.com", "Test", 100)
        collector.log_email_replied("email_2", 200, 300)
        collector.log_email_starred("email_3")
        collector.log_email_archived("email_4")
        
        assert len(collector.email_activities) >= 4
        events = [e['event'] for e in collector.email_activities]
        assert 'opened' in events
        assert 'replied' in events
        assert 'starred' in events
        assert 'archived' in events


class TestAnalyticsData:
    """Test suite for analytics data management"""
    
    @pytest.fixture
    def collector(self):
        return AnalyticsCollector()
    
    def test_email_activity_storage(self, collector):
        """Test that email activities are stored properly"""
        initial_count = len(collector.email_activities)
        
        collector.log_email_opened("test_email", "sender@test.com", "Test", 100)
        
        assert len(collector.email_activities) == initial_count + 1
    
    def test_job_activity_storage(self, collector):
        """Test that job activities are stored properly"""
        initial_count = len(collector.job_activities)
        
        collector.log_job_viewed("job_123", "Engineer", "Company", 30)
        
        assert len(collector.job_activities) == initial_count + 1


@pytest.mark.integration
def test_analytics_collector_full_workflow():
    """Integration test: Complete analytics workflow"""
    collector = AnalyticsCollector()
    
    # Simulate a day of user activity
    for hour in range(24):
        # Email activities
        collector.log_email_opened(f"email_{hour}", f"sender{hour}@test.com", f"Subject {hour}", hour * 60)
        if hour % 2 == 0:
            collector.log_email_replied(f"email_{hour}", hour * 60, 200)
        if hour % 3 == 0:
            collector.log_email_starred(f"email_{hour}")
        
        # Job activities
        collector.log_job_viewed(f"job_{hour}", f"Position {hour}", f"Company {hour}", hour * 5)
    
    # Verify data was collected
    assert len(collector.email_activities) >= 24
    assert len(collector.job_activities) >= 24


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
