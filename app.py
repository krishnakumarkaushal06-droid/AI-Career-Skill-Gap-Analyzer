from flask import Flask, render_template, request, redirect, url_for
import os
import re
import psycopg2
import psycopg2.extras

from werkzeug.utils import secure_filename
from pypdf import PdfReader


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)


print("======================================")
print("PROJECT ROOT:")
print(app.root_path)

print("STATIC FOLDER:")
print(app.static_folder)

print("VIDEO PATH:")
print(os.path.join(app.static_folder, "my-ai-video.mp4"))

print("VIDEO EXISTS:")
print(
    os.path.exists(
        os.path.join(
            app.static_folder,
            "my-ai-video.mp4"
        )
    )
)
print("======================================")


# =========================================================
# CONFIGURATION
# =========================================================

DELETE_PASSWORD = "krishna"

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)


# =========================================================
# CAREER DATABASE
# =========================================================

JOBS = {

    "Data Analyst": {
        "Python": 20,
        "SQL": 20,
        "Excel": 15,
        "Statistics": 15,
        "Power BI": 15,
        "Data Visualization": 10,
        "Communication": 5
    },

    "Data Scientist": {
        "Python": 20,
        "SQL": 15,
        "Statistics": 15,
        "Machine Learning": 20,
        "Pandas": 10,
        "NumPy": 10,
        "Data Visualization": 10
    },

    "ML Engineer": {
        "Python": 20,
        "Machine Learning": 20,
        "TensorFlow": 15,
        "PyTorch": 15,
        "SQL": 10,
        "NumPy": 10,
        "Pandas": 10
    },

    "Business Analyst": {
        "Excel": 20,
        "SQL": 15,
        "Power BI": 15,
        "Statistics": 10,
        "Data Visualization": 15,
        "Communication": 15,
        "Business Analysis": 10
    },

    "Software Developer": {
        "Java": 20,
        "C++": 15,
        "Python": 15,
        "JavaScript": 15,
        "HTML": 10,
        "CSS": 10,
        "SQL": 10,
        "Git": 5
    },

    "Web Developer": {
        "HTML": 15,
        "CSS": 15,
        "JavaScript": 20,
        "React": 15,
        "Node.js": 10,
        "SQL": 10,
        "Git": 5,
        "UI/UX": 10
    },

    "Data Engineer": {
        "Python": 15,
        "SQL": 20,
        "ETL": 15,
        "Pandas": 10,
        "Apache Spark": 15,
        "Cloud": 10,
        "Git": 5,
        "Linux": 10
    },

    "Cyber Security Analyst": {
        "Networking": 15,
        "Linux": 15,
        "Python": 15,
        "Cybersecurity": 20,
        "SQL": 10,
        "SIEM": 10,
        "Cloud": 5,
        "Git": 10
    }
}


# =========================================================
# SKILL ALIASES
# =========================================================

ALIASES = {

    "python": "Python",

    "sql": "SQL",
    "mysql": "SQL",

    "excel": "Excel",
    "microsoft excel": "Excel",

    "power bi": "Power BI",
    "powerbi": "Power BI",

    "statistics": "Statistics",
    "statistical analysis": "Statistics",

    "machine learning": "Machine Learning",
    "ml": "Machine Learning",

    "pandas": "Pandas",
    "numpy": "NumPy",

    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",

    "data visualization": "Data Visualization",
    "data visualisation": "Data Visualization",
    "visualization": "Data Visualization",

    "communication": "Communication",

    "java": "Java",

    "c++": "C++",
    "cpp": "C++",

    "javascript": "JavaScript",
    "js": "JavaScript",

    "html": "HTML",
    "css": "CSS",

    "react": "React",
    "reactjs": "React",

    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node js": "Node.js",

    "git": "Git",
    "github": "Git",

    "ui/ux": "UI/UX",
    "ui ux": "UI/UX",

    "etl": "ETL",
    "extract transform load": "ETL",

    "apache spark": "Apache Spark",
    "spark": "Apache Spark",

    "cloud": "Cloud",
    "aws": "Cloud",

    "linux": "Linux",

    "networking": "Networking",
    "network": "Networking",

    "cybersecurity": "Cybersecurity",
    "cyber security": "Cybersecurity",

    "siem": "SIEM",

    "business analysis": "Business Analysis",
    "business analyst": "Business Analysis"
}


