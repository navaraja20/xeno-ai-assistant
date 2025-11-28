"""
Analytics Dashboard UI
PyQt6-based dashboard for viewing productivity analytics
"""

from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.logger import setup_logger
from src.modules.analytics_visualizer import get_visualizer
from src.modules.productivity_scorer import get_productivity_scorer


class AnalyticsDashboard(QWidget):
    """Main analytics dashboard widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger("analytics.dashboard")
        self.visualizer = get_visualizer()
        self.scorer = get_productivity_scorer()

        self._setup_ui()
        self._start_refresh_timer()
        self._refresh_dashboard()

    def _setup_ui(self):
        """Setup dashboard UI"""
        layout = QVBoxLayout(self)

        # Header
        header = self._create_header()
        layout.addLayout(header)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_overview_tab(), "📊 Overview")
        tabs.addTab(self._create_trends_tab(), "📈 Trends")
        tabs.addTab(self._create_breakdown_tab(), "📉 Breakdown")
        tabs.addTab(self._create_goals_tab(), "🎯 Goals")
        tabs.addTab(self._create_insights_tab(), "💡 Insights")

        layout.addWidget(tabs)

    def _create_header(self) -> QHBoxLayout:
        """Create dashboard header"""
        layout = QHBoxLayout()

        # Title
        title = QLabel("📊 Analytics Dashboard")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        layout.addStretch()

        # Time range selector
        range_label = QLabel("Time Range:")
        layout.addWidget(range_label)

        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(
            ["Today", "Last 7 Days", "Last 30 Days", "This Month", "All Time"]
        )
        self.time_range_combo.setCurrentIndex(1)  # Default: Last 7 Days
        self.time_range_combo.currentIndexChanged.connect(self._on_time_range_changed)
        layout.addWidget(self.time_range_combo)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_dashboard)
        refresh_btn.setStyleSheet(
            """
            QPushButton {
                background: #007ACC;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #005A9E;
            }
        """
        )
        layout.addWidget(refresh_btn)

        return layout

    def _create_overview_tab(self) -> QWidget:
        """Create overview tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Score gauge
        score_group = QGroupBox("Productivity Score")
        score_layout = QVBoxLayout(score_group)

        self.score_gauge_container = QWidget()
        score_layout.addWidget(self.score_gauge_container)

        layout.addWidget(score_group)

        # Completion rates
        rates_group = QGroupBox("Completion Rates")
        rates_layout = QVBoxLayout(rates_group)

        self.completion_rates_container = QWidget()
        rates_layout.addWidget(self.completion_rates_container)

        layout.addWidget(rates_group)

        # Weekly summary
        weekly_group = QGroupBox("Weekly Summary")
        weekly_layout = QVBoxLayout(weekly_group)

        self.weekly_summary_container = QWidget()
        weekly_layout.addWidget(self.weekly_summary_container)

        layout.addWidget(weekly_group)

        return widget

    def _create_trends_tab(self) -> QWidget:
        """Create trends tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Productivity trend
        trend_group = QGroupBox("Productivity Trend (Last 30 Days)")
        trend_layout = QVBoxLayout(trend_group)

        self.productivity_trend_container = QWidget()
        trend_layout.addWidget(self.productivity_trend_container)

        layout.addWidget(trend_group)

        # Time distribution
        time_group = QGroupBox("Activity by Hour")
        time_layout = QVBoxLayout(time_group)

        self.time_distribution_container = QWidget()
        time_layout.addWidget(self.time_distribution_container)

        layout.addWidget(time_group)

        return widget

    def _create_breakdown_tab(self) -> QWidget:
        """Create breakdown tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Activity breakdown
        activity_group = QGroupBox("Activity Breakdown")
        activity_layout = QVBoxLayout(activity_group)

        self.activity_breakdown_container = QWidget()
        activity_layout.addWidget(self.activity_breakdown_container)

        layout.addWidget(activity_group)

        # Statistics table
        stats_group = QGroupBox("Detailed Statistics")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_table = QTextEdit()
        self.stats_table.setReadOnly(True)
        self.stats_table.setMaximumHeight(300)
        stats_layout.addWidget(self.stats_table)

        layout.addWidget(stats_group)

        return widget

    def _create_goals_tab(self) -> QWidget:
        """Create goals tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Goals progress
        goals_group = QGroupBox("Goal Progress")
        goals_layout = QVBoxLayout(goals_group)

        self.goals_progress_container = QWidget()
        goals_layout.addWidget(self.goals_progress_container)

        layout.addWidget(goals_group)

        # Goals list
        goals_list_group = QGroupBox("Goal Details")
        goals_list_layout = QVBoxLayout(goals_list_group)

        self.goals_list = QTextEdit()
        self.goals_list.setReadOnly(True)
        goals_list_layout.addWidget(self.goals_list)

        layout.addWidget(goals_list_group)

        return widget

    def _create_insights_tab(self) -> QWidget:
        """Create insights tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # AI Insights
        insights_group = QGroupBox("💡 AI-Powered Insights")
        insights_layout = QVBoxLayout(insights_group)

        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setStyleSheet(
            """
            QTextEdit {
                font-size: 13px;
                line-height: 1.6;
                padding: 10px;
            }
        """
        )
        insights_layout.addWidget(self.insights_text)

        layout.addWidget(insights_group)

        # Recommendations
        rec_group = QGroupBox("📝 Recommendations")
        rec_layout = QVBoxLayout(rec_group)

        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        rec_layout.addWidget(self.recommendations_text)

        layout.addWidget(rec_group)

        return widget

    def _refresh_dashboard(self):
        """Refresh all dashboard data"""
        self.logger.info("Refreshing analytics dashboard")

        start_date, end_date = self._get_date_range()

        # Update score gauge
        self._update_score_gauge(start_date, end_date)

        # Update completion rates
        self._update_completion_rates()

        # Update weekly summary
        self._update_weekly_summary()

        # Update productivity trend
        self._update_productivity_trend()

        # Update time distribution
        self._update_time_distribution(start_date, end_date)

        # Update activity breakdown
        self._update_activity_breakdown(start_date, end_date)

        # Update statistics
        self._update_statistics(start_date, end_date)

        # Update goals
        self._update_goals()

        # Update insights
        self._update_insights(start_date, end_date)

    def _get_date_range(self):
        """Get date range based on selection"""
        range_text = self.time_range_combo.currentText()

        end_date = datetime.now()

        if range_text == "Today":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif range_text == "Last 7 Days":
            start_date = end_date - timedelta(days=7)
        elif range_text == "Last 30 Days":
            start_date = end_date - timedelta(days=30)
        elif range_text == "This Month":
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # All Time
            start_date = end_date - timedelta(days=365)

        return start_date, end_date

    def _update_score_gauge(self, start_date, end_date):
        """Update productivity score gauge"""
        try:
            fig, canvas = self.visualizer.create_productivity_score_gauge(start_date, end_date)

            # Clear container
            layout = QVBoxLayout()
            layout.addWidget(canvas)
            self.score_gauge_container.setLayout(layout)
        except Exception as e:
            self.logger.error(f"Error updating score gauge: {e}")

    def _update_completion_rates(self):
        """Update completion rates chart"""
        try:
            fig, canvas = self.visualizer.create_completion_rates_chart()

            layout = QVBoxLayout()
            layout.addWidget(canvas)
            self.completion_rates_container.setLayout(layout)
        except Exception as e:
            self.logger.error(f"Error updating completion rates: {e}")

    def _update_weekly_summary(self):
        """Update weekly summary chart"""
        try:
            fig, canvas = self.visualizer.create_weekly_summary_chart()

            layout = QVBoxLayout()
            layout.addWidget(canvas)
            self.weekly_summary_container.setLayout(layout)
        except Exception as e:
            self.logger.error(f"Error updating weekly summary: {e}")

    def _update_productivity_trend(self):
        """Update productivity trend chart"""
        try:
            fig, canvas = self.visualizer.create_productivity_trend_chart(30)

            layout = QVBoxLayout()
            layout.addWidget(canvas)
            self.productivity_trend_container.setLayout(layout)
        except Exception as e:
            self.logger.error(f"Error updating productivity trend: {e}")

    def _update_time_distribution(self, start_date, end_date):
        """Update time distribution heatmap"""
        try:
            fig, canvas = self.visualizer.create_time_distribution_heatmap(start_date, end_date)

            layout = QVBoxLayout()
            layout.addWidget(canvas)
            self.time_distribution_container.setLayout(layout)
        except Exception as e:
            self.logger.error(f"Error updating time distribution: {e}")

    def _update_activity_breakdown(self, start_date, end_date):
        """Update activity breakdown chart"""
        try:
            fig, canvas = self.visualizer.create_activity_breakdown_chart(start_date, end_date)

            layout = QVBoxLayout()
            layout.addWidget(canvas)
            self.activity_breakdown_container.setLayout(layout)
        except Exception as e:
            self.logger.error(f"Error updating activity breakdown: {e}")

    def _update_statistics(self, start_date, end_date):
        """Update statistics table"""
        try:
            metrics = self.scorer.get_detailed_metrics(start_date, end_date)

            stats_html = "<h3>Detailed Metrics</h3>"

            # Task metrics
            stats_html += "<h4>📋 Tasks</h4><ul>"
            stats_html += f"<li>Created: {metrics['task_metrics']['tasks_created']}</li>"
            stats_html += f"<li>Completed: {metrics['task_metrics']['tasks_completed']}</li>"
            stats_html += (
                f"<li>Completion Rate: {metrics['task_metrics']['completion_rate']*100:.1f}%</li>"
            )
            stats_html += "</ul>"

            # Focus metrics
            stats_html += "<h4>🎯 Focus</h4><ul>"
            stats_html += f"<li>Sessions: {metrics['focus_metrics']['total_focus_sessions']}</li>"
            stats_html += (
                f"<li>Total Hours: {metrics['focus_metrics']['total_focus_hours']:.1f}</li>"
            )
            stats_html += f"<li>Avg Session: {metrics['focus_metrics']['avg_session_duration_minutes']:.0f} min</li>"
            stats_html += "</ul>"

            # Communication metrics
            stats_html += "<h4>📧 Communication</h4><ul>"
            stats_html += f"<li>Emails Read: {metrics['communication_metrics']['emails_read']}</li>"
            stats_html += f"<li>Emails Sent: {metrics['communication_metrics']['emails_sent']}</li>"
            stats_html += f"<li>Response Rate: {metrics['communication_metrics']['email_response_rate']*100:.1f}%</li>"
            stats_html += "</ul>"

            # Time metrics
            stats_html += "<h4>⏰ Time</h4><ul>"
            stats_html += (
                f"<li>Total Tracked: {metrics['time_metrics']['total_tracked_hours']:.1f}h</li>"
            )
            stats_html += f"<li>Meetings: {metrics['time_metrics']['meeting_hours']:.1f}h</li>"
            stats_html += f"<li>Focus Time: {metrics['time_metrics']['focus_hours']:.1f}h</li>"
            stats_html += "</ul>"

            self.stats_table.setHtml(stats_html)
        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")
            self.stats_table.setText("Error loading statistics")

    def _update_goals(self):
        """Update goals progress"""
        try:
            # Update chart
            fig, canvas = self.visualizer.create_goals_progress_chart()

            layout = QVBoxLayout()
            layout.addWidget(canvas)
            self.goals_progress_container.setLayout(layout)

            # Update goals list
            goals = self.scorer.get_productivity_goals()

            goals_html = "<h3>Your Productivity Goals</h3>"

            for goal_name, goal_data in goals.items():
                current = goal_data["current"]
                target = goal_data["target"]
                rec = goal_data["recommendation"]

                progress = (current / target * 100) if target > 0 else 0

                color = "#28A745" if progress >= 100 else "#FFC107" if progress >= 80 else "#DC3545"

                goals_html += (
                    f"<div style='margin: 10px 0; padding: 10px; border-left: 4px solid {color};'>"
                )
                goals_html += f"<h4>{goal_name.replace('_', ' ').title()}</h4>"
                goals_html += f"<p><strong>Current:</strong> {current:.1f} | <strong>Target:</strong> {target:.1f}</p>"
                goals_html += f"<p><strong>Progress:</strong> {progress:.0f}%</p>"
                goals_html += f"<p><em>{rec}</em></p>"
                goals_html += "</div>"

            self.goals_list.setHtml(goals_html)
        except Exception as e:
            self.logger.error(f"Error updating goals: {e}")

    def _update_insights(self, start_date, end_date):
        """Update AI insights"""
        try:
            insights = self.scorer.get_productivity_insights(start_date, end_date)

            insights_html = "<h3>AI-Powered Insights</h3>"
            insights_html += (
                "<p>Based on your activity patterns, here are personalized recommendations:</p>"
            )
            insights_html += "<ul>"

            for insight in insights:
                insights_html += f"<li style='margin: 8px 0; font-size: 13px;'>{insight}</li>"

            insights_html += "</ul>"

            self.insights_text.setHtml(insights_html)

            # Add recommendations
            rec_html = "<h3>Action Items</h3><ul>"
            rec_html += "<li>📅 Schedule deep focus sessions during your peak hours</li>"
            rec_html += "<li>📧 Set aside specific times for email processing</li>"
            rec_html += "<li>✅ Break large tasks into smaller, manageable chunks</li>"
            rec_html += "<li>🎯 Use focus modes to minimize distractions</li>"
            rec_html += "<li>📊 Review this dashboard weekly to track progress</li>"
            rec_html += "</ul>"

            self.recommendations_text.setHtml(rec_html)
        except Exception as e:
            self.logger.error(f"Error updating insights: {e}")

    def _on_time_range_changed(self):
        """Handle time range change"""
        self._refresh_dashboard()

    def _start_refresh_timer(self):
        """Start periodic refresh timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_dashboard)
        self.refresh_timer.start(300000)  # Refresh every 5 minutes


# Demo/testing function
if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    from src.modules.analytics_engine import ActivityType, track_activity

    app = QApplication(sys.argv)

    # Generate some test data
    for i in range(50):
        track_activity(ActivityType.EMAIL_READ, 120, priority="medium")
        track_activity(ActivityType.TASK_COMPLETED, 1800, priority="high")
        track_activity(ActivityType.FOCUS_SESSION, 3600, completed=True)

    # Create dashboard
    dashboard = AnalyticsDashboard()
    dashboard.resize(1200, 800)
    dashboard.setWindowTitle("XENO Analytics Dashboard")
    dashboard.show()

    sys.exit(app.exec())
