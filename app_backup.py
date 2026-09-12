from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import re
from datetime import datetime

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "career_analyzer.db")


# ============================================================
# CAREER PROFILES
# ============================================================

CAREER_PROFILES = {

    "Data Analyst": {
        "skills": {
            "Python": 10,
            "SQL": 10,
            "Excel": 9,
            "Power BI": 9,
            "Tableau": 8,
            "Statistics": 9,
            "Pandas": 8,
            "NumPy": 7,
            "Data Visualization": 8,
            "Data Cleaning": 8
        }
    },

    "Data Scientist": {
        "skills": {
            "Python": 10,
            "SQL": 8,
            "Machine Learning": 10,
            "Statistics": 9,
            "Pandas": 8,
            "NumPy": 8,
            "Scikit-learn": 9,
            "Data Visualization": 7,
            "Deep Learning": 8,
            "TensorFlow": 7
        }
    },

    "Machine Learning Engineer": {
        "skills": {
            "Python": 10,
            "Machine Learning": 10,
            "Deep Learning": 9,
            "TensorFlow": 8,
            "PyTorch": 8,
            "Scikit-learn": 9,
            "SQL": 7,
            "Git": 8,
            "Docker": 8,
            "NLP": 7
        }
    },

    "AI Engineer": {
        "skills": {
            "Python": 10,
            "Machine Learning": 10,
            "Deep Learning": 9,
            "NLP": 9,
            "TensorFlow": 8,
            "PyTorch": 8,
            "Generative AI": 9,
            "LLM": 9,
            "Git": 7,
            "Docker": 7
        }
    },

    "Web Developer": {
        "skills": {
            "HTML": 10,
            "CSS": 10,
            "JavaScript": 10,
            "React": 9,
            "Node.js": 8,
            "Git": 8,
            "REST API": 8,
            "Bootstrap": 7,
            "MongoDB": 7,
            "Responsive Design": 8
        }
    },

    "Frontend Developer": {
        "skills": {
            "HTML": 10,
            "CSS": 10,
            "JavaScript": 10,
            "React": 10,
            "Bootstrap": 8,
            "Responsive Design": 9,
            "Git": 8,
            "TypeScript": 7,
            "UI/UX": 7
        }
    },

    "Backend Developer": {
        "skills": {
            "Python": 8,
            "Java": 9,
            "Node.js": 9,
            "SQL": 10,
            "REST API": 10,
            "Git": 8,
            "Docker": 8,
            "MongoDB": 8,
            "MySQL": 9,
            "Flask": 8
        }
    },

    "Full Stack Developer": {
        "skills": {
            "HTML": 9,
            "CSS": 9,
            "JavaScript": 10,
            "React": 9,
            "Node.js": 9,
            "Python": 8,
            "SQL": 9,
            "MongoDB": 8,
            "Git": 9,
            "REST API": 9
        }
    },

    "Software Developer": {
        "skills": {
            "Java": 10,
            "Python": 9,
            "C++": 8,
            "Data Structures": 10,
            "Algorithms": 10,
            "OOP": 9,
            "SQL": 8,
            "Git": 8,
            "Problem Solving": 9
        }
    },

    "Java Developer": {
        "skills": {
            "Java": 10,
            "OOP": 10,
            "Spring Boot": 9,
            "SQL": 9,
            "REST API": 9,
            "Git": 8,
            "Hibernate": 8,
            "Maven": 7,
            "Data Structures": 8
        }
    },

    "Cloud Engineer": {
        "skills": {
            "AWS": 10,
            "Azure": 8,
            "GCP": 8,
            "Linux": 9,
            "Docker": 9,
            "Kubernetes": 10,
            "Git": 8,
            "Networking": 8,
            "CI/CD": 9,
            "Terraform": 8
        }
    },

    "DevOps Engineer": {
        "skills": {
            "Linux": 9,
            "Docker": 10,
            "Kubernetes": 10,
            "AWS": 9,
            "Git": 9,
            "CI/CD": 10,
            "Jenkins": 8,
            "Terraform": 8,
            "Python": 7,
            "Networking": 8
        }
    },

    "Cybersecurity Analyst": {
        "skills": {
            "Cybersecurity": 10,
            "Networking": 9,
            "Linux": 9,
            "Python": 8,
            "Ethical Hacking": 9,
            "Cryptography": 8,
            "SIEM": 8,
            "Firewalls": 8,
            "OWASP": 8
        }
    },

    "Database Administrator": {
        "skills": {
            "SQL": 10,
            "MySQL": 10,
            "Oracle": 9,
            "Database Management": 10,
            "Database Design": 9,
            "Backup": 8,
            "Linux": 7,
            "Performance Tuning": 8
        }
    }
}