# =========================================================
# LEARNING ROADMAP
# =========================================================

LEARNING = {

    "Python":
        "Build a small Pandas data-analysis project.",

    "SQL":
        "Practice joins, subqueries, CTEs and window functions.",

    "Excel":
        "Learn PivotTables, lookup functions and dashboards.",

    "Statistics":
        "Study probability, distributions, correlation and hypothesis testing.",

    "Power BI":
        "Create an interactive dashboard using a public dataset.",

    "Data Visualization":
        "Learn chart selection, storytelling and dashboard design.",

    "Machine Learning":
        "Build and evaluate a classification or regression model.",

    "Pandas":
        "Clean, transform and analyze a real dataset.",

    "NumPy":
        "Practice arrays, vectorization and numerical operations.",

    "TensorFlow":
        "Build a small neural-network classifier.",

    "PyTorch":
        "Implement a basic neural-network training pipeline.",

    "Java":
        "Build a small OOP application using collections and exceptions.",

    "C++":
        "Practice STL, OOP and algorithmic problem solving.",

    "JavaScript":
        "Build an interactive web application.",

    "HTML":
        "Create accessible semantic web pages.",

    "CSS":
        "Learn responsive layouts and modern UI styling.",

    "React":
        "Build a component-based dashboard.",

    "Node.js":
        "Create a REST API.",

    "Git":
        "Use branches, commits and pull requests in a project.",

    "Linux":
        "Practice shell commands, permissions and process management.",

    "Cloud":
        "Learn basic compute, storage, networking and deployment concepts.",

    "Networking":
        "Study TCP/IP, DNS, HTTP and subnetting.",

    "Cybersecurity":
        "Learn authentication, common attacks and secure coding.",

    "SIEM":
        "Practice log analysis and alert triage.",

    "UI/UX":
        "Create wireframes and usability-focused interfaces.",

    "ETL":
        "Build an extract-transform-load pipeline.",

    "Apache Spark":
        "Process a larger dataset with Spark DataFrames.",

    "Business Analysis":
        "Practice requirements, KPIs and stakeholder analysis.",

    "Communication":
        "Practice presenting technical findings clearly."
}


# =========================================================
# OPPORTUNITY DATABASE
# =========================================================

