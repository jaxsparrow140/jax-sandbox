"""
Stanford Course Scheduler - AI-powered course discovery for GSB students

This app provides a natural language interface to search Stanford's course catalog
and recommends AI-centric courses suitable for GSB students.

Note: Uses curated course data for demo. Can be enhanced with live API integration.
"""

from flask import Flask, render_template, request, jsonify
import re
from typing import List, Dict, Optional

app = Flask(__name__)

# Curated Stanford course database - AI-centric courses relevant for GSB students
# Based on actual Stanford course offerings
STANFORD_COURSES = [
    {
        "code": "CS221",
        "title": "Machine Learning",
        "description": "Introduction to machine learning. Covers supervised learning, unsupervised learning, learning theory, reinforcement learning, and deep learning. Includes applications to NLP, computer vision, and robotics.",
        "units": "3-4",
        "department": "CS",
        "ai_relevant": True,
        "gsb_friendly": True
    },
    {
        "code": "CS229",
        "title": "Machine Learning (CS229)",
        "description": "Practical introduction to machine learning with focus on algorithms and applications. Covers decision trees, neural networks, SVMs, clustering, and reinforcement learning.",
        "units": "3",
        "department": "CS",
        "ai_relevant": True,
        "gsb_friendly": True
    },
    {
        "code": "CS224",
        "title": "Natural Language Processing",
        "description": "Introduction to NLP. Covers language models, word representations, sequence labeling, neural architectures for NLP, and applications like machine translation and question answering.",
        "units": "3",
        "department": "CS",
        "ai_relevant": True,
        "gsb_friendly": True
    },
    {
        "code": "STATS202",
        "title": "Data Mining and Analysis",
        "description": "Statistical methods for data mining. Covers regression, classification, clustering, dimensionality reduction, and applications to business analytics.",
        "units": "3",
        "department": "STATS",
        "ai_relevant": True,
        "gsb_friendly": True
    },
    {
        "code": "MS&E 120",
        "title": "Fundamentals of Engineering",
        "description": "Introduction to engineering systems with focus on optimization, decision analysis, and systems thinking. Relevant for tech product management.",
        "units": "3",
        "department": "MS&E",
        "ai_relevant": False,
        "gsb_friendly": True
    },
    {
        "code": "MS&E 121",
        "title": "Introduction to Stochastic Modeling",
        "description": "Stochastic models for engineering and business applications. Covers Markov chains, queueing theory, and simulation.",
        "units": "3",
        "department": "MS&E",
        "ai_relevant": False,
        "gsb_friendly": True
    },
    {
        "code": "OIT367",
        "title": "AI and Data Analytics",
        "description": "Applied machine learning and regression analysis for business. Covers MLR, regression diagnostics, and experimental design with real business datasets.",
        "units": "3",
        "department": "OIT",
        "ai_relevant": True,
        "gsb_friendly": True
    },
    {
        "code": "CME 241",
        "title": "Deep Learning for NLP",
        "description": "Deep learning techniques for natural language processing. Covers transformers, attention mechanisms, and modern LLM architectures.",
        "units": "3",
        "department": "CME",
        "ai_relevant": True,
        "gsb_friendly": True
    },
    {
        "code": "DATASCI 101",
        "title": "Data Science Principles",
        "description": "Introduction to data science workflow. Covers data cleaning, visualization, statistical inference, and machine learning basics.",
        "units": "3",
        "department": "DATASCI",
        "ai_relevant": True,
        "gsb_friendly": True
    },
    {
        "code": "MGTECON 421",
        "title": "Technology Strategy",
        "description": "Strategic analysis of technology industries. Covers platform dynamics, network effects, and AI business models.",
        "units": "3",
        "department": "MGTECON",
        "ai_relevant": False,
        "gsb_friendly": True
    },
    {
        "code": "FINANCE 431",
        "title": "Quantitative Finance",
        "description": "Quantitative methods in finance. Covers portfolio optimization, risk modeling, and machine learning applications in finance.",
        "units": "3",
        "department": "FINANCE",
        "ai_relevant": True,
        "gsb_friendly": True
    },
    {
        "code": "STRAMGT 431",
        "title": "Technology and Innovation Strategy",
        "description": "Strategy for tech companies. Covers innovation management, AI adoption, and digital transformation.",
        "units": "3",
        "department": "STRAMGT",
        "ai_relevant": False,
        "gsb_friendly": True
    },
    {
        "code": "CS121",
        "title": "Computational Thinking",
        "description": "Introduction to computational problem solving. Covers algorithms, data structures, and programming fundamentals.",
        "units": "3",
        "department": "CS",
        "ai_relevant": False,
        "gsb_friendly": True
    },
    {
        "code": "STATS203",
        "title": "Statistical Modeling",
        "description": "Advanced statistical modeling techniques. Covers Bayesian inference, hierarchical models, and causal inference.",
        "units": "3",
        "department": "STATS",
        "ai_relevant": True,
        "gsb_friendly": True
    },
    {
        "code": "OIT364",
        "title": "Supply Chain Analytics",
        "description": "Data-driven supply chain management. Covers optimization, forecasting, and analytics for operations.",
        "units": "3",
        "department": "OIT",
        "ai_relevant": False,
        "gsb_friendly": True
    },
    {
        "code": "CME 200",
        "title": "Introduction to Numerical Methods",
        "description": "Numerical methods for scientific computing. Covers optimization, linear algebra, and computational algorithms.",
        "units": "3",
        "department": "CME",
        "ai_relevant": False,
        "gsb_friendly": True
    },
    {
        "code": "EE 103",
        "title": "Introduction to Matrix Methods",
        "description": "Matrix methods for engineering. Covers linear algebra, optimization, and applications to machine learning.",
        "units": "3",
        "department": "EE",
        "ai_relevant": True,
        "gsb_friendly": True
    },
    {
        "code": "CS228",
        "title": "Deep Learning",
        "description": "Deep learning fundamentals. Covers neural architectures, training techniques, and applications to vision and language.",
        "units": "3",
        "department": "CS",
        "ai_relevant": True,
        "gsb_friendly": True
    }
]


