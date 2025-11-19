"""
Analytics Dashboard Visualization
Creates interactive charts and graphs for productivity analysis
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import seaborn as sns
import numpy as np
import pandas as pd
from core.logger import setup_logger


class AnalyticsDashboard:
    """Generate analytics visualizations for productivity insights"""
    
    def __init__(self, analytics_collector=None, predictive_analytics=None):
        """Initialize analytics dashboard"""
        self.logger = setup_logger("ml.analytics_dashboard")
        self.analytics_collector = analytics_collector
        self.predictive_analytics = predictive_analytics
        
        # Set style
        sns.set_style("darkgrid")
        plt.rcParams['figure.facecolor'] = '#2b2d31'
        plt.rcParams['axes.facecolor'] = '#313338'
        plt.rcParams['text.color'] = 'white'
        plt.rcParams['axes.labelcolor'] = 'white'
        plt.rcParams['xtick.color'] = 'white'
        plt.rcParams['ytick.color'] = 'white'
        plt.rcParams['grid.color'] = '#40444b'
        
        self.logger.info("Analytics Dashboard initialized")
    
    def create_email_response_chart(self) -> Figure:
        """Create email response time chart"""
        if not self.analytics_collector or not self.analytics_collector.email_activities:
            return self._create_no_data_figure("No email data available")
        
        # Extract reply times
        replies = [
            {
                'timestamp': datetime.fromisoformat(a['timestamp']),
                'response_time': a['time_since_received_seconds'] / 3600  # Convert to hours
            }
            for a in self.analytics_collector.email_activities
            if a['event'] == 'replied' and 'time_since_received_seconds' in a
        ]
        
        if not replies:
            return self._create_no_data_figure("No reply data available")
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Response time distribution
        response_times = [r['response_time'] for r in replies]
        ax1.hist(response_times, bins=20, color='#5865F2', edgecolor='white', alpha=0.7)
        ax1.set_xlabel('Response Time (hours)')
        ax1.set_ylabel('Number of Emails')
        ax1.set_title('Email Response Time Distribution', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Response time trend
        df = pd.DataFrame(replies)
        df = df.set_index('timestamp')
        daily_avg = df.resample('D')['response_time'].mean()
        
        ax2.plot(daily_avg.index, daily_avg.values, color='#57F287', linewidth=2, marker='o')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Average Response Time (hours)')
        ax2.set_title('Response Time Trend', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
    
    def create_productivity_heatmap(self) -> Figure:
        """Create productivity heatmap by hour and day"""
        if not self.analytics_collector or not self.analytics_collector.productivity_log:
            return self._create_no_data_figure("No productivity data available")
        
        # Create hourly/daily matrix
        data = np.zeros((7, 24))  # 7 days, 24 hours
        counts = np.zeros((7, 24))
        
        for log in self.analytics_collector.productivity_log:
            day = log['day_of_week']
            hour = log['hour']
            quality = log['quality_score']
            
            data[day, hour] += quality
            counts[day, hour] += 1
        
        # Calculate averages
        with np.errstate(divide='ignore', invalid='ignore'):
            data = np.divide(data, counts)
            data[~np.isfinite(data)] = 0
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(14, 6))
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = [f'{h:02d}:00' for h in range(24)]
        
        im = ax.imshow(data, cmap='YlOrRd', aspect='auto', vmin=0, vmax=10)
        
        # Set ticks
        ax.set_xticks(np.arange(len(hours))[::2])
        ax.set_xticklabels([hours[i] for i in range(0, len(hours), 2)], rotation=45)
        ax.set_yticks(np.arange(len(days)))
        ax.set_yticklabels(days)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Average Productivity Quality (1-10)', rotation=270, labelpad=20)
        
        ax.set_title('Productivity Heatmap by Day and Hour', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Day of Week')
        
        plt.tight_layout()
        return fig
    
    def create_job_search_analytics(self) -> Figure:
        """Create job search analytics chart"""
        if not self.analytics_collector or not self.analytics_collector.job_activities:
            return self._create_no_data_figure("No job search data available")
        
        # Count activities by type
        activity_counts = {}
        for activity in self.analytics_collector.job_activities:
            event = activity['event']
            activity_counts[event] = activity_counts.get(event, 0) + 1
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Activity breakdown pie chart
        colors = ['#5865F2', '#57F287', '#FEE75C', '#EB459E', '#ED4245']
        ax1.pie(
            activity_counts.values(),
            labels=activity_counts.keys(),
            autopct='%1.1f%%',
            colors=colors[:len(activity_counts)],
            textprops={'color': 'white', 'fontsize': 11}
        )
        ax1.set_title('Job Search Activity Breakdown', fontsize=14, fontweight='bold')
        
        # Application funnel
        viewed = activity_counts.get('viewed', 0)
        saved = activity_counts.get('saved', 0)
        applied = activity_counts.get('applied', 0)
        
        # Count outcomes
        interviews = sum(1 for a in self.analytics_collector.job_activities if a.get('outcome') == 'interview')
        offers = sum(1 for a in self.analytics_collector.job_activities if a.get('outcome') == 'offer')
        
        stages = ['Viewed', 'Saved', 'Applied', 'Interviews', 'Offers']
        counts = [viewed, saved, applied, interviews, offers]
        
        bars = ax2.barh(stages, counts, color='#5865F2')
        ax2.set_xlabel('Count')
        ax2.set_title('Application Funnel', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add count labels
        for i, (stage, count) in enumerate(zip(stages, counts)):
            if count > 0:
                ax2.text(count + max(counts)*0.02, i, str(count), va='center', fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def create_github_activity_chart(self) -> Figure:
        """Create GitHub activity chart"""
        if not self.analytics_collector or not self.analytics_collector.github_activities:
            return self._create_no_data_figure("No GitHub data available")
        
        # Group activities by type
        activity_counts = {}
        for activity in self.analytics_collector.github_activities:
            act_type = activity['activity_type']
            activity_counts[act_type] = activity_counts.get(act_type, 0) + 1
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        activities = list(activity_counts.keys())
        counts = list(activity_counts.values())
        
        bars = ax.bar(activities, counts, color='#5865F2', edgecolor='white', alpha=0.8)
        
        # Highlight max
        max_idx = counts.index(max(counts))
        bars[max_idx].set_color('#57F287')
        
        ax.set_xlabel('Activity Type')
        ax.set_ylabel('Count')
        ax.set_title('GitHub Activity Breakdown', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        return fig
    
    def create_time_allocation_chart(self) -> Figure:
        """Create time allocation pie chart"""
        if not self.analytics_collector or not self.analytics_collector.productivity_log:
            return self._create_no_data_figure("No productivity data available")
        
        # Sum duration by task type
        task_durations = {}
        for log in self.analytics_collector.productivity_log:
            task_type = log['task_type']
            duration = log['duration_seconds'] / 3600  # Convert to hours
            task_durations[task_type] = task_durations.get(task_type, 0) + duration
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['#5865F2', '#57F287', '#FEE75C', '#EB459E', '#ED4245', '#FF6B6B']
        
        wedges, texts, autotexts = ax.pie(
            task_durations.values(),
            labels=task_durations.keys(),
            autopct=lambda pct: f'{pct:.1f}%\n({pct/100 * sum(task_durations.values()):.1f}h)',
            colors=colors[:len(task_durations)],
            textprops={'color': 'white', 'fontsize': 11}
        )
        
        # Bold percentages
        for autotext in autotexts:
            autotext.set_fontweight('bold')
        
        ax.set_title('Time Allocation by Task Type', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def create_productivity_trends(self) -> Figure:
        """Create productivity trends over time"""
        if not self.analytics_collector or not self.analytics_collector.productivity_log:
            return self._create_no_data_figure("No productivity data available")
        
        # Create DataFrame
        df = pd.DataFrame(self.analytics_collector.productivity_log)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        # Resample to daily averages
        daily_quality = df.resample('D')['quality_score'].mean()
        daily_duration = df.resample('D')['duration_seconds'].sum() / 3600  # Hours
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Quality trend
        ax1.plot(daily_quality.index, daily_quality.values, color='#57F287', linewidth=2, marker='o')
        ax1.fill_between(daily_quality.index, daily_quality.values, alpha=0.3, color='#57F287')
        ax1.set_ylabel('Average Quality Score')
        ax1.set_title('Daily Productivity Quality Trend', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        
        # Duration trend
        ax2.bar(daily_duration.index, daily_duration.values, color='#5865F2', alpha=0.7)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Total Hours')
        ax2.set_title('Daily Work Duration', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
    
    def create_ml_predictions_chart(self) -> Figure:
        """Create chart showing ML prediction accuracy"""
        if not self.predictive_analytics:
            return self._create_no_data_figure("ML predictions not available")
        
        insights = self.predictive_analytics.get_insights()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Model status
        models = insights['models_trained']
        model_names = list(models.keys())
        model_status = [1 if models[m] else 0 for m in model_names]
        
        colors = ['#57F287' if s else '#ED4245' for s in model_status]
        ax1.barh(model_names, model_status, color=colors)
        ax1.set_xlim(0, 1.2)
        ax1.set_xticks([0, 1])
        ax1.set_xticklabels(['Not Trained', 'Trained'])
        ax1.set_title('ML Models Status', fontsize=12, fontweight='bold')
        
        # Training data size
        data_sizes = insights['training_data_size']
        ax2.bar(data_sizes.keys(), data_sizes.values(), color='#5865F2')
        ax2.set_ylabel('Number of Examples')
        ax2.set_title('Training Data Size', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Recommendations
        recommendations = insights['recommendations']
        if recommendations:
            ax3.text(0.1, 0.9, 'ML Recommendations:', fontsize=12, fontweight='bold', 
                    transform=ax3.transAxes, verticalalignment='top')
            
            for i, rec in enumerate(recommendations[:5]):  # Show max 5
                ax3.text(0.1, 0.8 - i*0.15, f"• {rec}", fontsize=10, 
                        transform=ax3.transAxes, verticalalignment='top', wrap=True)
            
            ax3.axis('off')
        else:
            ax3.text(0.5, 0.5, 'No recommendations yet\nCollecting data...', 
                    ha='center', va='center', fontsize=12, transform=ax3.transAxes)
            ax3.axis('off')
        
        # Placeholder for accuracy metrics (would need actual predictions vs outcomes)
        ax4.text(0.5, 0.5, 'Prediction Accuracy\nComing Soon', 
                ha='center', va='center', fontsize=12, transform=ax4.transAxes)
        ax4.axis('off')
        
        plt.tight_layout()
        return fig
    
    def create_comprehensive_report(self) -> List[Figure]:
        """Create comprehensive analytics report with all charts"""
        figures = []
        
        try:
            figures.append(self.create_email_response_chart())
        except Exception as e:
            self.logger.error(f"Failed to create email chart: {e}")
        
        try:
            figures.append(self.create_productivity_heatmap())
        except Exception as e:
            self.logger.error(f"Failed to create productivity heatmap: {e}")
        
        try:
            figures.append(self.create_job_search_analytics())
        except Exception as e:
            self.logger.error(f"Failed to create job chart: {e}")
        
        try:
            figures.append(self.create_time_allocation_chart())
        except Exception as e:
            self.logger.error(f"Failed to create time allocation chart: {e}")
        
        try:
            figures.append(self.create_productivity_trends())
        except Exception as e:
            self.logger.error(f"Failed to create productivity trends: {e}")
        
        try:
            figures.append(self.create_ml_predictions_chart())
        except Exception as e:
            self.logger.error(f"Failed to create ML chart: {e}")
        
        return figures
    
    def _create_no_data_figure(self, message: str) -> Figure:
        """Create placeholder figure when no data available"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=14, color='gray')
        ax.axis('off')
        return fig
    
    def save_report(self, output_dir: Path):
        """Save comprehensive report to files"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        figures = self.create_comprehensive_report()
        
        filenames = [
            'email_response_analysis.png',
            'productivity_heatmap.png',
            'job_search_analytics.png',
            'time_allocation.png',
            'productivity_trends.png',
            'ml_predictions.png'
        ]
        
        for fig, filename in zip(figures, filenames):
            try:
                fig.savefig(output_dir / filename, dpi=150, bbox_inches='tight', facecolor='#2b2d31')
                plt.close(fig)
                self.logger.info(f"Saved {filename}")
            except Exception as e:
                self.logger.error(f"Failed to save {filename}: {e}")
        
        self.logger.info(f"Analytics report saved to {output_dir}")