OPPORTUNITIES = [

    {
        "type": "Internship",
        "icon": "💼",
        "title": "Data Analyst Internship",
        "platform": "LinkedIn Jobs",
        "url": "https://www.linkedin.com/jobs/search/?keywords=Data%20Analyst%20Intern",
        "skills": [
            "Python",
            "SQL",
            "Excel",
            "Power BI",
            "Data Visualization"
        ]
    },

    {
        "type": "Internship",
        "icon": "📊",
        "title": "Business & Data Analytics Internship",
        "platform": "Internshala",
        "url": "https://internshala.com/internships/data-analytics-internship/",
        "skills": [
            "Excel",
            "SQL",
            "Power BI",
            "Statistics",
            "Communication"
        ]
    },

    {
        "type": "Internship",
        "icon": "🤖",
        "title": "Machine Learning Internship",
        "platform": "LinkedIn Jobs",
        "url": "https://www.linkedin.com/jobs/search/?keywords=Machine%20Learning%20Intern",
        "skills": [
            "Python",
            "Machine Learning",
            "Pandas",
            "NumPy",
            "TensorFlow"
        ]
    },

    {
        "type": "Internship",
        "icon": "💻",
        "title": "Software Developer Internship",
        "platform": "Internshala",
        "url": "https://internshala.com/internships/software-development-internship/",
        "skills": [
            "Java",
            "Python",
            "C++",
            "Git"
        ]
    },

    {
        "type": "Internship",
        "icon": "🌐",
        "title": "Web Development Internship",
        "platform": "Internshala",
        "url": "https://internshala.com/internships/web-development-internship/",
        "skills": [
            "HTML",
            "CSS",
            "JavaScript",
            "React",
            "Node.js"
        ]
    },

    {
        "type": "Remote Job",
        "icon": "🌍",
        "title": "Remote Data Analyst Opportunities",
        "platform": "LinkedIn Remote Jobs",
        "url": "https://www.linkedin.com/jobs/search/?keywords=Data%20Analyst&f_WT=2",
        "skills": [
            "Python",
            "SQL",
            "Excel",
            "Power BI",
            "Data Visualization"
        ]
    },

    {
        "type": "Remote Job",
        "icon": "🏠",
        "title": "Remote Software Developer Opportunities",
        "platform": "LinkedIn Remote Jobs",
        "url": "https://www.linkedin.com/jobs/search/?keywords=Software%20Developer&f_WT=2",
        "skills": [
            "Java",
            "Python",
            "JavaScript",
            "SQL",
            "Git"
        ]
    },

    {
        "type": "Remote Job",
        "icon": "🧠",
        "title": "Remote AI & Machine Learning Opportunities",
        "platform": "LinkedIn Remote Jobs",
        "url": "https://www.linkedin.com/jobs/search/?keywords=Machine%20Learning&f_WT=2",
        "skills": [
            "Python",
            "Machine Learning",
            "Pandas",
            "NumPy"
        ]
    },

    {
        "type": "Remote Job",
        "icon": "🔐",
        "title": "Remote Cybersecurity Opportunities",
        "platform": "LinkedIn Remote Jobs",
        "url": "https://www.linkedin.com/jobs/search/?keywords=Cybersecurity&f_WT=2",
        "skills": [
            "Cybersecurity",
            "Networking",
            "Linux",
            "Python",
            "SIEM"
        ]
    },

    {
        "type": "Hackathon",
        "icon": "🏆",
        "title": "AI & Data Science Hackathons",
        "platform": "Devfolio",
        "url": "https://devfolio.co/hackathons",
        "skills": [
            "Python",
            "Machine Learning",
            "Pandas",
            "SQL",
            "Data Visualization"
        ]
    },

    {
        "type": "Hackathon",
        "icon": "🚀",
        "title": "Software & Web Development Hackathons",
        "platform": "Devfolio",
        "url": "https://devfolio.co/hackathons",
        "skills": [
            "JavaScript",
            "HTML",
            "CSS",
            "React",
            "Node.js",
            "Git"
        ]
    },

    {
        "type": "Hackathon",
        "icon": "🇮🇳",
        "title": "National Innovation & Student Hackathons",
        "platform": "Unstop",
        "url": "https://unstop.com/hackathons",
        "skills": [
            "Python",
            "Java",
            "SQL",
            "Machine Learning",
            "Communication"
        ]
    }
]


# =========================================================
# POSTGRESQL DATABASE CONNECTION
# =========================================================

def get_db_connection():

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:

        raise Exception(
            "DATABASE_URL environment variable is not configured."
        )

    return psycopg2.connect(
        database_url,
        sslmode="require"
    )


# =========================================================
# CREATE TABLE
# =========================================================

def create_table():

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id SERIAL PRIMARY KEY,
                resume_name VARCHAR(255) NOT NULL,
                target_career VARCHAR(255) NOT NULL,
                keyword_score DOUBLE PRECISION,
                ai_semantic_score DOUBLE PRECISION,
                final_score DOUBLE PRECISION,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        db.commit()

        print("===================================")
        print("POSTGRESQL TABLE READY")
        print("===================================")

    except Exception as e:

        print("===================================")
        print("TABLE CREATION ERROR:")
        print(e)
        print("===================================")

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# SAVE ANALYSIS TO POSTGRESQL
# =========================================================

def save_analysis(
    filename,
    career,
    keyword_score,
    ai_semantic_score,
    final_score
):

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor()

        query = """
        INSERT INTO analysis_history
        (
            resume_name,
            target_career,
            keyword_score,
            ai_semantic_score,
            final_score
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """

        values = (
            filename,
            career,
            keyword_score,
            ai_semantic_score,
            final_score
        )

        cursor.execute(
            query,
            values
        )

        db.commit()

        print("===================================")
        print("ANALYSIS SAVED TO POSTGRESQL SUCCESSFULLY")
        print("===================================")

    except Exception as e:

        print("===================================")
        print("DATABASE SAVE ERROR:")
        print(e)
        print("===================================")

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# GET DASHBOARD DATA
# =========================================================