# ============================================================
# SKILL ALIASES
# ============================================================

SKILL_ALIASES = {

    "python": "Python",
    "python3": "Python",

    "java": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",

    "c++": "C++",
    "cpp": "C++",
    "c language": "C",

    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",

    "react": "React",
    "reactjs": "React",
    "node": "Node.js",
    "nodejs": "Node.js",

    "sql": "SQL",
    "mysql": "MySQL",
    "oracle": "Oracle",
    "mongodb": "MongoDB",

    "excel": "Excel",
    "microsoft excel": "Excel",

    "power bi": "Power BI",
    "powerbi": "Power BI",
    "tableau": "Tableau",

    "pandas": "Pandas",
    "numpy": "NumPy",

    "statistics": "Statistics",
    "statistical analysis": "Statistics",

    "machine learning": "Machine Learning",
    "ml": "Machine Learning",

    "deep learning": "Deep Learning",
    "dl": "Deep Learning",

    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",

    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",

    "nlp": "NLP",
    "natural language processing": "NLP",

    "generative ai": "Generative AI",
    "gen ai": "Generative AI",
    "llm": "LLM",
    "large language model": "LLM",

    "git": "Git",
    "github": "Git",

    "docker": "Docker",
    "kubernetes": "Kubernetes",

    "aws": "AWS",
    "amazon web services": "AWS",

    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",

    "linux": "Linux",
    "networking": "Networking",

    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "jenkins": "Jenkins",
    "terraform": "Terraform",

    "spring boot": "Spring Boot",
    "spring": "Spring Boot",
    "hibernate": "Hibernate",
    "maven": "Maven",

    "rest api": "REST API",
    "restful api": "REST API",
    "api": "REST API",

    "data structures": "Data Structures",
    "dsa": "Data Structures",
    "algorithms": "Algorithms",
    "algorithm": "Algorithms",

    "oop": "OOP",
    "object oriented programming": "OOP",

    "problem solving": "Problem Solving",

    "data visualization": "Data Visualization",
    "data cleaning": "Data Cleaning",

    "database management": "Database Management",
    "database design": "Database Design",
    "performance tuning": "Performance Tuning",

    "cybersecurity": "Cybersecurity",
    "cyber security": "Cybersecurity",
    "ethical hacking": "Ethical Hacking",
    "ethical hacker": "Ethical Hacking",

    "cryptography": "Cryptography",
    "siem": "SIEM",
    "firewall": "Firewalls",
    "firewalls": "Firewalls",
    "owasp": "OWASP",

    "bootstrap": "Bootstrap",
    "responsive design": "Responsive Design",
    "ui/ux": "UI/UX"
}


# ============================================================
# RELATED SKILLS
# ============================================================

RELATED_SKILLS = {

    "Python": ["Pandas", "NumPy", "Machine Learning", "Flask"],
    "SQL": ["MySQL", "Database Management", "Database Design"],
    "Java": ["OOP", "Spring Boot", "Hibernate", "Maven"],
    "JavaScript": ["React", "Node.js", "TypeScript"],
    "HTML": ["CSS", "Responsive Design", "Bootstrap"],
    "CSS": ["HTML", "Bootstrap", "Responsive Design"],
    "Machine Learning": ["Python", "Statistics", "Scikit-learn", "Deep Learning"],
    "Deep Learning": ["Machine Learning", "TensorFlow", "PyTorch"],
    "React": ["JavaScript", "HTML", "CSS", "TypeScript"],
    "Docker": ["Kubernetes", "CI/CD", "Linux"],
    "Kubernetes": ["Docker", "Linux", "CI/CD"],
    "AWS": ["Docker", "Linux", "Kubernetes"],
    "Linux": ["Docker", "Networking", "AWS"],
    "Data Visualization": ["Power BI", "Tableau", "Excel"],
    "Pandas": ["Python", "NumPy", "Data Cleaning"],
    "NumPy": ["Python", "Pandas", "Statistics"]
}


