"""
Predictive Analytics Engine for XENO
Uses machine learning to predict job success, email priority, and optimal work times
"""
import os
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from src.core.logger import setup_logger


class PredictiveAnalytics:
    """ML-powered predictive analytics for XENO"""
    
    def __init__(self, data_dir: Path = None):
        """Initialize predictive analytics engine"""
        self.logger = setup_logger("ml.predictive_analytics")
        self.data_dir = data_dir or Path(__file__).parent.parent.parent / "data" / "ml"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Models
        self.job_success_model = None
        self.email_priority_model = None
        self.work_time_model = None
        
        # Scalers
        self.job_scaler = StandardScaler()
        self.email_scaler = StandardScaler()
        self.time_scaler = StandardScaler()
        
        # Training data
        self.job_training_data = []
        self.email_training_data = []
        self.productivity_data = []
        
        self._load_models()
        self._load_training_data()
        
        self.logger.info("Predictive Analytics Engine initialized")
    
    def predict_job_success(self, job_data: Dict) -> Tuple[float, Dict]:
        """
        Predict probability of job application success
        
        Args:
            job_data: Dictionary containing job features
                - title: Job title
                - company: Company name
                - location: Job location
                - salary_range: Salary range
                - required_skills: List of required skills
                - experience_required: Years of experience
                - company_size: Company size category
                - industry: Industry type
        
        Returns:
            Tuple of (success_probability, feature_importance)
        """
        try:
            if self.job_success_model is None:
                # Initialize with default if no model
                self._train_default_job_model()
            
            # Extract features
            features = self._extract_job_features(job_data)
            features_scaled = self.job_scaler.transform([features])
            
            # Predict
            probability = self.job_success_model.predict_proba(features_scaled)[0][1]
            
            # Get feature importance
            feature_names = [
                'title_match', 'skills_match', 'experience_match', 
                'location_score', 'salary_fit', 'company_reputation',
                'industry_alignment', 'time_posted'
            ]
            importance = dict(zip(feature_names, self.job_success_model.feature_importances_))
            
            self.logger.info(f"Job success prediction: {probability:.2%}")
            return probability, importance
            
        except Exception as e:
            self.logger.error(f"Job prediction failed: {e}")
            return 0.5, {}
    
    def predict_email_priority(self, email_data: Dict) -> Tuple[int, str]:
        """
        Predict email priority (1-5 scale)
        
        Args:
            email_data: Dictionary containing email features
                - sender: Sender email
                - subject: Email subject
                - body_length: Length of email body
                - has_attachments: Boolean
                - time_received: Datetime
                - thread_length: Number of emails in thread
                - previous_interactions: Number of past emails with sender
        
        Returns:
            Tuple of (priority_score, reason)
        """
        try:
            if self.email_priority_model is None:
                self._train_default_email_model()
            
            # Extract features
            features = self._extract_email_features(email_data)
            features_scaled = self.email_scaler.transform([features])
            
            # Predict (1-5 scale)
            priority = int(self.email_priority_model.predict(features_scaled)[0])
            priority = max(1, min(5, priority))  # Clamp to 1-5
            
            # Generate reason
            reason = self._explain_email_priority(email_data, priority)
            
            self.logger.info(f"Email priority: {priority} - {reason}")
            return priority, reason
            
        except Exception as e:
            self.logger.error(f"Email priority prediction failed: {e}")
            return 3, "Default priority"
    
    def predict_optimal_work_time(self, task_type: str) -> Tuple[datetime, float]:
        """
        Predict optimal time to work on a task based on historical productivity
        
        Args:
            task_type: Type of task (coding, email, meeting, creative, etc.)
        
        Returns:
            Tuple of (suggested_time, productivity_score)
        """
        try:
            if self.work_time_model is None:
                self._train_default_time_model()
            
            # Get current time features
            now = datetime.now()
            
            # Test different time slots for next 7 days
            best_time = now
            best_score = 0.0
            
            for day in range(7):
                for hour in range(8, 20):  # 8 AM to 8 PM
                    test_time = now + timedelta(days=day, hours=hour-now.hour)
                    features = self._extract_time_features(test_time, task_type)
                    features_scaled = self.time_scaler.transform([features])
                    
                    score = self.work_time_model.predict(features_scaled)[0]
                    
                    if score > best_score:
                        best_score = score
                        best_time = test_time
            
            self.logger.info(f"Optimal time for {task_type}: {best_time.strftime('%A, %I:%M %p')} (score: {best_score:.2f})")
            return best_time, best_score
            
        except Exception as e:
            self.logger.error(f"Work time prediction failed: {e}")
            # Return next available slot (morning)
            tomorrow_9am = datetime.now().replace(hour=9, minute=0, second=0) + timedelta(days=1)
            return tomorrow_9am, 0.7
    
    def record_job_outcome(self, job_data: Dict, got_interview: bool, got_offer: bool = False):
        """Record job application outcome for training"""
        outcome_data = {
            'job': job_data,
            'got_interview': got_interview,
            'got_offer': got_offer,
            'timestamp': datetime.now().isoformat()
        }
        self.job_training_data.append(outcome_data)
        self._save_training_data()
        
        # Retrain if enough new data
        if len(self.job_training_data) % 10 == 0:
            self._retrain_job_model()
    
    def record_email_action(self, email_data: Dict, action: str, time_to_action: int):
        """
        Record email action for training
        
        Args:
            email_data: Email features
            action: Action taken (replied, archived, starred, deleted)
            time_to_action: Seconds until action was taken
        """
        action_data = {
            'email': email_data,
            'action': action,
            'time_to_action': time_to_action,
            'timestamp': datetime.now().isoformat()
        }
        self.email_training_data.append(action_data)
        self._save_training_data()
        
        if len(self.email_training_data) % 20 == 0:
            self._retrain_email_model()
    
    def record_productivity(self, task_type: str, time: datetime, productivity_score: float):
        """Record productivity at specific time for training"""
        productivity_data = {
            'task_type': task_type,
            'time': time.isoformat(),
            'productivity_score': productivity_score,
            'day_of_week': time.weekday(),
            'hour': time.hour
        }
        self.productivity_data.append(productivity_data)
        self._save_training_data()
        
        if len(self.productivity_data) % 30 == 0:
            self._retrain_time_model()
    
    def _extract_job_features(self, job_data: Dict) -> List[float]:
        """Extract numerical features from job data"""
        features = [
            self._calculate_title_match(job_data.get('title', '')),
            self._calculate_skills_match(job_data.get('required_skills', [])),
            self._calculate_experience_match(job_data.get('experience_required', 0)),
            self._calculate_location_score(job_data.get('location', '')),
            self._calculate_salary_fit(job_data.get('salary_range', '')),
            self._calculate_company_reputation(job_data.get('company', '')),
            self._calculate_industry_alignment(job_data.get('industry', '')),
            self._calculate_time_posted(job_data.get('posted_date', datetime.now()))
        ]
        return features
    
    def _extract_email_features(self, email_data: Dict) -> List[float]:
        """Extract numerical features from email data"""
        features = [
            self._calculate_sender_importance(email_data.get('sender', '')),
            self._analyze_subject_urgency(email_data.get('subject', '')),
            min(email_data.get('body_length', 0) / 1000, 10),  # Normalized length
            1.0 if email_data.get('has_attachments', False) else 0.0,
            self._calculate_time_sensitivity(email_data.get('time_received', datetime.now())),
            min(email_data.get('thread_length', 1) / 10, 5),  # Normalized thread length
            min(email_data.get('previous_interactions', 0) / 20, 5),  # Normalized interactions
            self._detect_keywords(email_data.get('subject', '') + ' ' + email_data.get('body', ''))
        ]
        return features
    
    def _extract_time_features(self, time: datetime, task_type: str) -> List[float]:
        """Extract features for time prediction"""
        features = [
            time.weekday(),  # 0-6
            time.hour,  # 0-23
            1.0 if time.weekday() < 5 else 0.0,  # Is weekday
            1.0 if 9 <= time.hour <= 17 else 0.0,  # Is work hours
            self._encode_task_type(task_type),
            self._get_historical_productivity(time.weekday(), time.hour, task_type),
            1.0 if time.hour < 12 else 0.0,  # Is morning
            1.0 if 13 <= time.hour <= 16 else 0.0  # Is afternoon
        ]
        return features
    
    def _calculate_title_match(self, title: str) -> float:
        """Calculate how well job title matches user profile"""
        # Simplified - would use user's preferred job titles
        preferred = ['python developer', 'data scientist', 'ml engineer', 'software engineer']
        title_lower = title.lower()
        
        for pref in preferred:
            if pref in title_lower:
                return 1.0
        return 0.3
    
    def _calculate_skills_match(self, required_skills: List[str]) -> float:
        """Calculate skills match percentage"""
        # Simplified - would use user's skill profile
        user_skills = {'python', 'javascript', 'react', 'sql', 'machine learning', 'aws'}
        
        if not required_skills:
            return 0.5
        
        required_set = {skill.lower() for skill in required_skills}
        matches = len(user_skills.intersection(required_set))
        
        return min(matches / len(required_set), 1.0) if required_set else 0.5
    
    def _calculate_experience_match(self, required_years: int) -> float:
        """Calculate experience match"""
        # Simplified - would use user's actual experience
        user_experience = 5
        
        if required_years <= user_experience:
            return 1.0
        elif required_years <= user_experience + 2:
            return 0.7
        else:
            return 0.3
    
    def _calculate_location_score(self, location: str) -> float:
        """Calculate location preference score"""
        # Simplified - would use user's location preferences
        if 'remote' in location.lower():
            return 1.0
        # Would check against user's preferred cities
        return 0.5
    
    def _calculate_salary_fit(self, salary_range: str) -> float:
        """Calculate if salary fits expectations"""
        # Simplified - would parse salary and compare to expectations
        if not salary_range:
            return 0.5
        
        # Look for high salary keywords
        if any(word in salary_range.lower() for word in ['competitive', 'above market', '150k', '200k']):
            return 1.0
        return 0.6
    
    def _calculate_company_reputation(self, company: str) -> float:
        """Calculate company reputation score"""
        # Simplified - would use company database/API
        top_companies = ['google', 'microsoft', 'amazon', 'apple', 'meta']
        
        if any(comp in company.lower() for comp in top_companies):
            return 1.0
        return 0.5
    
    def _calculate_industry_alignment(self, industry: str) -> float:
        """Calculate industry alignment"""
        # Simplified - would use user's industry preferences
        preferred_industries = ['technology', 'ai', 'fintech', 'healthcare tech']
        
        if any(ind in industry.lower() for ind in preferred_industries):
            return 1.0
        return 0.4
    
    def _calculate_time_posted(self, posted_date: datetime) -> float:
        """Calculate freshness score"""
        age_days = (datetime.now() - posted_date).days
        
        if age_days <= 1:
            return 1.0
        elif age_days <= 3:
            return 0.8
        elif age_days <= 7:
            return 0.6
        else:
            return 0.3
    
    def _calculate_sender_importance(self, sender: str) -> float:
        """Calculate sender importance score"""
        # Simplified - would use contact frequency and role
        vip_domains = ['@google.com', '@microsoft.com', '@important-client.com']
        
        if any(domain in sender for domain in vip_domains):
            return 1.0
        
        # Would check against user's important contacts list
        return 0.5
    
    def _analyze_subject_urgency(self, subject: str) -> float:
        """Analyze subject line for urgency"""
        urgent_keywords = ['urgent', 'asap', 'important', 'critical', 'deadline', 'today', 'now']
        subject_lower = subject.lower()
        
        for keyword in urgent_keywords:
            if keyword in subject_lower:
                return 1.0
        
        return 0.3
    
    def _calculate_time_sensitivity(self, received_time: datetime) -> float:
        """Calculate time sensitivity"""
        hours_old = (datetime.now() - received_time).total_seconds() / 3600
        
        if hours_old < 1:
            return 1.0
        elif hours_old < 24:
            return 0.7
        elif hours_old < 72:
            return 0.4
        else:
            return 0.2
    
    def _detect_keywords(self, text: str) -> float:
        """Detect important keywords"""
        important_keywords = [
            'meeting', 'call', 'review', 'approval', 'decision',
            'budget', 'contract', 'deadline', 'issue', 'problem'
        ]
        
        text_lower = text.lower()
        count = sum(1 for keyword in important_keywords if keyword in text_lower)
        
        return min(count / 3, 1.0)
    
    def _encode_task_type(self, task_type: str) -> float:
        """Encode task type as number"""
        task_encoding = {
            'coding': 1.0,
            'email': 2.0,
            'meeting': 3.0,
            'creative': 4.0,
            'planning': 5.0,
            'learning': 6.0
        }
        return task_encoding.get(task_type.lower(), 0.0)
    
    def _get_historical_productivity(self, day_of_week: int, hour: int, task_type: str) -> float:
        """Get historical productivity score for time slot"""
        # Filter productivity data for this time slot
        matching = [
            p for p in self.productivity_data
            if p['day_of_week'] == day_of_week 
            and abs(p['hour'] - hour) <= 1
            and p['task_type'] == task_type
        ]
        
        if matching:
            return np.mean([p['productivity_score'] for p in matching])
        
        # Default productivity patterns
        if hour < 9 or hour > 18:
            return 0.3
        elif 9 <= hour <= 11:
            return 0.9  # Morning peak
        elif hour == 12 or hour == 13:
            return 0.5  # Lunch dip
        elif 14 <= hour <= 16:
            return 0.8  # Afternoon peak
        else:
            return 0.6
    
    def _explain_email_priority(self, email_data: Dict, priority: int) -> str:
        """Generate explanation for email priority"""
        reasons = []
        
        if self._analyze_subject_urgency(email_data.get('subject', '')) > 0.7:
            reasons.append("urgent keywords")
        
        if self._calculate_sender_importance(email_data.get('sender', '')) > 0.7:
            reasons.append("important sender")
        
        if self._calculate_time_sensitivity(email_data.get('time_received', datetime.now())) > 0.7:
            reasons.append("recent")
        
        if email_data.get('has_attachments', False):
            reasons.append("has attachments")
        
        if reasons:
            return "High priority due to: " + ", ".join(reasons)
        elif priority > 3:
            return "Moderate priority"
        else:
            return "Standard priority"
    
    def _train_default_job_model(self):
        """Train default job success model with synthetic data"""
        self.logger.info("Training default job success model...")
        
        # Create synthetic training data
        X_train = np.random.rand(100, 8)
        # Higher scores on features = higher success
        y_train = (X_train.mean(axis=1) > 0.6).astype(int)
        
        self.job_scaler.fit(X_train)
        X_scaled = self.job_scaler.transform(X_train)
        
        self.job_success_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.job_success_model.fit(X_scaled, y_train)
        
        self._save_models()
    
    def _train_default_email_model(self):
        """Train default email priority model with synthetic data"""
        self.logger.info("Training default email priority model...")
        
        # Create synthetic training data
        X_train = np.random.rand(100, 8)
        # Priority based on feature scores
        y_train = np.clip((X_train.mean(axis=1) * 5).astype(int) + 1, 1, 5)
        
        self.email_scaler.fit(X_train)
        X_scaled = self.email_scaler.transform(X_train)
        
        self.email_priority_model = GradientBoostingRegressor(n_estimators=50, random_state=42)
        self.email_priority_model.fit(X_scaled, y_train)
        
        self._save_models()
    
    def _train_default_time_model(self):
        """Train default work time model with synthetic data"""
        self.logger.info("Training default work time model...")
        
        # Create synthetic training data with time patterns
        X_train = np.random.rand(100, 8)
        # Productivity higher during work hours
        y_train = np.random.rand(100) * X_train[:, 3]  # Work hours feature
        
        self.time_scaler.fit(X_train)
        X_scaled = self.time_scaler.transform(X_train)
        
        self.work_time_model = GradientBoostingRegressor(n_estimators=50, random_state=42)
        self.work_time_model.fit(X_scaled, y_train)
        
        self._save_models()
    
    def _retrain_job_model(self):
        """Retrain job model with collected data"""
        if len(self.job_training_data) < 10:
            return
        
        self.logger.info(f"Retraining job model with {len(self.job_training_data)} examples...")
        
        X_train = []
        y_train = []
        
        for data in self.job_training_data:
            features = self._extract_job_features(data['job'])
            X_train.append(features)
            # Success = got interview or offer
            y_train.append(1 if data['got_interview'] or data['got_offer'] else 0)
        
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        self.job_scaler.fit(X_train)
        X_scaled = self.job_scaler.transform(X_train)
        
        self.job_success_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.job_success_model.fit(X_scaled, y_train)
        
        self._save_models()
    
    def _retrain_email_model(self):
        """Retrain email model with collected data"""
        if len(self.email_training_data) < 20:
            return
        
        self.logger.info(f"Retraining email model with {len(self.email_training_data)} examples...")
        
        X_train = []
        y_train = []
        
        for data in self.email_training_data:
            features = self._extract_email_features(data['email'])
            X_train.append(features)
            
            # Calculate priority from action and time
            if data['action'] == 'replied' and data['time_to_action'] < 3600:
                priority = 5
            elif data['action'] == 'starred':
                priority = 4
            elif data['action'] == 'replied':
                priority = 3
            elif data['action'] == 'archived':
                priority = 2
            else:
                priority = 1
            
            y_train.append(priority)
        
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        self.email_scaler.fit(X_train)
        X_scaled = self.email_scaler.transform(X_train)
        
        self.email_priority_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.email_priority_model.fit(X_scaled, y_train)
        
        self._save_models()
    
    def _retrain_time_model(self):
        """Retrain work time model with collected data"""
        if len(self.productivity_data) < 30:
            return
        
        self.logger.info(f"Retraining time model with {len(self.productivity_data)} examples...")
        
        X_train = []
        y_train = []
        
        for data in self.productivity_data:
            time = datetime.fromisoformat(data['time'])
            features = self._extract_time_features(time, data['task_type'])
            X_train.append(features)
            y_train.append(data['productivity_score'])
        
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        self.time_scaler.fit(X_train)
        X_scaled = self.time_scaler.transform(X_train)
        
        self.work_time_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.work_time_model.fit(X_scaled, y_train)
        
        self._save_models()
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            models = {
                'job_model': self.job_success_model,
                'email_model': self.email_priority_model,
                'time_model': self.work_time_model,
                'job_scaler': self.job_scaler,
                'email_scaler': self.email_scaler,
                'time_scaler': self.time_scaler
            }
            
            with open(self.data_dir / 'models.pkl', 'wb') as f:
                pickle.dump(models, f)
            
            self.logger.info("Models saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save models: {e}")
    
    def _load_models(self):
        """Load trained models from disk"""
        try:
            model_file = self.data_dir / 'models.pkl'
            if model_file.exists():
                with open(model_file, 'rb') as f:
                    models = pickle.load(f)
                
                self.job_success_model = models.get('job_model')
                self.email_priority_model = models.get('email_model')
                self.work_time_model = models.get('time_model')
                self.job_scaler = models.get('job_scaler', StandardScaler())
                self.email_scaler = models.get('email_scaler', StandardScaler())
                self.time_scaler = models.get('time_scaler', StandardScaler())
                
                self.logger.info("Models loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load models: {e}")
    
    def _save_training_data(self):
        """Save training data to disk"""
        try:
            data = {
                'job_training': self.job_training_data,
                'email_training': self.email_training_data,
                'productivity': self.productivity_data
            }
            
            with open(self.data_dir / 'training_data.json', 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
        except Exception as e:
            self.logger.error(f"Failed to save training data: {e}")
    
    def _load_training_data(self):
        """Load training data from disk"""
        try:
            data_file = self.data_dir / 'training_data.json'
            if data_file.exists():
                with open(data_file, 'r') as f:
                    data = json.load(f)
                
                self.job_training_data = data.get('job_training', [])
                self.email_training_data = data.get('email_training', [])
                self.productivity_data = data.get('productivity', [])
                
                self.logger.info(f"Loaded training data: {len(self.job_training_data)} jobs, "
                               f"{len(self.email_training_data)} emails, {len(self.productivity_data)} productivity records")
        except Exception as e:
            self.logger.error(f"Failed to load training data: {e}")
    
    def get_insights(self) -> Dict:
        """Get ML insights and statistics"""
        return {
            'models_trained': {
                'job_success': self.job_success_model is not None,
                'email_priority': self.email_priority_model is not None,
                'work_time': self.work_time_model is not None
            },
            'training_data_size': {
                'jobs': len(self.job_training_data),
                'emails': len(self.email_training_data),
                'productivity': len(self.productivity_data)
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate ML-based recommendations"""
        recommendations = []
        
        # Job search recommendations
        if self.job_training_data:
            success_rate = sum(1 for d in self.job_training_data if d['got_interview']) / len(self.job_training_data)
            if success_rate < 0.2:
                recommendations.append("Consider refining your job search criteria - low interview rate detected")
        
        # Email recommendations
        if self.email_training_data:
            quick_replies = sum(1 for d in self.email_training_data if d['time_to_action'] < 3600)
            if quick_replies > len(self.email_training_data) * 0.7:
                recommendations.append("You respond quickly to emails - consider scheduling specific email times")
        
        # Productivity recommendations
        if self.productivity_data:
            morning_prod = np.mean([p['productivity_score'] for p in self.productivity_data if 6 <= p['hour'] <= 12])
            afternoon_prod = np.mean([p['productivity_score'] for p in self.productivity_data if 13 <= p['hour'] <= 18])
            
            if morning_prod > afternoon_prod * 1.2:
                recommendations.append("You're most productive in mornings - schedule important tasks before noon")
            elif afternoon_prod > morning_prod * 1.2:
                recommendations.append("You're most productive in afternoons - save complex tasks for after lunch")
        
        return recommendations

# Aliases for compatibility
PredictiveEngine = PredictiveAnalytics
BehaviorAnalyzer = PredictiveAnalytics