def get_dashboard_data():

    history = []
    total = 0
    average = 0
    latest = 0
    chart_history = []

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )

        cursor.execute(
            """
            SELECT
                id,
                resume_name,
                target_career,
                keyword_score,
                ai_semantic_score,
                final_score,
                analyzed_at
            FROM analysis_history
            ORDER BY id DESC
            """
        )

        history = cursor.fetchall()

        history = [
            dict(row)
            for row in history
        ]

        total = len(history)

        if total > 0:

            average = round(
                sum(
                    float(
                        row["final_score"] or 0
                    )
                    for row in history
                )
                / total,
                2
            )

            latest = float(
                history[0]["final_score"] or 0
            )

        chart_history = list(
            reversed(history)
        )

    except Exception as e:

        print("===================================")
        print("DASHBOARD DATA ERROR:")
        print(e)
        print("===================================")

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()

    return (
        history,
        total,
        average,
        latest,
        chart_history
    )


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def pdf_text(path):

    reader = PdfReader(path)

    text = ""

    for page in reader.pages:

        text += (
            page.extract_text() or ""
        )

        text += "\n"

    return text


# =========================================================
# SKILL EXTRACTION
# =========================================================

def skills_from_text(text):

    low = text.lower()

    found = []

    sorted_aliases = sorted(
        ALIASES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    for alias, canonical in sorted_aliases:

        pattern = (
            r"(?<![a-z0-9])"
            +
            re.escape(alias)
            +
            r"(?![a-z0-9])"
        )

        if re.search(
            pattern,
            low
        ):

            if canonical not in found:

                found.append(
                    canonical
                )

    return found


# =========================================================
# WEIGHTED KEYWORD SCORE
# =========================================================

def weighted_score(
    skills,
    required
):

    total = 0

    for skill, weight in required.items():

        if skill in skills:

            total += weight

    return round(
        total,
        2
    )


# =========================================================
# SEMANTIC RELATED SKILL SCORE
# =========================================================

def semantic_bonus(
    skills,
    required
):

    groups = [

        {
            "Python",
            "Pandas",
            "NumPy",
            "Machine Learning"
        },

        {
            "SQL",
            "ETL",
            "Apache Spark"
        },

        {
            "Excel",
            "Power BI",
            "Data Visualization",
            "Statistics"
        },

        {
            "JavaScript",
            "React",
            "Node.js",
            "HTML",
            "CSS"
        },

        {
            "Linux",
            "Networking",
            "Cybersecurity",
            "SIEM",
            "Cloud"
        },

        {
            "Java",
            "C++",
            "Python",
            "Git"
        }
    ]

    bonus = 0

    for group in groups:

        have = len(
            set(skills)
            &
            group
        )

        need = len(
            set(required)
            &
            group
        )

        if need and have:

            bonus += min(
                5,
                round(
                    5
                    *
                    have
                    /
                    max(
                        need,
                        1
                    )
                )
            )

    return min(
        100,
        bonus
    )


# =========================================================
# COMPLETE ANALYSIS
# =========================================================

def analyze(
    skills,
    career
):

    required = JOBS[career]

    keyword_score = weighted_score(
        skills,
        required
    )

    semantic = semantic_bonus(
        skills,
        required
    )

    ai_semantic_score = min(
        100,
        round(
            keyword_score
            +
            semantic,
            2
        )
    )

    final_score = min(
        100,
        round(
            0.85
            *
            keyword_score
            +
            0.15
            *
            ai_semantic_score,
            2
        )
    )

    existing = []
    missing = []

    for skill in required:

        if skill in skills:

            existing.append(
                skill
            )

        else:

            missing.append(
                skill
            )

    priority = sorted(
        missing,
        key=lambda s: required[s],
        reverse=True
    )

    return (
        keyword_score,
        ai_semantic_score,
        final_score,
        existing,
        missing,
        priority,
        required
    )


# =========================================================
# CAREER RECOMMENDATIONS
# =========================================================

def role_recommendations(skills):

    results = []

    for role, required in JOBS.items():

        score = weighted_score(
            skills,
            required
        )

        results.append(
            {
                "career": role,
                "score": score
            }
        )

    return sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )


# =========================================================
# OPPORTUNITY MATCHING
# =========================================================