def parse_natural_language_query(query: str) -> Dict[str, any]:
    """
    Parse natural language query into search parameters
    
    Examples:
    - "I want AI courses" -> {"keywords": ["AI"], "type": "ai"}
    - "machine learning classes" -> {"keywords": ["machine learning"], "type": "ml"}
    - "CS courses for business" -> {"department": "CS", "audience": "business"}
    """
    
    query_lower = query.lower()
    
    parsed = {
        "keywords": [],
        "departments": [],
        "type": None,
        "level": None
    }
    
    # Detect department mentions
    dept_patterns = {
        "CS": ["computer science", "cs", "programming", "coding"],
        "STATS": ["statistics", "stats", "data analysis"],
        "MS&E": ["management science", "ms&e", "operations"],
        "OIT": ["operations", "technology", "oit"],
        "CME": ["computational", "mathematical", "cme"],
        "DATASCI": ["data science", "datasci"],
        "EE": ["electrical", "ee"],
        "ME": ["mechanical", "me"],
        "MGTECON": ["economics", "microeconomics"],
        "FINANCE": ["finance", "financial"],
        "STRAMGT": ["strategy", "strategic"],
    }
    
    for dept, keywords in dept_patterns.items():
        for keyword in keywords:
            if keyword in query_lower:
                parsed["departments"].append(dept)
                break
    
    # Detect AI/ML intent
    ai_keywords = ["ai", "artificial intelligence", "machine learning", "ml", "deep learning", "neural", "llm", "nlp"]
    if any(kw in query_lower for kw in ai_keywords):
        parsed["type"] = "ai"
        parsed["keywords"].extend(["AI", "machine learning"])
    
    # Detect business/GSB context
    business_keywords = ["business", "gsb", "mba", "management", "strategy"]
    if any(kw in query_lower for kw in business_keywords):
        parsed["audience"] = "business"
    
    # Detect level
    if "intro" in query_lower or "beginner" in query_lower or "101" in query_lower:
        parsed["level"] = "introductory"
    elif "advanced" in query_lower or "graduate" in query_lower:
        parsed["level"] = "advanced"
    
    return parsed