# ============================================================
# OPPORTUNITIES
# ============================================================

OPPORTUNITIES = [

    {
        "type": "Internship",
        "title": "Data & AI Internships",
        "platform": "Unstop",
        "icon": "🎓",
        "skills": ["Python", "SQL", "Pandas", "Machine Learning"],
        "url": "https://unstop.com/internships"
    },

    {
        "type": "Internship",
        "title": "Software Development Internships",
        "platform": "Unstop",
        "icon": "💻",
        "skills": ["Java", "Python", "JavaScript", "Git"],
        "url": "https://unstop.com/internships"
    },

    {
        "type": "Remote Job",
        "title": "Remote Software Jobs",
        "platform": "Wellfound",
        "icon": "🌐",
        "skills": ["Python", "Java", "JavaScript", "React", "SQL"],
        "url": "https://wellfound.com/jobs"
    },

    {
        "type": "Remote Job",
        "title": "Remote Data Jobs",
        "platform": "Wellfound",
        "icon": "📊",
        "skills": ["Python", "SQL", "Excel", "Power BI", "Machine Learning"],
        "url": "https://wellfound.com/jobs"
    },

    {
        "type": "Hackathon",
        "title": "AI & Technology Hackathons",
        "platform": "Devfolio",
        "icon": "🏆",
        "skills": ["Python", "Machine Learning", "JavaScript", "React"],
        "url": "https://devfolio.co/hackathons"
    },

    {
        "type": "Hackathon",
        "title": "Web Development Hackathons",
        "platform": "Devfolio",
        "icon": "🚀",
        "skills": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
        "url": "https://devfolio.co/hackathons"
    }
]


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_name TEXT NOT NULL,
            target_career TEXT NOT NULL,
            keyword_score REAL NOT NULL,
            ai_semantic_score REAL NOT NULL,
            final_score REAL NOT NULL,
            analyzed_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(file):

    if PdfReader is None:
        raise RuntimeError(
            "pypdf is not installed. Run: pip install pypdf"
        )

    reader = PdfReader(file)

    text_parts = []

    for page in reader.pages:

        try:
            text = page.extract_text() or ""
            text_parts.append(text)
        except Exception:
            continue

    return "\n".join(text_parts)


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    text = text.lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(r"\s+", " ", text)

    return text


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skills(text):

    normalized = normalize_text(text)

    found = set()

    for alias, canonical in SKILL_ALIASES.items():

        pattern = r"(?<![a-z0-9+#.-])" + re.escape(alias) + r"(?![a-z0-9+#.-])"

        if re.search(pattern, normalized):

            found.add(canonical)

    return sorted(found)


# ============================================================
# KEYWORD MATCHING
# ============================================================

def calculate_keyword_score(existing_skills, career):

    profile = CAREER_PROFILES[career]["skills"]

    total_weight = sum(profile.values())

    matched_weight = 0

    for skill in existing_skills:

        if skill in profile:
            matched_weight += profile[skill]

    if total_weight == 0:
        return 0

    score = (matched_weight / total_weight) * 100

    return round(min(score, 100), 2)


# ============================================================
# SEMANTIC / RELATED SKILL SCORE
# ============================================================

