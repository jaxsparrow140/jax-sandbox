"""
AI course recommendations for a GSB MBA student doing concurrent MS in CS.
"""

RECOMMENDATIONS = {
    "must_take": {
        "emoji": "\ud83d\udd25",
        "label": "Must-Take Foundations",
        "description": "Core AI/ML courses every CS+MBA student should take",
        "courses": [
            {
                "code": "CS 229",
                "why": "The gold standard ML course at Stanford. Covers everything from linear regression to neural nets. Essential foundation for any AI-focused career."
            },
            {
                "code": "CS 221",
                "why": "Broad survey of AI techniques \u2014 search, planning, reasoning under uncertainty. Gives you the vocabulary and mental models for the entire field."
            },
            {
                "code": "CS 224N",
                "why": "NLP is at the heart of the LLM revolution. Learn transformers, attention, and modern language models from Christopher Manning, a legend in the field."
            },
            {
                "code": "CS 230",
                "why": "Andrew Ng's deep learning course. Practical and project-based. Perfect for building the intuition you need to evaluate AI investments and products."
            },
            {
                "code": "EE 364A",
                "why": "Optimization is the backbone of ML. Boyd's course is a Stanford classic and will deepen your understanding of how models actually learn."
            },
        ]
    },
    "gsb_ai_intersection": {
        "emoji": "\ud83d\udca1",
        "label": "GSB + AI Intersection",
        "description": "Where business strategy meets artificial intelligence",
        "courses": [
            {
                "code": "OIT 367",
                "why": "Directly bridges AI/ML and business applications. Learn to identify where ML creates real business value vs. where it's just hype."
            },
            {
                "code": "STRAMGT 351",
                "why": "Brynjolfsson explores how AI reshapes competitive dynamics. Critical for anyone thinking about AI startups or leading AI transformation."
            },
            {
                "code": "GSBGEN 566",
                "why": "Susan Athey on AI's societal impact. As a future tech leader, understanding governance and responsible deployment is essential."
            },
            {
                "code": "MS&E 226",
                "why": "Bridges the gap between data science theory and practice. Causal inference skills are invaluable for making data-driven business decisions."
            },
            {
                "code": "FINANCE 385",
                "why": "If you're interested in fintech or quantitative investing, this covers algorithmic trading, risk modeling, and AI-driven financial innovation."
            },
            {
                "code": "MKTG 355",
                "why": "AI is transforming marketing. Learn recommendation systems, dynamic pricing, and customer analytics \u2014 skills that translate directly to product roles."
            },
            {
                "code": "OIT 673",
                "why": "Guido Imbens (Nobel laureate) on using data and ML for organizational decision-making. Combines rigor with practical business applications."
            },
        ]
    },
    "advanced_specialized": {
        "emoji": "\ud83d\ude80",
        "label": "Advanced / Specialized",
        "description": "Cutting-edge topics for going deep on specific AI frontiers",
        "courses": [
            {
                "code": "CS 336",
                "why": "Build a GPT from scratch. This is the course if you want to truly understand LLMs at a systems level \u2014 tokenization, training, RLHF, and deployment."
            },
            {
                "code": "CS 324",
                "why": "Deep dive into large language models \u2014 architecture, capabilities, alignment, and societal impact. Directly relevant to the current AI wave."
            },
            {
                "code": "CS 236",
                "why": "Generative models are behind DALL-E, Midjourney, and Stable Diffusion. Learn VAEs, GANs, and diffusion models from Stefano Ermon."
            },
            {
                "code": "CS 234",
                "why": "RL powers robotics, game AI, and recommendation systems. Emma Brunskill is one of the best in the field."
            },
            {
                "code": "CS 330",
                "why": "Meta-learning and multi-task learning from Chelsea Finn. Critical for understanding how to build AI systems that generalize across tasks."
            },
            {
                "code": "CS 329H",
                "why": "RLHF and AI alignment \u2014 the techniques that made ChatGPT possible. Understand how to build AI that follows human intent."
            },
            {
                "code": "CS 231N",
                "why": "The definitive computer vision course. Even if CV isn't your focus, understanding visual AI is increasingly important for multimodal systems."
            },
            {
                "code": "CS 25",
                "why": "Just 1 unit \u2014 a seminar on transformers with guest lectures from top researchers. Low commitment, high insight. Easy to fit into any schedule."
            },
            {
                "code": "CS 329S",
                "why": "ML Systems Design covers the full production ML pipeline. Essential if you want to build or lead teams shipping real ML products."
            },
        ]
    },
}


def get_recommendations(courses: list[dict]) -> dict:
    """Build recommendations with full course data attached."""
    course_map = {c["code"]: c for c in courses}
    result = {}

    for category_key, category in RECOMMENDATIONS.items():
        enriched_courses = []
        for rec in category["courses"]:
            course_data = course_map.get(rec["code"])
            if course_data:
                enriched_courses.append({
                    **course_data,
                    "why": rec["why"],
                })
            else:
                enriched_courses.append({
                    "code": rec["code"],
                    "title": "Course details not in cache",
                    "why": rec["why"],
                    "description": "",
                    "units": "",
                    "schedule": "",
                    "instructor": "",
                    "department": "",
                })

        result[category_key] = {
            "emoji": category["emoji"],
            "label": category["label"],
            "description": category["description"],
            "courses": enriched_courses,
        }

    return result
