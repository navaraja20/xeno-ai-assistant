"""
Analytics Visualizer
Creates charts, graphs, and visual representations of productivity data
"""

import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.core.logger import setup_logger
from src.modules.analytics_engine import get_analytics_engine
from src.modules.productivity_scorer import get_productivity_scorer


class AnalyticsVisualizer:
    """Creates visualizations for analytics data"""

    def __init__(self):
        self.logger = setup_logger("analytics.visualizer")
        self.engine = get_analytics_engine()
        self.scorer = get_productivity_scorer()

        # Configure matplotlib style
        plt.style.use("seaborn-v0_8-darkgrid")
        self.color_scheme = {
            "primary": "#007ACC",
            "success": "#28A745",
            "warning": "#FFC107",
            "danger": "#DC3545",
            "info": "#17A2B8",
            "gray": "#6C757D",
        }

    def create_productivity_trend_chart(self, days: int = 30) -> Tuple[Figure, FigureCanvas]:
        """Create productivity trend line chart"""

        fig = Figure(figsize=(10, 4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Get trend data
        trends = self.engine.get_productivity_trends(days)

        if not trends:
            ax.text(
                0.5,
                0.5,
                "No data available",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            return fig, canvas

        dates = [t[0] for t in trends]
        scores = [t[1] * 100 for t in trends]  # Convert to 0-100 scale

        # Plot line
        ax.plot(dates, scores, color=self.color_scheme["primary"], linewidth=2, marker="o")

        # Add moving average
        if len(scores) >= 7:
            ma = np.convolve(scores, np.ones(7) / 7, mode="valid")
            ma_dates = dates[6:]
            ax.plot(
                ma_dates,
                ma,
                color=self.color_scheme["success"],
                linestyle="--",
                linewidth=2,
                label="7-day average",
                alpha=0.7,
            )

        # Add target line
        ax.axhline(y=80, color=self.color_scheme["warning"], linestyle=":", label="Target (80)")

        # Styling
        ax.set_title("Productivity Trend", fontsize=14, fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("Productivity Score")
        ax.set_ylim(0, 100)
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Rotate x-axis labels
        fig.autofmt_xdate()

        fig.tight_layout()
        return fig, canvas

    def create_activity_breakdown_chart(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> Tuple[Figure, FigureCanvas]:
        """Create activity breakdown pie chart"""

        fig = Figure(figsize=(8, 6))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Get activity data
        breakdown = self.engine.get_activity_breakdown(start_date, end_date)

        if not breakdown:
            ax.text(
                0.5,
                0.5,
                "No data available",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            return fig, canvas

        # Sort by count
        sorted_activities = sorted(breakdown.items(), key=lambda x: x[1]["count"], reverse=True)

        # Take top 8, group rest as "Other"
        if len(sorted_activities) > 8:
            top_8 = sorted_activities[:8]
            other_count = sum(x[1]["count"] for x in sorted_activities[8:])
            activities = top_8 + [("Other", {"count": other_count})]
        else:
            activities = sorted_activities

        labels = [self._format_activity_label(a[0]) for a in activities]
        sizes = [a[1]["count"] for a in activities]

        # Colors
        colors = [
            "#007ACC",
            "#28A745",
            "#FFC107",
            "#DC3545",
            "#17A2B8",
            "#6C757D",
            "#E83E8C",
            "#6F42C1",
            "#20C997",
        ]

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors[: len(sizes)],
            autopct="%1.1f%%",
            startangle=90,
        )

        # Styling
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        ax.set_title("Activity Breakdown", fontsize=14, fontweight="bold")

        fig.tight_layout()
        return fig, canvas

    def create_time_distribution_heatmap(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> Tuple[Figure, FigureCanvas]:
        """Create hourly time distribution heatmap"""

        fig = Figure(figsize=(12, 4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Get time distribution
        distribution = self.engine.get_time_distribution(start_date, end_date)

        if not distribution:
            ax.text(
                0.5,
                0.5,
                "No data available",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            return fig, canvas

        # Create hourly data (0-23)
        hours = list(range(24))
        minutes = [distribution.get(h, 0) for h in hours]

        # Create bar chart
        bars = ax.bar(hours, minutes, color=self.color_scheme["primary"], alpha=0.7)

        # Color bars based on intensity
        max_minutes = max(minutes) if minutes else 1
        for bar, minute in zip(bars, minutes):
            intensity = minute / max_minutes
            if intensity > 0.7:
                bar.set_color(self.color_scheme["danger"])
            elif intensity > 0.4:
                bar.set_color(self.color_scheme["warning"])
            else:
                bar.set_color(self.color_scheme["info"])

        # Styling
        ax.set_title("Activity by Hour of Day", fontsize=14, fontweight="bold")
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Minutes")
        ax.set_xticks(hours)
        ax.set_xticklabels([f"{h:02d}:00" for h in hours], rotation=45, ha="right")
        ax.grid(True, alpha=0.3, axis="y")

        fig.tight_layout()
        return fig, canvas

    def create_weekly_summary_chart(
        self, week_start: datetime = None
    ) -> Tuple[Figure, FigureCanvas]:
        """Create weekly summary bar chart"""

        fig = Figure(figsize=(10, 5))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Get weekly data
        weekly = self.engine.get_weekly_summary(week_start)

        if not weekly or not weekly.get("daily_summaries"):
            ax.text(
                0.5,
                0.5,
                "No data available",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            return fig, canvas

        daily = weekly["daily_summaries"]

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        events = [d["total_events"] for d in daily]
        durations = [d["total_duration_minutes"] / 60 for d in daily]  # Convert to hours
        scores = [d["productivity_score"] * 100 for d in daily]

        x = np.arange(len(days))
        width = 0.25

        # Create grouped bars
        ax.bar(x - width, events, width, label="Events", color=self.color_scheme["info"])
        ax.bar(x, durations, width, label="Hours", color=self.color_scheme["primary"])
        ax.bar(x + width, scores, width, label="Score", color=self.color_scheme["success"])

        # Styling
        ax.set_title("Weekly Activity Summary", fontsize=14, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(days)
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")

        fig.tight_layout()
        return fig, canvas

    def create_completion_rates_chart(self) -> Tuple[Figure, FigureCanvas]:
        """Create completion rates comparison chart"""

        fig = Figure(figsize=(8, 5))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Get completion rates
        rates = self.engine.get_completion_rates()

        if not rates:
            ax.text(
                0.5,
                0.5,
                "No data available",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            return fig, canvas

        categories = ["Tasks", "Email\nResponses", "Focus\nSessions"]
        values = [
            rates.get("task_completion_rate", 0) * 100,
            rates.get("email_response_rate", 0) * 100,
            rates.get("focus_completion_rate", 0) * 100,
        ]

        # Create horizontal bars
        colors = [
            self.color_scheme["success"]
            if v >= 80
            else self.color_scheme["warning"]
            if v >= 60
            else self.color_scheme["danger"]
            for v in values
        ]

        bars = ax.barh(categories, values, color=colors, alpha=0.7)

        # Add value labels
        for bar, value in zip(bars, values):
            width = bar.get_width()
            ax.text(
                width + 2,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.1f}%",
                ha="left",
                va="center",
                fontweight="bold",
            )

        # Add target line
        ax.axvline(x=80, color=self.color_scheme["gray"], linestyle="--", label="Target (80%)")

        # Styling
        ax.set_title("Completion Rates", fontsize=14, fontweight="bold")
        ax.set_xlabel("Completion Rate (%)")
        ax.set_xlim(0, 110)
        ax.legend()
        ax.grid(True, alpha=0.3, axis="x")

        fig.tight_layout()
        return fig, canvas

    def create_productivity_score_gauge(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> Tuple[Figure, FigureCanvas]:
        """Create productivity score gauge/meter"""

        fig = Figure(figsize=(6, 4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111, projection="polar")

        # Get score
        score = self.scorer.calculate_productivity_score(start_date, end_date)

        # Create gauge
        theta = np.linspace(0, np.pi, 100)

        # Background arc
        ax.plot(theta, [1] * len(theta), color="#E0E0E0", linewidth=20, solid_capstyle="round")

        # Score arc
        score_theta = np.linspace(0, np.pi * (score / 100), 100)
        color = (
            self.color_scheme["success"]
            if score >= 80
            else self.color_scheme["warning"]
            if score >= 60
            else self.color_scheme["danger"]
        )
        ax.plot(
            score_theta,
            [1] * len(score_theta),
            color=color,
            linewidth=20,
            solid_capstyle="round",
        )

        # Add score text
        ax.text(
            0,
            0,
            f"{score:.0f}",
            ha="center",
            va="center",
            fontsize=40,
            fontweight="bold",
            color=color,
        )
        ax.text(
            0,
            -0.3,
            "Productivity Score",
            ha="center",
            va="center",
            fontsize=12,
            color="#666",
        )

        # Remove labels and ticks
        ax.set_ylim(0, 1.2)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.spines["polar"].set_visible(False)

        fig.tight_layout()
        return fig, canvas

    def create_goals_progress_chart(self) -> Tuple[Figure, FigureCanvas]:
        """Create goals progress chart"""

        fig = Figure(figsize=(10, 6))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Get goals
        goals = self.scorer.get_productivity_goals()

        if not goals:
            ax.text(
                0.5,
                0.5,
                "No goals set",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            return fig, canvas

        goal_names = list(goals.keys())
        current_values = [goals[g]["current"] for g in goal_names]
        target_values = [goals[g]["target"] for g in goal_names]

        x = np.arange(len(goal_names))
        width = 0.35

        # Create grouped bars
        bars1 = ax.bar(
            x - width / 2,
            current_values,
            width,
            label="Current",
            color=self.color_scheme["primary"],
        )
        bars2 = ax.bar(
            x + width / 2,
            target_values,
            width,
            label="Target",
            color=self.color_scheme["success"],
            alpha=0.5,
        )

        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    f"{height:.1f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )

        # Styling
        ax.set_title("Goal Progress", fontsize=14, fontweight="bold")
        ax.set_ylabel("Value")
        ax.set_xticks(x)
        ax.set_xticklabels(
            [self._format_goal_label(g) for g in goal_names], rotation=15, ha="right"
        )
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")

        fig.tight_layout()
        return fig, canvas

    def _format_activity_label(self, activity: str) -> str:
        """Format activity label for display"""
        return activity.replace("_", " ").title()

    def _format_goal_label(self, goal: str) -> str:
        """Format goal label for display"""
        labels = {
            "task_completion": "Task\nCompletion",
            "focus_time": "Focus\nTime",
            "email_response": "Email\nResponse",
            "productivity_score": "Productivity\nScore",
        }
        return labels.get(goal, goal.replace("_", " ").title())


# Global instance
_visualizer: Optional[AnalyticsVisualizer] = None


def get_visualizer() -> AnalyticsVisualizer:
    """Get global visualizer instance"""
    global _visualizer
    if _visualizer is None:
        _visualizer = AnalyticsVisualizer()
    return _visualizer