def calculate_semantic_score(existing_skills, career):

    profile = CAREER_PROFILES[career]["skills"]

    exact_weight = 0
    related_weight = 0

    total_weight = sum(profile.values())

    existing_set = set(existing_skills)

    for skill in existing_set:

        if skill in profile:

            exact_weight += profile[skill]

        else:

            related = RELATED_SKILLS.get(skill, [])

            for related_skill in related:

                if related_skill in profile:

                    related_weight += profile[related_skill] * 0.35
                    break

    combined = exact_weight + related_weight

    if total_weight == 0:
        return 0

    score = (combined / total_weight) * 100

    return round(min(score, 100), 2)


# ============================================================
# FINAL SCORE
# ============================================================

def calculate_final_score(keyword_score, semantic_score):

    final = (keyword_score * 0.60) + (semantic_score * 0.40)

    return round(min(final, 100), 2)


# ============================================================
# CAREER LEVEL
# ============================================================

def get_level(score):

    if score >= 85:
        return "Advanced"

    if score >= 65:
        return "Intermediate"

    if score >= 40:
        return "Developing"

    return "Beginner"


# ============================================================
# CAREER RECOMMENDATIONS
# ============================================================

def get_career_recommendations(existing_skills):

    recommendations = []

    for career, profile_data in CAREER_PROFILES.items():

        profile = profile_data["skills"]

        total_weight = sum(profile.values())

        matched_weight = 0
        related_weight = 0

        for skill in existing_skills:

            if skill in profile:

                matched_weight += profile[skill]

            else:

                related = RELATED_SKILLS.get(skill, [])

                for related_skill in related:

                    if related_skill in profile:

                        related_weight += profile[related_skill] * 0.30
                        break

        score = ((matched_weight + related_weight) / total_weight) * 100

        score = round(min(score, 100), 2)

        recommendations.append({
            "career": career,
            "score": score
        })

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return recommendations


# ============================================================
# MISSING SKILLS
# ============================================================

def get_missing_skills(existing_skills, career):

    profile = CAREER_PROFILES[career]["skills"]

    existing_set = set(existing_skills)

    missing = []

    for skill in profile:

        if skill not in existing_set:

            missing.append(skill)

    missing.sort(
        key=lambda x: profile[x],
        reverse=True
    )

    return missing


# ============================================================
# ROADMAP
# ============================================================