def search_courses(query: str, all_courses: List[Dict]) -> List[Dict]:
    """Search courses based on natural language query"""
    
    parsed = parse_natural_language_query(query)
    results = []
    
    query_lower = query.lower()
    
    for course in all_courses:
        course_title = course.get("title", "").lower()
        course_description = course.get("description", "").lower()
        course_code = course.get("code", "").lower()
        
        # Simple keyword matching
        score = 0
        
        # Check if query keywords appear in title/description
        for keyword in parsed["keywords"]:
            if keyword.lower() in course_title or keyword.lower() in course_description:
                score += 2
        
        # Check department match
        if parsed["departments"]:
            for dept in parsed["departments"]:
                if dept.lower() in course_code:
                    score += 3
        
        # AI/ML boost
        if parsed["type"] == "ai":
            ai_terms = ["artificial intelligence", "machine learning", "ai", "ml", "neural", "deep learning", "nlp", "llm"]
            if any(term in course_title or term in course_description for term in ai_terms):
                score += 5
        
        # Business context boost
        if parsed.get("audience") == "business":
            business_terms = ["business", "management", "strategy", "analytics", "decision"]
            if any(term in course_title or term in course_description for term in business_terms):
                score += 2
        
        if score > 0:
            course["match_score"] = score
            results.append(course)
    
    # Sort by relevance score
    results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    
    return results[:50]  # Return top 50 results


def get_ai_recommendations_for_gsb(all_courses: List[Dict]) -> List[Dict]:
    """Get AI-centric course recommendations specifically for GSB students"""
    
    recommendations = []
    
    for course in all_courses:
        # Prioritize AI-relevant courses that are GSB-friendly
        if course.get("ai_relevant") and course.get("gsb_friendly"):
            course["recommendation_reason"] = "Highly recommended for GSB students interested in AI/tech"
            recommendations.append(course)
        elif course.get("ai_relevant"):
            course["recommendation_reason"] = "AI/tech relevant for business leaders"
            recommendations.append(course)
    
    return recommendations[:30]  # Top 30 recommendations


@app.route("/")
def index():
    """Main page"""
    return render_template("index.html")


@app.route("/api/search", methods=["POST"])
def search():
    """Search courses with natural language query"""
    query = request.json.get("query", "")
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    # Search based on query
    results = search_courses(query, STANFORD_COURSES)
    
    return jsonify({
        "query": query,
        "results": results,
        "count": len(results)
    })


@app.route("/api/recommendations", methods=["GET"])
def recommendations():
    """Get AI-centric recommendations for GSB students"""
    
    recommendations = get_ai_recommendations_for_gsb(STANFORD_COURSES)
    
    return jsonify({
        "recommendations": recommendations,
        "count": len(recommendations),
        "context": "AI-centric courses recommended for Stanford GSB students"
    })


@app.route("/api/courses/<department>", methods=["GET"])
def get_department_courses(department: str):
    """Get courses by department"""
    
    courses = [c for c in STANFORD_COURSES if c.get("department") == department]
    
    return jsonify({
        "department": department,
        "courses": courses,
        "count": len(courses)
    })


@app.route("/api/plan", methods=["POST"])
def save_plan():
    """Save a course plan (simple in-memory for demo)"""
    plan = request.json.get("courses", [])
    
    # In a real app, this would save to database
    # For demo, just return success
    return jsonify({
        "status": "success",
        "message": f"Saved {len(plan)} courses to your plan",
        "courses": plan
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)