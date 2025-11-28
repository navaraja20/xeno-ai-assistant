"""
Job Hunter Demo
Test the intelligent job hunting system
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication

from src.jobs.job_hunter_ui import JobHunterWidget, QMainWindow


def test_search():
    """Test job search functionality"""
    print("=" * 60)
    print("XENO Job Hunter - Search Test")
    print("=" * 60)

    from src.jobs.job_hunter import get_job_hunter

    hunter = get_job_hunter()

    # Load resume
    print("\n1. Loading sample resume...")
    sample_resume = """John Doe
Data Science Master's Student at EPITA

Email: john@example.com | Phone: +33 6 12 34 56 78

SUMMARY
Passionate Data Science student with strong background in Machine Learning, Deep Learning, and NLP.
Proficient in Python, TensorFlow, PyTorch, and scikit-learn. Seeking internship to apply skills.

EDUCATION
Master's in Data Science, EPITA (2024-2025)
- Courses: ML, DL, NLP, Computer Vision, Big Data
- GPA: 3.8/4.0

SKILLS
- Languages: Python, R, SQL, Java
- ML/DL: TensorFlow, PyTorch, Keras, scikit-learn
- Data: Pandas, NumPy, Matplotlib, Seaborn
- Tools: Git, Docker, Jupyter

PROJECTS
Sentiment Analysis on Twitter Data
- Built BERT-based model with 92% accuracy
- Processed 1M+ tweets using PySpark
- Deployed on AWS with Flask API

Image Classification System
- Trained ResNet50 on custom dataset
- Achieved 95% validation accuracy
- Implemented data augmentation pipeline
"""

    # Save to temp file
    os.makedirs("data/temp", exist_ok=True)
    resume_path = "data/temp/sample_resume.txt"
    with open(resume_path, "w", encoding="utf-8") as f:
        f.write(sample_resume)

    hunter.load_resume(resume_path)
    print("✅ Resume loaded")

    # Search jobs
    print("\n2. Searching for Data Science internships...")
    jobs = hunter.search_jobs(
        keywords=["Data Science", "Machine Learning"],
        location="France",
        job_types=["internship"],
        sources=["indeed"],
        max_per_source=10,
    )

    print(f"✅ Found {len(jobs)} opportunities")

    # Display results
    print("\n3. Top 5 results:")
    for i, job in enumerate(jobs[:5], 1):
        print(f"\n{i}. {job.title}")
        print(f"   Company: {job.company}")
        print(f"   Location: {job.location}")
        print(f"   Source: {job.source}")
        print(f"   URL: {job.url}")

    # Export to Excel
    print("\n4. Exporting to Excel...")
    excel_path = hunter.export_to_excel()
    print(f"✅ Exported to: {excel_path}")

    # Statistics
    print("\n5. Statistics:")
    stats = hunter.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")


def test_resume_tailoring():
    """Test resume tailoring"""
    print("\n" + "=" * 60)
    print("Resume Tailoring Test")
    print("=" * 60)

    from src.jobs.resume_tailor import get_resume_tailor

    tailor = get_resume_tailor()

    sample_resume = """John Doe
Data Science Student

SKILLS
Python, Machine Learning, TensorFlow, Data Analysis

EXPERIENCE
Data Science Intern - Company X
- Built ML models
- Analyzed data
"""

    job_description = """Data Science Internship
We're looking for a student with:
- Strong Python skills
- Experience with NLP and Deep Learning
- Knowledge of PyTorch
- Data visualization skills

You will:
- Build NLP models for text classification
- Work with large datasets
- Create data visualizations
"""

    print("\n1. Original Resume:")
    print(sample_resume[:200] + "...")

    print("\n2. Job Description:")
    print(job_description[:200] + "...")

    print("\n3. Calculating match score...")
    score = tailor.calculate_match_score(sample_resume, job_description)
    print(f"✅ Match Score: {score}%")

    print("\n4. Getting improvement suggestions...")
    suggestions = tailor.suggest_improvements(sample_resume, job_description)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")


def test_cover_letter():
    """Test cover letter generation"""
    print("\n" + "=" * 60)
    print("Cover Letter Generation Test")
    print("=" * 60)

    from src.jobs.cover_letter_generator import get_cover_letter_generator

    generator = get_cover_letter_generator()

    sample_resume = "John Doe\nData Science Student\nSkills: Python, ML, NLP"
    job_description = "Data Science Intern - Build NLP models"

    print("\n1. Generating cover letter...")
    print("   Company: TechCorp")
    print("   Position: Data Science Intern")

    # Note: This requires AI agent to be configured
    print("\n⚠️  Cover letter generation requires AI agent configuration")
    print("   (Will be available once AI agent is complete)")


def main():
    """Main demo"""
    print(
        """
╔══════════════════════════════════════════════════════════╗
║         XENO Job Hunter - Interactive Demo              ║
╚══════════════════════════════════════════════════════════╝

This demo showcases the intelligent job hunting system:

1. 🔍 Multi-site job scraping (Indeed, LinkedIn, etc.)
2. 📊 Excel export with job details
3. 🎯 AI-powered resume tailoring
4. ✍️  Automated cover letter generation
5. 📈 Match scoring and suggestions
6. 🖥️  Full GUI application

Choose a demo:
[1] Test Job Search (scrape Indeed)
[2] Test Resume Tailoring
[3] Test Cover Letter Generation
[4] Launch Full GUI
[0] Exit
"""
    )

    while True:
        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            test_search()

        elif choice == "2":
            test_resume_tailoring()

        elif choice == "3":
            test_cover_letter()

        elif choice == "4":
            print("\n🚀 Launching GUI...")
            app = QApplication(sys.argv)

            window = QMainWindow()
            window.setWindowTitle("XENO Job Hunter")
            window.setGeometry(100, 100, 1200, 800)

            widget = JobHunterWidget()
            window.setCentralWidget(widget)

            window.show()
            sys.exit(app.exec())

        elif choice == "0":
            print("\nGoodbye! 👋")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
