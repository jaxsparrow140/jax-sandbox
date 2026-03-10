import xml.etree.ElementTree as ET
from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__)

STANFORD_API = "https://explorecourses.stanford.edu/search"

RECOMMENDATIONS = [
    {
        "id": "rec-1",
        "code": "MS&E 226",
        "title": "Fundamentals of Data Science",
        "units": "3",
        "term": "Autumn",
        "description": "Statistical tools for data-driven decision making: prediction, causal inference, and decision analysis.",
        "category": "Core AI/ML",
        "why_gsb": "The gateway drug to data science — teaches you to think statistically about business problems without drowning in theory."
    },
    {
        "id": "rec-2",
        "code": "CS 229",
        "title": "Machine Learning",
        "units": "3-4",
        "term": "Autumn",
        "description": "Topics: supervised learning, unsupervised learning, learning theory, reinforcement learning and adaptive control.",
        "category": "Core AI/ML",
        "why_gsb": "The gold standard ML course. Heavy math, but gives you credibility and depth that no bootcamp can match."
    },
    {
        "id": "rec-3",
        "code": "CS 221",
        "title": "Artificial Intelligence: Principles and Techniques",
        "units": "3-4",
        "term": "Autumn, Spring",
        "description": "Principles and techniques of artificial intelligence. Search, game playing, logic, machine learning, deep learning.",
        "category": "Core AI/ML",
        "why_gsb": "Broad AI foundations — perfect if you want to speak the language of your future engineering teams."
    },
    {
        "id": "rec-4",
        "code": "MS&E 338",
        "title": "Reinforcement Learning",
        "units": "3",
        "term": "Spring",
        "description": "Foundations of reinforcement learning: Markov decision processes, dynamic programming, temporal difference learning, policy gradient methods.",
        "category": "Core AI/ML",
        "why_gsb": "Increasingly relevant for pricing, operations, and autonomous systems strategy."
    },
    {
        "id": "rec-5",
        "code": "CS 324",
        "title": "Large Language Models",
        "units": "3-4",
        "term": "Winter",
        "description": "Understanding the foundations and societal impact of large language models. Covers modeling, theory, ethics, and future directions.",
        "category": "Generative AI & LLMs",
        "why_gsb": "Understand the tech behind ChatGPT and what's coming next — essential for any AI-adjacent business strategy."
    },
    {
        "id": "rec-6",
        "code": "MS&E 336",
        "title": "AI and Business Strategy",
        "units": "3",
        "term": "Spring",
        "description": "How generative AI and foundation models reshape industries, business models, and competitive advantage.",
        "category": "Generative AI & LLMs",
        "why_gsb": "Tailor-made for GSB — connects cutting-edge AI capabilities directly to strategic decision-making."
    },
    {
        "id": "rec-7",
        "code": "OB 378",
        "title": "The Future of Work: AI, Automation, and the Workforce",
        "units": "3",
        "term": "Spring",
        "description": "Examines how AI and automation are transforming work, organizations, and labor markets.",
        "category": "AI for Business",
        "why_gsb": "Critical for future CEOs — understand how AI changes hiring, org design, and workforce strategy."
    },
    {
        "id": "rec-8",
        "code": "GSB 648",
        "title": "Data and Decisions",
        "units": "4",
        "term": "Autumn, Winter",
        "description": "Analytical frameworks for data-driven decision making in business contexts using statistical modeling.",
        "category": "AI for Business",
        "why_gsb": "Core GSB offering that builds your quantitative toolkit for every business decision you'll make."
    },
    {
        "id": "rec-9",
        "code": "MS&E 237",
        "title": "Data Management and Analytics",
        "units": "3",
        "term": "Autumn",
        "description": "Data management, data warehousing, and analytics for business intelligence and decision making.",
        "category": "AI for Business",
        "why_gsb": "Practical data infrastructure knowledge — know what your data team is actually building."
    },
    {
        "id": "rec-10",
        "code": "CS 281",
        "title": "Ethics of Artificial Intelligence",
        "units": "3-4",
        "term": "Winter",
        "description": "Ethical issues arising from the development and deployment of AI: fairness, accountability, transparency, and privacy.",
        "category": "Ethics & Policy",
        "why_gsb": "AI regulation is coming fast. This course prepares you to lead responsibly, not reactively."
    },
    {
        "id": "rec-11",
        "code": "POLS 114D",
        "title": "AI Policy and Governance",
        "units": "3-5",
        "term": "Spring",
        "description": "Analysis of policy frameworks governing artificial intelligence development, deployment, and societal impact.",
        "category": "Ethics & Policy",
        "why_gsb": "Navigate the regulatory landscape — essential knowledge for anyone building or investing in AI companies."
    },
    {
        "id": "rec-12",
        "code": "STRAMGT 354",
        "title": "Entrepreneurship and Venture Capital",
        "units": "3",
        "term": "Winter",
        "description": "Frameworks for evaluating and building technology ventures, with emphasis on AI and deep tech startups.",
        "category": "Entrepreneurship meets AI",
        "why_gsb": "Learn to evaluate AI startups — whether you're founding one or funding one."
    },
    {
        "id": "rec-13",
        "code": "STRAMGT 361",
        "title": "Technology Venture Formation",
        "units": "3",
        "term": "Spring",
        "description": "Hands-on course in forming and launching technology ventures. Students work in teams to develop real business concepts.",
        "category": "Entrepreneurship meets AI",
        "why_gsb": "Turn your AI idea into a real venture — the ultimate GSB capstone for technical entrepreneurs."
    }
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    try:
        resp = requests.get(
            STANFORD_API,
            params={
                "q": query,
                "view": "xml-20200810",
                "filter-coursestatus-Active": "on",
            },
            timeout=5,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch from Stanford API: {str(e)}"}), 502

    courses = []
    try:
        root = ET.fromstring(resp.text)
        for course_el in root.iter("course"):
            code_parts = []
            subj = course_el.get("subject", "")
            cat = course_el.get("catalogNumber", "")
            if subj:
                code_parts.append(subj)
            if cat:
                code_parts.append(cat)
            code = " ".join(code_parts)

            title = course_el.findtext("title", "")
            description = course_el.findtext("description", "")
            units_min = course_el.findtext("unitsMin", "")
            units_max = course_el.findtext("unitsMax", "")
            if units_min and units_max and units_min != units_max:
                units = f"{units_min}-{units_max}"
            else:
                units = units_min or units_max or "TBD"

            terms = set()
            for section in course_el.iter("section"):
                term = section.findtext("term", "")
                if term:
                    terms.add(term)
            term_str = ", ".join(sorted(terms)) if terms else "See bulletin"

            courses.append({
                "code": code,
                "title": title,
                "units": units,
                "term": term_str,
                "description": description,
            })

            if len(courses) >= 20:
                break
    except ET.ParseError:
        return jsonify({"error": "Failed to parse Stanford API response"}), 502

    return jsonify(courses)


@app.route("/api/recommendations")
def recommendations():
    return jsonify(RECOMMENDATIONS)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