def generate_roadmap(existing_skills, career):

    profile = CAREER_PROFILES[career]["skills"]

    existing_set = set(existing_skills)

    roadmap = []

    for skill, weight in sorted(
        profile.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        if skill in existing_set:
            continue

        if weight >= 9:
            priority = "High"

        elif weight >= 7:
            priority = "Medium"

        else:
            priority = "Low"

        roadmap.append({
            "skill": skill,
            "priority": priority,
            "action": get_learning_action(skill)
        })

    return roadmap[:8]


# ============================================================
# LEARNING ACTION
# ============================================================

def get_learning_action(skill):

    actions = {

        "Python":
            "Learn Python fundamentals, functions, OOP and build a practical project.",

        "SQL":
            "Practice SELECT, JOIN, GROUP BY, subqueries and database projects.",

        "Excel":
            "Practice formulas, PivotTables, charts and data-cleaning workflows.",

        "Power BI":
            "Learn dashboards, Power Query, DAX and create an analytics dashboard.",

        "Tableau":
            "Build interactive dashboards and practice data visualization.",

        "Machine Learning":
            "Study supervised and unsupervised learning and build ML projects.",

        "Statistics":
            "Learn probability, distributions, hypothesis testing and regression.",

        "Pandas":
            "Practice DataFrame operations, filtering, grouping and data cleaning.",

        "NumPy":
            "Practice arrays, vectorization and numerical computations.",

        "Java":
            "Practice Java OOP, collections, exception handling and build applications.",

        "OOP":
            "Practice encapsulation, inheritance, polymorphism and abstraction.",

        "Data Structures":
            "Practice arrays, linked lists, stacks, queues, trees and hash tables.",

        "Algorithms":
            "Practice sorting, searching, recursion and algorithmic problem solving.",

        "HTML":
            "Build semantic and responsive web pages using HTML5.",

        "CSS":
            "Practice layouts, Flexbox, Grid, responsive design and animations.",

        "JavaScript":
            "Practice DOM manipulation, events, ES6 and asynchronous JavaScript.",

        "React":
            "Build React components, state management and a small frontend project.",

        "Node.js":
            "Build REST APIs using Node.js and connect them to a database.",

        "Git":
            "Practice Git branching, commits, pull requests and GitHub workflows.",

        "Docker":
            "Learn images, containers, Dockerfiles and containerize a project.",

        "Kubernetes":
            "Learn pods, deployments, services and basic Kubernetes orchestration.",

        "AWS":
            "Learn core AWS services and deploy a small cloud application.",

        "Linux":
            "Practice Linux commands, permissions, processes and shell scripting.",

        "Cybersecurity":
            "Learn security fundamentals, common attacks and defensive practices.",

        "Ethical Hacking":
            "Study ethical hacking concepts in legal lab environments.",

        "NLP":
            "Learn text preprocessing, embeddings and basic NLP applications.",

        "Deep Learning":
            "Study neural networks and build an image or text classification project.",

        "TensorFlow":
            "Build and train neural-network models using TensorFlow.",

        "PyTorch":
            "Practice tensors, neural networks and model training with PyTorch.",

        "Generative AI":
            "Learn LLM concepts, prompting and build a small GenAI application.",

        "LLM":
            "Study transformer-based language models and build an LLM-powered project.",

        "REST API":
            "Learn HTTP methods, JSON and build/test REST APIs.",

        "MongoDB":
            "Practice document-based data modeling and CRUD operations.",

        "MySQL":
            "Practice relational schema design, SQL queries and constraints.",

        "Database Management":
            "Learn indexing, transactions, normalization and database administration.",

        "Database Design":
            "Practice ER diagrams, normalization and relational schema design."
    }

    return actions.get(
        skill,
        f"Study {skill}, practice it through exercises and build a small project."
    )


# ============================================================
# OPPORTUNITY MATCHING
# ============================================================

def generate_opportunities(existing_skills):

    existing_set = set(existing_skills)

    results = []

    for opportunity in OPPORTUNITIES:

        required = opportunity["skills"]

        matched = [
            skill for skill in required
            if skill in existing_set
        ]

        missing = [
            skill for skill in required
            if skill not in existing_set
        ]

        if required:

            score = (len(matched) / len(required)) * 100

        else:

            score = 0

        result = dict(opportunity)

        result["matched"] = matched
        result["missing"] = missing
        result["score"] = round(score, 2)

        results.append(result)

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results


# ============================================================
# DATABASE HISTORY
# ============================================================

def save_analysis(
    resume_name,
    career,
    keyword_score,
    semantic_score,
    final_score
):

    conn = get_db()

    conn.execute("""
        INSERT INTO analysis_history
        (
            resume_name,
            target_career,
            keyword_score,
            ai_semantic_score,
            final_score,
            analyzed_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        resume_name,
        career,
        keyword_score,
        semantic_score,
        final_score,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


# ============================================================
# GET HISTORY
# ============================================================

def get_history():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM analysis_history
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

def get_dashboard_data():

    conn = get_db()

    total_row = conn.execute("""
        SELECT COUNT(*) AS total
        FROM analysis_history
    """).fetchone()

    average_row = conn.execute("""
        SELECT AVG(final_score) AS average
        FROM analysis_history
    """).fetchone()

    latest_row = conn.execute("""
        SELECT final_score
        FROM analysis_history
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    chart_rows = conn.execute("""
        SELECT id, final_score
        FROM analysis_history
        ORDER BY id ASC
    """).fetchall()

    conn.close()

    total = total_row["total"] if total_row else 0

    average = (
        average_row["average"]
        if average_row and average_row["average"] is not None
        else 0
    )

    latest = (
        latest_row["final_score"]
        if latest_row
        else 0
    )

    return (
        total,
        round(average, 2),
        latest,
        chart_rows
    )


# ============================================================
# CREATE RESULT
# ============================================================

def analyze_resume(resume_text, career):

    existing_skills = extract_skills(resume_text)

    keyword_score = calculate_keyword_score(
        existing_skills,
        career
    )

    semantic_score = calculate_semantic_score(
        existing_skills,
        career
    )

    final_score = calculate_final_score(
        keyword_score,
        semantic_score
    )

    missing = get_missing_skills(
        existing_skills,
        career
    )

    roadmap = generate_roadmap(
        existing_skills,
        career
    )

    roles = get_career_recommendations(
        existing_skills
    )

    opportunities = generate_opportunities(
        existing_skills
    )

    return {

        "career": career,

        "level": get_level(final_score),

        "score": final_score,

        "keyword_score": keyword_score,

        "ai_score": semantic_score,

        "existing": [
            skill
            for skill in existing_skills
            if skill in CAREER_PROFILES[career]["skills"]
        ],

        "missing": missing,

        "skills": existing_skills,

        "roles": roles,

        "roadmap": roadmap,

        "opportunities": opportunities
    }


# ============================================================
# MAIN ROUTE
# ============================================================

@app.route("/", methods=["GET", "POST"])
def index():

    error = None
    result = None

    jobs = list(CAREER_PROFILES.keys())

    if request.method == "POST":

        resume = request.files.get("resume")
        career = request.form.get("career")

        # ----------------------------------------------------
        # Validate file
        # ----------------------------------------------------

        if not resume:

            error = "Please upload your resume PDF."

        elif not resume.filename:

            error = "Please select a resume PDF."

        elif not resume.filename.lower().endswith(".pdf"):

            error = "Only PDF resumes are supported."

        elif career not in CAREER_PROFILES:

            error = "Please select a valid target career."

        else:

            try:

                resume_text = extract_pdf_text(resume)

                if not resume_text.strip():

                    error = (
                        "Could not extract text from this PDF. "
                        "Please upload a text-based PDF resume."
                    )

                else:

                    result = analyze_resume(
                        resume_text,
                        career
                    )

                    save_analysis(
                        resume.filename,
                        career,
                        result["keyword_score"],
                        result["ai_score"],
                        result["score"]
                    )

            except Exception as e:

                error = f"Analysis failed: {str(e)}"

    # --------------------------------------------------------
    # Dashboard
    # --------------------------------------------------------

    history = get_history()

    total, average, latest, chart_history = (
        get_dashboard_data()
    )

    return render_template(
        "index.html",
        jobs=jobs,
        result=result,
        error=error,
        history=history,
        chart_history=chart_history,
        total=total,
        average=average,
        latest=latest
    )


# ============================================================
# DELETE SINGLE HISTORY RECORD
# ============================================================

@app.route(
    "/delete-history/<int:record_id>",
    methods=["POST"]
)
def delete_history(record_id):

    conn = get_db()

    conn.execute("""
        DELETE FROM analysis_history
        WHERE id = ?
    """, (record_id,))

    conn.commit()
    conn.close()

    return redirect(
        url_for(
            "index",
            deleted="one"
        )
    )


# ============================================================
# DELETE ALL HISTORY
# ============================================================

@app.route(
    "/delete-all-history",
    methods=["POST"]
)
def delete_all_history_route():

    conn = get_db()

    conn.execute("""
        DELETE FROM analysis_history
    """)

    conn.commit()

    # Reset auto increment
    conn.execute("""
        DELETE FROM sqlite_sequence
        WHERE name = 'analysis_history'
    """)

    conn.commit()
    conn.close()

    return redirect(
        url_for(
            "index",
            deleted="all"
        )
    )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    return render_template(
        "index.html",
        jobs=list(CAREER_PROFILES.keys()),
        result=None,
        error="File is too large. Maximum size is 10 MB.",
        history=get_history(),
        chart_history=get_dashboard_data()[3],
        total=get_dashboard_data()[0],
        average=get_dashboard_data()[1],
        latest=get_dashboard_data()[2]
    ), 413


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    init_db()

    print()
    print("=" * 60)
    print(" AI CAREER & SKILL GAP ANALYZER")
    print("=" * 60)
    print(" Server starting...")
    print(" Open: http://127.0.0.1:5000")
    print("=" * 60)
    print()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )