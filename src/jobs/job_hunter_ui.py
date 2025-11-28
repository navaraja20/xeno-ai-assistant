"""
Job Hunter UI
PyQt6 interface for job hunting automation
"""

import os
import sys
from datetime import datetime
from typing import List, Optional

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.logger import setup_logger
from src.jobs.cover_letter_generator import get_cover_letter_generator
from src.jobs.job_hunter import JobOpportunity, get_job_hunter
from src.jobs.resume_tailor import get_resume_tailor


class JobSearchWorker(QThread):
    """Background worker for job search"""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, keywords: List[str], location: str, sources: List[str], max_results: int):
        super().__init__()
        self.keywords = keywords
        self.location = location
        self.sources = sources
        self.max_results = max_results
        self.hunter = get_job_hunter()

    def run(self):
        try:
            total_sources = len(self.sources)

            for idx, source in enumerate(self.sources):
                self.progress.emit(int((idx / total_sources) * 100), f"Scraping {source}...")

                jobs = self.hunter.search_jobs(
                    keywords=self.keywords,
                    location=self.location,
                    sources=[source],
                    max_per_source=self.max_results,
                )

            self.progress.emit(100, "Search complete!")
            self.finished.emit(self.hunter.jobs_db)

        except Exception as e:
            self.error.emit(str(e))


class ApplicationWorker(QThread):
    """Background worker for application creation"""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, job_indices: List[int]):
        super().__init__()
        self.job_indices = job_indices
        self.hunter = get_job_hunter()

    def run(self):
        try:
            total = len(self.job_indices)
            results = []

            for idx, job_idx in enumerate(self.job_indices):
                self.progress.emit(
                    int((idx / total) * 100), f"Creating application {idx + 1}/{total}..."
                )

                result = self.hunter.batch_apply([job_idx])
                results.extend(result)

            self.progress.emit(100, "All applications created!")
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))


