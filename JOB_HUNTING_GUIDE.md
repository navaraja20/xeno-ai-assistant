# 🎯 Job Hunting Guide - Find Your Data Science Internship

## 📋 Overview

This guide will help you use XENO to find and apply to Data Science internships in France with AI-powered resume tailoring and cover letter generation.

---

## 🚀 Prerequisites

### 1. Setup AI Agent
Follow `AI_SETUP.md` to setup either:
- **Ollama** (local, free, private) - Recommended
- **Gemini** (cloud, powerful)
- **Both** (best of both worlds)

### 2. Prepare Your Resume
Create a text file with your resume:

**Example: `my_resume.txt`**
```
[Your Name]
Data Science Master's Student at EPITA

Email: your@email.com | Phone: +33 X XX XX XX XX
LinkedIn: linkedin.com/in/yourprofile | GitHub: github.com/yourusername

SUMMARY
Passionate Data Science student with strong background in Machine Learning, 
Deep Learning, and NLP. Proficient in Python, TensorFlow, PyTorch. Seeking 
internship to apply theoretical knowledge to real-world problems.

EDUCATION
Master's in Data Science, EPITA (2024-2025)
- Relevant Coursework: ML, DL, NLP, Computer Vision, Big Data Analytics
- GPA: 3.8/4.0

Bachelor's in Computer Science, [University] (2020-2024)

TECHNICAL SKILLS
- Languages: Python, R, SQL, Java, JavaScript
- ML/DL: TensorFlow, PyTorch, Keras, scikit-learn
- Data: Pandas, NumPy, Matplotlib, Seaborn, Plotly
- Big Data: Spark, Hadoop
- Cloud: AWS, Azure, GCP basics
- Tools: Git, Docker, Jupyter, VS Code

PROJECTS
Sentiment Analysis System (2024)
- Built BERT-based model achieving 92% accuracy on Twitter data
- Processed 1M+ tweets using PySpark for distributed computing
- Deployed REST API on AWS Lambda with Flask
- Tech: Python, PyTorch, BERT, PySpark, AWS, Flask

Image Classification for Medical Diagnosis (2023)
- Trained ResNet50 on custom medical image dataset
- Achieved 95% validation accuracy with data augmentation
- Implemented transfer learning to reduce training time
- Tech: Python, TensorFlow, Keras, OpenCV

NLP Chatbot for Customer Service (2023)
- Developed intent classification system with 88% accuracy
- Integrated with DialogFlow for conversational flow
- Processed 10K+ customer queries
- Tech: Python, spaCy, TensorFlow, DialogFlow

EXPERIENCE
Data Science Intern - [Company Name] (Summer 2023)
- Built predictive models improving customer retention by 15%
- Analyzed 500K+ data points to identify key patterns
- Presented findings to senior management
- Tech: Python, scikit-learn, Pandas, Tableau

Teaching Assistant - EPITA (2024)
- Assisted 50+ students in Machine Learning coursework
- Conducted weekly lab sessions on Python and scikit-learn
- Developed course materials and exercises

CERTIFICATIONS
- Machine Learning Specialization (Coursera, Stanford)
- Deep Learning Specialization (Coursera, deeplearning.ai)
- TensorFlow Developer Certificate (Google)

LANGUAGES
- French: Native
- English: Fluent (C1)
- [Other]: Basic/Intermediate

INTERESTS
AI Research, Open Source Contribution, Kaggle Competitions
```

**Tips:**
- Use plain text (.txt) or Markdown (.md)
- Include quantifiable achievements ("improved by 15%")
- List all technical skills
- Keep it truthful - AI will customize, not fabricate
- Save as: `E:\my_resume.txt`

---

## 🔍 Step 1: Search for Jobs

### Interactive Method (GUI)
```powershell
cd "E:\Personal assistant"
python demos\demo_job_hunter.py
# Choose option 4: Launch Full GUI
```

1. Click "Load Resume" → Select your `my_resume.txt`
2. Enter keywords: `Data Science, Machine Learning, NLP, Deep Learning`
3. Location: `France`
4. Check job sources: Indeed, LinkedIn, etc.
5. Click "Start Search"
6. Wait for scraping to complete

### Python Method (Script)
```python
from src.jobs.job_hunter import get_job_hunter

# Initialize
hunter = get_job_hunter()

# Load your resume
hunter.load_resume("E:/my_resume.txt")

# Search jobs
jobs = hunter.search_jobs(
    keywords=[
        "Data Science",
        "Machine Learning",
        "Deep Learning",
        "NLP",
        "Data Analyst",
    ],
    location="France",
    job_types=["internship"],
    sources=["indeed"],  # Add more when available: "linkedin", "wttj"
    max_per_source=100
)

print(f"Found {len(jobs)} opportunities!")

# Export to Excel
excel_path = hunter.export_to_excel("E:/jobs/data_science_internships.xlsx")
print(f"Exported to: {excel_path}")
```

---

## 📊 Step 2: Review Jobs in Excel

1. **Open Excel file**
   ```
   E:\jobs\data_science_internships.xlsx
   ```

2. **Columns explained:**
   - **Title**: Job title
   - **Company**: Company name
   - **Location**: City, France
   - **Type**: internship, full-time, etc.
   - **Description**: Job description summary
   - **Requirements**: Key requirements
   - **Posted**: Date posted
   - **URL**: Link to job posting
   - **Source**: Indeed, LinkedIn, etc.
   - **Match %**: How well your resume matches (if calculated)

3. **Filter & Sort:**
   - Filter by Location (Paris, Lyon, etc.)
   - Sort by Match % (highest first)
   - Sort by Posted Date (newest first)

4. **Mark Jobs to Apply:**
   - Add a column "Apply"
   - Mark "Yes" for jobs you want
   - Or just note the row numbers (0, 5, 12, etc.)

**Example Selection:**
```
Row 0: ML Intern at TechCorp (Paris) - Match 85%
Row 5: Data Science Intern at StartupX (Lyon) - Match 78%
Row 12: NLP Intern at ResearchLab (Toulouse) - Match 90%
Row 18: AI Intern at BigCo (Paris) - Match 82%
Row 23: Data Analyst Intern at FinTech (Paris) - Match 75%
```

---

## ✍️ Step 3: Create Applications

### Method 1: Batch Apply (Python)
```python
from src.jobs.job_hunter import get_job_hunter

hunter = get_job_hunter()

# Apply to selected jobs (by row number from Excel)
results = hunter.batch_apply([0, 5, 12, 18, 23])

# Check results
for r in results:
    if r['status'] == 'success':
        job = r['job']
        print(f"\n✅ Application created for {job['company']}")
        print(f"   Position: {job['title']}")
        print(f"   Resume: {r['resume_path']}")
        print(f"   Cover Letter: {r['cover_letter_path']}")
    else:
        print(f"\n❌ Failed: {r.get('error')}")
```

### Method 2: GUI
1. Open Job Hunter GUI
2. Go to "Opportunities" tab
3. Select checkboxes for jobs you want
4. Go to "Applications" tab
5. Click "Create Applications for Selected Jobs"
6. Wait for AI to tailor resumes and generate cover letters
7. Check results in "Generated Applications" section

---

## 📁 Step 4: Review Generated Applications

### Location
```
E:\Personal assistant\data\jobs\applications\
```

### Files Created (per job)
```
TechCorp_20240115_resume.md
TechCorp_20240115_cover_letter.md

StartupX_20240115_resume.md
StartupX_20240115_cover_letter.md

...etc
```

### What AI Did:

**For Each Resume:**
- ✅ Analyzed job description
- ✅ Identified key requirements
- ✅ Highlighted matching skills from your resume
- ✅ Reordered sections to emphasize relevant experience
- ✅ Added keywords from job posting
- ✅ Kept it ATS-friendly
- ✅ Maintained truthfulness

**For Each Cover Letter:**
- ✅ Researched company (from job posting)
- ✅ Explained why you're interested in THIS role
- ✅ Highlighted 2-3 most relevant experiences
- ✅ Used specific examples with results
- ✅ Professional but personal tone
- ✅ Strong call to action

---

## 📝 Step 5: Finalize Applications

### Review AI Output
1. **Read Resume**
   - Check for accuracy
   - Ensure all info is correct
   - Verify skills match
   - No fabricated experience

2. **Read Cover Letter**
   - Personalized to company?
   - Specific examples?
   - Proper tone?
   - No generic phrases?

3. **Make Edits**
   - Add personal touch
   - Fix any errors
   - Adjust tone if needed

### Convert to PDF
```python
# Option 1: Use pandoc (install first)
# https://pandoc.org/installing.html

import os

def md_to_pdf(md_file):
    pdf_file = md_file.replace('.md', '.pdf')
    os.system(f'pandoc {md_file} -o {pdf_file}')
    return pdf_file

# Convert all resumes and cover letters
import glob

app_dir = "E:/Personal assistant/data/jobs/applications/"
md_files = glob.glob(f"{app_dir}*.md")

for md in md_files:
    pdf = md_to_pdf(md)
    print(f"Created: {pdf}")
```

**Or use online converters:**
- https://www.markdowntopdf.com/
- https://dillinger.io/ (export to PDF)
- Copy to Google Docs → Download as PDF

---

## 📧 Step 6: Submit Applications

### For Each Job:

1. **Visit Job URL**
   - Get from Excel file
   - Open in browser

2. **Fill Application Form**
   - Personal info
   - Education
   - Upload resume (PDF)
   - Upload cover letter (PDF)

3. **LinkedIn Easy Apply**
   - If available, use it
   - Faster process
   - Same PDF files

4. **Track Application**
   ```python
   from src.jobs.job_hunter import get_job_hunter
   
   hunter = get_job_hunter()
   stats = hunter.get_statistics()
   print(stats)
   ```

---

## 📊 Step 7: Track Progress

### View Statistics
```python
from src.jobs.job_hunter import get_job_hunter

hunter = get_job_hunter()
stats = hunter.get_statistics()

print(f"Total Jobs Found: {stats['total_jobs']}")
print(f"Applications Created: {stats['applied']}")
print(f"Pending: {stats['pending']}")

print("\nBy Source:")
for source, count in stats['by_source'].items():
    print(f"  {source}: {count} jobs")

print("\nBy Type:")
for type, count in stats['by_type'].items():
    print(f"  {type}: {count} jobs")
```

### Update Application Status
```python
# In future updates, track:
# - Application submitted
# - Interview scheduled
# - Rejection received
# - Offer received
```

---

## 💡 Tips for Success

### Job Search Strategy

1. **Cast Wide Net**
   - Search 50-100 jobs initially
   - Filter to 20-30 best matches
   - Apply to 10-15 top choices

2. **Keywords Matter**
   - Use variations: "Data Science", "Data Scientist", "ML Engineer"
   - Include specific skills: "NLP", "Deep Learning", "Computer Vision"
   - Try related roles: "Data Analyst", "Research Intern"

3. **Location Strategy**
   - Focus on major cities: Paris, Lyon, Toulouse, Nantes
   - Consider remote opportunities
   - Check "Location" in Excel before applying

### Resume Optimization

1. **Keep Base Resume Strong**
   - General but comprehensive
   - All skills and projects
   - Let AI customize per job

2. **Quantify Everything**
   - "Improved accuracy by 15%"
   - "Processed 1M+ data points"
   - "Reduced time by 30%"

3. **Technical Skills**
   - List ALL relevant skills
   - Specific frameworks/tools
   - AI will match to job requirements

### Cover Letter Tips

1. **Review AI Output**
   - Check company name is correct
   - Ensure examples are relevant
   - Verify tone is professional

2. **Add Personal Touch**
   - Why THIS company specifically?
   - Any connections or insights?
   - Genuine enthusiasm

3. **Call to Action**
   - Request interview
   - Express interest in discussion
   - Provide contact info

### Application Best Practices

1. **Quality Control**
   - Read before sending
   - Check for errors
   - Verify company name
   - Correct position title

2. **Timing**
   - Apply within 24-48 hours of posting
   - Early applications get more attention
   - Set up alerts for new jobs

3. **Follow Up**
   - Wait 1 week
   - Send polite follow-up email
   - Express continued interest

---

## 🔄 Workflow Summary

```
1. Load Resume → XENO
2. Search Jobs → Indeed, LinkedIn, etc.
3. Export to Excel → Review & Select
4. Batch Apply → AI tailors resume + cover letter
5. Review Output → Check accuracy
6. Convert to PDF → Professional format
7. Submit Applications → Via job sites
8. Track Progress → Monitor responses
9. Follow Up → After 1 week
10. Interview! → Prepare and succeed
```

---

## 📈 Expected Results

### Timeline
- **Day 1**: Setup XENO, search jobs (100+)
- **Day 2**: Review jobs, select 20-30
- **Day 3**: Create applications (AI does heavy lifting)
- **Day 4-5**: Review, finalize, convert to PDF
- **Day 6-7**: Submit applications
- **Week 2+**: Follow up, interviews

### Success Metrics
- **Applications**: 10-20 tailored applications
- **Response Rate**: 20-30% (industry average)
- **Interviews**: 2-5 per 20 applications
- **Time Saved**: 90% compared to manual tailoring

### What You Save
- **Manual Resume Tailoring**: 1 hour → 5 minutes (AI)
- **Cover Letter Writing**: 45 minutes → 2 minutes (AI)
- **Per Application**: 2 hours → 15 minutes
- **For 20 Applications**: 40 hours → 5 hours 🎉

---

## 🆘 Troubleshooting

### "No jobs found"
- Broaden keywords
- Try different cities
- Increase `max_per_source`
- Check internet connection

### "Resume tailoring failed"
- Verify AI is setup (Ollama or Gemini)
- Check resume format (plain text)
- Try simpler resume structure
- Check AI status: `agent.get_status()`

### "Cover letter too generic"
- Review AI output carefully
- Add personal touches manually
- Provide more context in base resume
- Use better job descriptions (more detailed)

### "Match score too low"
- Add missing skills to resume
- Use job-specific keywords
- Highlight relevant projects
- Consider if job is good fit

---

## 📚 Additional Resources

### Job Sites (Manual Search)
- Indeed France: https://fr.indeed.com
- LinkedIn Jobs: https://linkedin.com/jobs
- Welcome to the Jungle: https://welcometothejungle.com/fr
- Glassdoor: https://glassdoor.com
- StepStone: https://stepstone.fr

### Resume Tools
- Grammarly: Check grammar
- Hemingway App: Improve clarity
- Resume.io: ATS checker
- Canva: Visual resume (after AI tailoring)

### Interview Prep
- LeetCode: Coding practice
- Glassdoor: Interview questions
- Kaggle: Data Science projects
- YouTube: Mock interviews

---

## ✅ Checklist

**Before Starting:**
- [ ] AI agent setup (Ollama or Gemini)
- [ ] Resume prepared and saved
- [ ] Job preferences clear (keywords, location)

**During Job Search:**
- [ ] Search multiple job sites
- [ ] Export to Excel
- [ ] Review and filter jobs
- [ ] Note row numbers to apply

**Creating Applications:**
- [ ] Batch apply to selected jobs
- [ ] Review AI-generated resumes
- [ ] Review AI-generated cover letters
- [ ] Make necessary edits

**Submitting:**
- [ ] Convert to PDF
- [ ] Submit via job sites
- [ ] Track submissions
- [ ] Set reminders for follow-up

**Follow Up:**
- [ ] Wait 1 week
- [ ] Send follow-up emails
- [ ] Prepare for interviews
- [ ] Update application status

---

**Good luck with your Data Science internship search! 🚀**

XENO is here to help you every step of the way. Let AI handle the tedious work while you focus on preparing for interviews and building your skills.

**Questions?** Check the troubleshooting section or review `AI_SETUP.md` for AI configuration help.

**Next:** After getting interviews, ask XENO's AI agent to help you prepare! 🎯