def opportunity_recommendations(
    skills,
    career
):

    results = []

    user_skills = set(skills)

    career_skills = set(
        JOBS.get(
            career,
            {}
        ).keys()
    )

    for opportunity in OPPORTUNITIES:

        opportunity_skills = set(
            opportunity["skills"]
        )

        matched = sorted(
            user_skills
            &
            opportunity_skills
        )

        missing = sorted(
            opportunity_skills
            -
            user_skills
        )

        total_skills = len(
            opportunity_skills
        )

        if total_skills > 0:

            skill_match = (
                len(matched)
                /
                total_skills
            ) * 100

        else:

            skill_match = 0

        career_related = len(
            career_skills
            &
            opportunity_skills
        )

        career_relevance = (
            career_related
            /
            max(
                len(opportunity_skills),
                1
            )
        ) * 15

        final_match = min(
            100,
            round(
                skill_match
                +
                career_relevance,
                2
            )
        )

        if final_match >= 80:

            readiness = "Excellent Match"
            badge = "excellent"

        elif final_match >= 60:

            readiness = "Strong Match"
            badge = "strong"

        elif final_match >= 40:

            readiness = "Moderate Match"
            badge = "moderate"

        else:

            readiness = "Skill Development Needed"
            badge = "low"

        results.append({

            "type":
                opportunity["type"],

            "icon":
                opportunity["icon"],

            "title":
                opportunity["title"],

            "platform":
                opportunity["platform"],

            "url":
                opportunity["url"],

            "score":
                final_match,

            "skill_match":
                round(
                    skill_match,
                    2
                ),

            "career_relevance":
                round(
                    career_relevance,
                    2
                ),

            "readiness":
                readiness,

            "badge":
                badge,

            "matched":
                matched,

            "missing":
                missing,

            "matched_count":
                len(matched),

            "total_count":
                total_skills
        })

    return sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )


# =========================================================
# READINESS LEVEL
# =========================================================

def get_readiness_level(score):

    if score >= 85:

        return (
            "Excellent Career Readiness"
        )

    if score >= 70:

        return (
            "Strong Career Readiness"
        )

    if score >= 50:

        return (
            "Developing Career Readiness"
        )

    return (
        "Beginner Career Readiness"
    )


# =========================================================
# HOME ROUTE
# =========================================================

@app.route(
    "/",
    methods=[
        "GET",
        "POST"
    ]
)

def index():

    if request.method == "POST":

        file = request.files.get(
            "resume"
        )

        career = request.form.get(
            "career"
        )

        if not file:

            (
                history,
                total,
                average,
                latest,
                chart_history
            ) = get_dashboard_data()

            return render_template(
                "index.html",
                jobs=JOBS,
                history=history,
                total=total,
                average=average,
                latest=latest,
                chart_history=chart_history,
                result=None,
                error="Please upload a resume."
            )

        if not file.filename.lower().endswith(
            ".pdf"
        ):

            (
                history,
                total,
                average,
                latest,
                chart_history
            ) = get_dashboard_data()

            return render_template(
                "index.html",
                jobs=JOBS,
                history=history,
                total=total,
                average=average,
                latest=latest,
                chart_history=chart_history,
                result=None,
                error="Please upload a PDF resume."
            )

        if career not in JOBS:

            (
                history,
                total,
                average,
                latest,
                chart_history
            ) = get_dashboard_data()

            return render_template(
                "index.html",
                jobs=JOBS,
                history=history,
                total=total,
                average=average,
                latest=latest,
                chart_history=chart_history,
                result=None,
                error="Please select a valid career."
            )

        filename = secure_filename(
            file.filename
        )

        path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(
            path
        )

        try:

            text = pdf_text(
                path
            )

            skills = skills_from_text(
                text
            )

            (
                keyword_score,
                ai_semantic_score,
                final_score,
                existing,
                missing,
                priority,
                required

            ) = analyze(
                skills,
                career
            )

            roles = role_recommendations(
                skills
            )

            roadmap = []

            for skill in priority:

                roadmap.append(
                    {

                        "skill":
                            skill,

                        "priority":

                            "High"

                            if required[skill] >= 15

                            else

                            "Medium",

                        "action":

                            LEARNING.get(
                                skill,
                                "Practice this skill with a project."
                            )
                    }
                )

            opportunities = (
                opportunity_recommendations(
                    skills,
                    career
                )
            )

            # SAVE ANALYSIS TO POSTGRESQL

            save_analysis(
                filename,
                career,
                keyword_score,
                ai_semantic_score,
                final_score
            )

            (
                history,
                total,
                average,
                latest,
                chart_history

            ) = get_dashboard_data()

            result = {

                "career":
                    career,

                "level":
                    get_readiness_level(
                        final_score
                    ),

                "score":
                    final_score,

                "keyword_score":
                    keyword_score,

                "ai_score":
                    ai_semantic_score,

                "skills":
                    skills,

                "existing":
                    existing,

                "missing":
                    missing,

                "required":
                    required,

                "roles":
                    roles,

                "roadmap":
                    roadmap,

                "opportunities":
                    opportunities
            }

            return render_template(

                "index.html",

                jobs=JOBS,

                result=result,

                history=history,

                total=total,

                average=average,

                latest=latest,

                chart_history=chart_history
            )

        except Exception as e:

            print("===================================")
            print("ANALYSIS ERROR:")
            print(e)
            print("===================================")

            (
                history,
                total,
                average,
                latest,
                chart_history

            ) = get_dashboard_data()

            return render_template(

                "index.html",

                jobs=JOBS,

                history=history,

                total=total,

                average=average,

                latest=latest,

                chart_history=chart_history,

                result=None,

                error=(
                    "Could not analyze this PDF. "
                    "Please use a text-based PDF resume."
                )
            )

    (
        history,
        total,
        average,
        latest,
        chart_history

    ) = get_dashboard_data()

    return render_template(

        "index.html",

        jobs=JOBS,

        history=history,

        total=total,

        average=average,

        latest=latest,

        chart_history=chart_history,

        result=None
    )