class JobHunterWidget(QWidget):
    """Main job hunting interface"""

    def __init__(self):
        super().__init__()
        self.logger = setup_logger("jobs.ui")
        self.hunter = get_job_hunter()
        self.resume_tailor = get_resume_tailor()
        self.cover_generator = get_cover_letter_generator()

        self.search_worker: Optional[JobSearchWorker] = None
        self.app_worker: Optional[ApplicationWorker] = None

        self.init_ui()
        self.refresh_table()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("🎯 Intelligent Job Hunter")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_search_tab(), "🔍 Search Jobs")
        tabs.addTab(self.create_jobs_tab(), "📋 Opportunities")
        tabs.addTab(self.create_applications_tab(), "✍️ Applications")
        tabs.addTab(self.create_stats_tab(), "📊 Statistics")

        layout.addWidget(tabs)

        self.setLayout(layout)

    def create_search_tab(self) -> QWidget:
        """Search configuration panel"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Resume section
        resume_group = QGroupBox("📄 Your Resume")
        resume_layout = QVBoxLayout()

        resume_row = QHBoxLayout()
        self.resume_path_label = QLabel("No resume loaded")
        resume_row.addWidget(self.resume_path_label)

        load_resume_btn = QPushButton("Load Resume")
        load_resume_btn.clicked.connect(self.load_resume)
        resume_row.addWidget(load_resume_btn)

        resume_layout.addLayout(resume_row)
        resume_group.setLayout(resume_layout)
        layout.addWidget(resume_group)

        # Search parameters
        search_group = QGroupBox("🔎 Search Parameters")
        search_layout = QVBoxLayout()

        # Keywords
        keywords_row = QHBoxLayout()
        keywords_row.addWidget(QLabel("Keywords:"))
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Data Science, Machine Learning, NLP")
        keywords_row.addWidget(self.keywords_input)
        search_layout.addLayout(keywords_row)

        # Location
        location_row = QHBoxLayout()
        location_row.addWidget(QLabel("Location:"))
        self.location_input = QLineEdit("France")
        location_row.addWidget(self.location_input)
        search_layout.addLayout(location_row)

        # Job type
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Job Type:"))
        self.job_type_combo = QComboBox()
        self.job_type_combo.addItems(["Internship", "Full-Time", "Contract", "All"])
        type_row.addWidget(self.job_type_combo)
        search_layout.addLayout(type_row)

        # Sources
        sources_row = QHBoxLayout()
        sources_row.addWidget(QLabel("Sources:"))
        self.indeed_check = QCheckBox("Indeed")
        self.indeed_check.setChecked(True)
        self.linkedin_check = QCheckBox("LinkedIn")
        self.wttj_check = QCheckBox("WTTJ")
        self.glassdoor_check = QCheckBox("Glassdoor")
        sources_row.addWidget(self.indeed_check)
        sources_row.addWidget(self.linkedin_check)
        sources_row.addWidget(self.wttj_check)
        sources_row.addWidget(self.glassdoor_check)
        search_layout.addLayout(sources_row)

        # Max results
        max_row = QHBoxLayout()
        max_row.addWidget(QLabel("Max per source:"))
        self.max_results_spin = QSpinBox()
        self.max_results_spin.setRange(10, 200)
        self.max_results_spin.setValue(50)
        max_row.addWidget(self.max_results_spin)
        search_layout.addLayout(max_row)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Search button
        search_btn = QPushButton("🚀 Start Search")
        search_btn.clicked.connect(self.start_search)
        search_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-size: 14px; padding: 10px;"
        )
        layout.addWidget(search_btn)

        # Progress
        self.search_progress = QProgressBar()
        self.search_progress.setVisible(False)
        layout.addWidget(self.search_progress)

        self.search_status = QLabel("")
        layout.addWidget(self.search_status)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_jobs_tab(self) -> QWidget:
        """Jobs list and details"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Actions
        actions_row = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_table)
        actions_row.addWidget(refresh_btn)

        export_btn = QPushButton("📊 Export to Excel")
        export_btn.clicked.connect(self.export_jobs)
        actions_row.addWidget(export_btn)

        actions_row.addStretch()

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_jobs)
        actions_row.addWidget(select_all_btn)

        layout.addLayout(actions_row)

        # Jobs table
        self.jobs_table = QTableWidget()
        self.jobs_table.setColumnCount(8)
        self.jobs_table.setHorizontalHeaderLabels(
            ["✓", "Title", "Company", "Location", "Type", "Source", "Posted", "Match %"]
        )

        header = self.jobs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.jobs_table)

        # Job details
        details_group = QGroupBox("📝 Job Details")
        details_layout = QVBoxLayout()

        self.job_details = QTextEdit()
        self.job_details.setReadOnly(True)
        self.job_details.setMaximumHeight(150)
        details_layout.addWidget(self.job_details)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        self.jobs_table.itemSelectionChanged.connect(self.show_job_details)

        widget.setLayout(layout)
        return widget

    def create_applications_tab(self) -> QWidget:
        """Application creation and management"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Instructions
        info = QLabel("Select jobs from the Opportunities tab, then create applications here")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Create button
        create_btn = QPushButton("✍️ Create Applications for Selected Jobs")
        create_btn.clicked.connect(self.create_applications)
        create_btn.setStyleSheet(
            "background-color: #2196F3; color: white; font-size: 14px; padding: 10px;"
        )
        layout.addWidget(create_btn)

        # Progress
        self.app_progress = QProgressBar()
        self.app_progress.setVisible(False)
        layout.addWidget(self.app_progress)

        self.app_status = QLabel("")
        layout.addWidget(self.app_status)

        # Results
        results_group = QGroupBox("📦 Generated Applications")
        results_layout = QVBoxLayout()

        self.app_results = QTextEdit()
        self.app_results.setReadOnly(True)
        results_layout.addWidget(self.app_results)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        widget.setLayout(layout)
        return widget

    def create_stats_tab(self) -> QWidget:
        """Statistics and analytics"""
        widget = QWidget()
        layout = QVBoxLayout()

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)

        refresh_stats_btn = QPushButton("🔄 Refresh Statistics")
        refresh_stats_btn.clicked.connect(self.refresh_stats)
        layout.addWidget(refresh_stats_btn)

        widget.setLayout(layout)
        return widget

    def load_resume(self):
        """Load user's resume"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Resume",
            "",
            "Text Files (*.txt *.md);;PDF Files (*.pdf);;Word Files (*.docx);;All Files (*.*)",
        )

        if file_path:
            try:
                self.hunter.load_resume(file_path)
                self.resume_path_label.setText(f"✅ Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load resume: {e}")

    def start_search(self):
        """Start job search"""
        # Get parameters
        keywords_text = self.keywords_input.text().strip()
        if not keywords_text:
            QMessageBox.warning(self, "Missing Keywords", "Please enter search keywords")
            return

        keywords = [k.strip() for k in keywords_text.split(",")]
        location = self.location_input.text().strip()

        sources = []
        if self.indeed_check.isChecked():
            sources.append("indeed")
        if self.linkedin_check.isChecked():
            sources.append("linkedin")
        if self.wttj_check.isChecked():
            sources.append("wttj")
        if self.glassdoor_check.isChecked():
            sources.append("glassdoor")

        if not sources:
            QMessageBox.warning(self, "No Sources", "Please select at least one job source")
            return

        max_results = self.max_results_spin.value()

        # Start worker
        self.search_worker = JobSearchWorker(keywords, location, sources, max_results)
        self.search_worker.progress.connect(self.update_search_progress)
        self.search_worker.finished.connect(self.search_finished)
        self.search_worker.error.connect(self.search_error)

        self.search_progress.setVisible(True)
        self.search_worker.start()

    def update_search_progress(self, value: int, status: str):
        """Update search progress"""
        self.search_progress.setValue(value)
        self.search_status.setText(status)

    def search_finished(self, jobs: List[JobOpportunity]):
        """Search completed"""
        self.search_progress.setVisible(False)
        self.refresh_table()
        QMessageBox.information(self, "Search Complete", f"Found {len(jobs)} job opportunities!")

    def search_error(self, error: str):
        """Search failed"""
        self.search_progress.setVisible(False)
        QMessageBox.critical(self, "Search Error", error)

    def refresh_table(self):
        """Refresh jobs table"""
        jobs = self.hunter.jobs_db

        self.jobs_table.setRowCount(len(jobs))

        for row, job in enumerate(jobs):
            # Checkbox
            check = QCheckBox()
            if job.applied:
                check.setChecked(True)
                check.setEnabled(False)
            self.jobs_table.setCellWidget(row, 0, check)

            # Data
            self.jobs_table.setItem(row, 1, QTableWidgetItem(job.title))
            self.jobs_table.setItem(row, 2, QTableWidgetItem(job.company))
            self.jobs_table.setItem(row, 3, QTableWidgetItem(job.location))
            self.jobs_table.setItem(row, 4, QTableWidgetItem(job.job_type))
            self.jobs_table.setItem(row, 5, QTableWidgetItem(job.source))
            self.jobs_table.setItem(row, 6, QTableWidgetItem(job.posted_date))

            # Match score (if resume loaded)
            if self.hunter.resume_text:
                score = self.resume_tailor.calculate_match_score(
                    self.hunter.resume_text, job.description
                )
                self.jobs_table.setItem(row, 7, QTableWidgetItem(f"{score}%"))

    def select_all_jobs(self):
        """Select all non-applied jobs"""
        for row in range(self.jobs_table.rowCount()):
            check = self.jobs_table.cellWidget(row, 0)
            if check and check.isEnabled():
                check.setChecked(True)

    def show_job_details(self):
        """Show selected job details"""
        selected = self.jobs_table.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        if row >= len(self.hunter.jobs_db):
            return

        job = self.hunter.jobs_db[row]

        details = f"""**{job.title}**
**Company:** {job.company}
**Location:** {job.location}
**Type:** {job.job_type}
**Posted:** {job.posted_date}
**URL:** {job.url}

**Description:**
{job.description}

**Requirements:**
{job.requirements}
"""

        self.job_details.setPlainText(details)

    def export_jobs(self):
        """Export jobs to Excel"""
        if not self.hunter.jobs_db:
            QMessageBox.warning(self, "No Jobs", "No jobs to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Excel File",
            f"jobs_{datetime.now().strftime('%Y%m%d')}.xlsx",
            "Excel Files (*.xlsx)",
        )

        if file_path:
            try:
                self.hunter.export_to_excel(output_path=file_path)
                QMessageBox.information(self, "Export Success", f"Exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def create_applications(self):
        """Create applications for selected jobs"""
        if not self.hunter.resume_text:
            QMessageBox.warning(
                self, "No Resume", "Please load your resume first in the Search tab"
            )
            return

        # Get selected jobs
        selected_indices = []
        for row in range(self.jobs_table.rowCount()):
            check = self.jobs_table.cellWidget(row, 0)
            if check and check.isChecked() and check.isEnabled():
                selected_indices.append(row)

        if not selected_indices:
            QMessageBox.warning(self, "No Selection", "Please select jobs to apply to")
            return

        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirm",
            f"Create applications for {len(selected_indices)} jobs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # Start worker
        self.app_worker = ApplicationWorker(selected_indices)
        self.app_worker.progress.connect(self.update_app_progress)
        self.app_worker.finished.connect(self.applications_finished)
        self.app_worker.error.connect(self.applications_error)

        self.app_progress.setVisible(True)
        self.app_worker.start()

    def update_app_progress(self, value: int, status: str):
        """Update application progress"""
        self.app_progress.setValue(value)
        self.app_status.setText(status)

    def applications_finished(self, results: list):
        """Applications created"""
        self.app_progress.setVisible(False)

        # Show results
        success = [r for r in results if r.get("status") == "success"]
        failed = [r for r in results if r.get("status") == "failed"]

        result_text = f"✅ **Created {len(success)} applications**\n\n"

        for r in success:
            job = r["job"]
            result_text += f"**{job['company']}** - {job['title']}\n"
            result_text += f"  Resume: {r['resume_path']}\n"
            result_text += f"  Cover Letter: {r['cover_letter_path']}\n\n"

        if failed:
            result_text += f"\n❌ **Failed: {len(failed)}**\n"
            for r in failed:
                result_text += f"  Job {r['job_index']}: {r['error']}\n"

        self.app_results.setPlainText(result_text)
        self.refresh_table()

        QMessageBox.information(
            self,
            "Complete",
            f"Created {len(success)} applications\nCheck the Applications tab for details",
        )

    def applications_error(self, error: str):
        """Application creation failed"""
        self.app_progress.setVisible(False)
        QMessageBox.critical(self, "Error", error)

    def refresh_stats(self):
        """Refresh statistics"""
        stats = self.hunter.get_statistics()

        stats_text = f"""# 📊 Job Hunting Statistics

## Overview
- **Total Jobs Found:** {stats['total_jobs']}
- **Applications Created:** {stats['applied']}
- **Pending:** {stats['pending']}
- **Resume Loaded:** {'✅ Yes' if stats['resume_loaded'] else '❌ No'}

## By Source
"""

        for source, count in stats["by_source"].items():
            stats_text += f"- **{source}:** {count} jobs\n"

        stats_text += "\n## By Type\n"

        for job_type, count in stats["by_type"].items():
            stats_text += f"- **{job_type}:** {count} jobs\n"

        self.stats_text.setPlainText(stats_text)


def main():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("XENO Job Hunter")
    window.setGeometry(100, 100, 1200, 800)

    widget = JobHunterWidget()
    window.setCentralWidget(widget)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