# =========================================================
# DELETE SINGLE HISTORY RECORD
# =========================================================

@app.route(
    "/delete-history/<int:record_id>",
    methods=["POST"]
)
def delete_history(record_id):

    password = request.form.get(
        "delete_password",
        ""
    )

    if password != DELETE_PASSWORD:
        return redirect(
            url_for(
                "index",
                delete_error="wrong"
            )
            + "#dashboard"
        )

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            DELETE FROM analysis_history
            WHERE id = %s
            """,
            (record_id,)
        )

        db.commit()
        print(f"History record {record_id} deleted.")

    except Exception as e:
        print("DELETE HISTORY ERROR:")
        print(e)

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    return redirect(
        url_for(
            "index",
            deleted="one"
        )
        + "#dashboard"
    )


# =========================================================
# DELETE ALL HISTORY
# =========================================================

@app.route(
    "/delete-all-history",
    methods=["POST"]
)
def delete_all_history_route():

    password = request.form.get(
        "delete_password",
        ""
    )

    if password != DELETE_PASSWORD:
        return redirect(
            url_for(
                "index",
                delete_error="wrong"
            )
            + "#dashboard"
        )

    db = None
    cursor = None

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            TRUNCATE TABLE analysis_history
            RESTART IDENTITY
            """
        )

        db.commit()
        print("ALL HISTORY DELETED AND ID RESET TO 1")

    except Exception as e:
        print("DELETE ALL HISTORY ERROR:")
        print(e)

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    return redirect(
        url_for(
            "index",
            deleted="all"
        )
        + "#dashboard"
    )


# =========================================================
# DASHBOARD ROUTE
# =========================================================

@app.route(
    "/dashboard"
)

def dashboard():

    (
        history,
        total,
        average,
        latest,
        chart_history

    ) = get_dashboard_data()

    return render_template(

        "index.html",

        jobs=JOBS,

        history=history,

        total=total,

        average=average,

        latest=latest,

        chart_history=chart_history,

        result=None
    )


# =========================================================
# INTERACTIVE PROJECT PRESENTATION
# =========================================================

@app.route(
    "/presentation"
)

def presentation():

    return render_template(
        "presentation.html"
    )


# =========================================================
# FILE TOO LARGE ERROR
# =========================================================

@app.errorhandler(
    413
)

def file_too_large(error):

    (
        history,
        total,
        average,
        latest,
        chart_history

    ) = get_dashboard_data()

    return render_template(

        "index.html",

        jobs=JOBS,

        history=history,

        total=total,

        average=average,

        latest=latest,

        chart_history=chart_history,

        result=None,

        error=(
            "File is too large. "
            "Maximum allowed size is 8 MB."
        )

    ), 413


# =========================================================
# STARTUP
# =========================================================

create_table()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
