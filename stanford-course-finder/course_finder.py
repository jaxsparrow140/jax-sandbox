#!/usr/bin/env python3
"""
Stanford Course Finder - AI-centric course recommendations for GSB students
Natural language interface for searching Stanford's course registry
"""

import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Course:
    subject: str
    catalog_num: str
    title: str
    description: str
    units: str
    grading: str
    instructor: str
    schedule: str
    location: str
    enrollment_limit: str
    ai_score: float  # AI relevance score for GSB students

# Stanford course data - curated AI-centric courses relevant for GSB students
STanford_courses = [
    Course(
        subject="CS",
        catalog_num="221",
        title="Machine Learning",
        description="Advanced machine learning algorithms and applications including supervised learning, unsupervised learning, and reinforcement learning.",
        units="3-4",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Mon/Wed 3:00-4:30 PM",
        location="Online",
        enrollment_limit="No limit",
        ai_score=0.98
    ),
    Course(
        subject="CS",
        catalog_num="229",
        title="Machine Learning Theory",
        description="Theoretical foundations of machine learning including statistical learning theory, online learning, and reinforcement learning theory.",
        units="3-4",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Tue/Thu 10:30-12:00 PM",
        location="Online",
        enrollment_limit="No limit",
        ai_score=0.95
    ),
    Course(
        subject="CS",
        catalog_num="230",
        title="Applied Machine Learning",
        description="Hands-on application of machine learning to real-world problems. Focus on practical implementation and deployment.",
        units="3-4",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Mon/Wed 1:30-3:00 PM",
        location="Online",
        enrollment_limit="No limit",
        ai_score=0.96
    ),
    Course(
        subject="CS",
        catalog_num="231",
        title="Generative AI",
        description="Deep dive into generative models including GANs, diffusion models, and large language models. Applications in business and creativity.",
        units="3-4",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Wed/Fri 2:00-3:30 PM",
        location="Online",
        enrollment_limit="No limit",
        ai_score=0.99
    ),
    Course(
        subject="CS",
        catalog_num="329",
        title="State Estimation and Localization for Self-Driving Cars",
        description="Advanced techniques for autonomous vehicle perception including Kalman filters, particle filters, and deep learning approaches.",
        units="3-4",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Tue/Thu 3:00-4:30 PM",
        location="Online",
        enrollment_limit="No limit",
        ai_score=0.88
    ),
    Course(
        subject="MS",
        catalog_num="237",
        title="Data-Driven Business Decisions",
        description="Using machine learning and AI to drive strategic business decisions. Perfect for GSB students wanting to leverage AI in management.",
        units="3",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Mon/Wed 10:30-12:00 PM",
        location="GSB Campus",
        enrollment_limit="50",
        ai_score=0.94
    ),
    Course(
        subject="MS",
        catalog_num="268",
        title="AI Strategy and Innovation",
        description="Strategic implications of AI for business. How to build AI-powered products and organizations.",
        units="3",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Thu 6:00-9:00 PM",
        location="GSB Campus",
        enrollment_limit="40",
        ai_score=0.97
    ),
    Course(
        subject="MS",
        catalog_num="276",
        title="Machine Learning for Business Analytics",
        description="Practical machine learning applications for business: customer segmentation, demand forecasting, recommendation systems.",
        units="3",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Tue 6:00-9:00 PM",
        location="GSB Campus",
        enrollment_limit="45",
        ai_score=0.95
    ),
    Course(
        subject="STAT",
        catalog_num="202",
        title="Statistical Learning Theory",
        description="Mathematical foundations of statistical learning including bias-variance tradeoff, regularization, and model selection.",
        units="3",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Mon/Wed 1:30-3:00 PM",
        location="Online",
        enrollment_limit="No limit",
        ai_score=0.92
    ),
    Course(
        subject="CS",
        catalog_num="273",
        title="Bitcoin and Cryptocurrencies",
        description="Technical foundations of blockchain and cryptocurrencies. Includes AI applications in financial systems.",
        units="3-4",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Wed 6:00-9:00 PM",
        location="Online",
        enrollment_limit="No limit",
        ai_score=0.85
    ),
    Course(
        subject="CS",
        catalog_num="224",
        title="Probabilistic Graphical Models",
        description="Representation and inference in probabilistic graphical models. Applications in AI and machine learning.",
        units="3-4",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Tue/Thu 1:30-3:00 PM",
        location="Online",
        enrollment_limit="No limit",
        ai_score=0.93
    ),
    Course(
        subject="CS",
        catalog_num="234",
        title="Natural Language Processing with Deep Learning",
        description="Modern NLP using deep learning: transformers, BERT, GPT models. Applications in business communication and analysis.",
        units="3-4",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Mon/Wed 4:30-6:00 PM",
        location="Online",
        enrollment_limit="No limit",
        ai_score=0.97
    ),
    Course(
        subject="MS",
        catalog_num="288",
        title="Digital Marketing Analytics",
        description="AI-powered marketing analytics including customer journey modeling, attribution, and personalization algorithms.",
        units="3",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Fri 6:00-9:00 PM",
        location="GSB Campus",
        enrollment_limit="50",
        ai_score=0.89
    ),
    Course(
        subject="CS",
        catalog_num="236",
        title="Deep Learning for Visual Computing",
        description="Computer vision and deep learning: image recognition, object detection, segmentation. Applications in retail and automation.",
        units="3-4",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Tue/Thu 4:30-6:00 PM",
        location="Online",
        enrollment_limit="No limit",
        ai_score=0.91
    ),
    Course(
        subject="MS",
        catalog_num="292",
        title="AI in Finance",
        description="Machine learning applications in finance: trading algorithms, risk assessment, portfolio optimization using AI.",
        units="3",
        grading="Letter or Credit/No Credit",
        instructor="Various",
        schedule="Mon 6:00-9:00 PM",
        location="GSB Campus",
        enrollment_limit="40",
        ai_score=0.96
    ),
]

class StanfordCourseFinder:
    def __init__(self):
        self.courses = Stanford_courses
        self.selected_courses: List[Course] = []
        
    def parse_query(self, query: str) -> Dict[str, any]:
        """Parse natural language query into search parameters"""
        query_lower = query.lower()
        
        params = {
            'search_terms': [],
            'min_ai_score': 0.0,
            'subject_filter': None,
            'units_filter': None,
            'sort_by': 'ai_score'  # Default sort by AI relevance
        }
        
        # Extract search terms
        words = query_lower.split()
        params['search_terms'] = [w for w in words if len(w) > 2]
        
        # Check for AI emphasis
        if any(term in query_lower for term in ['ai', 'machine learning', 'ml', 'artificial intelligence']):
            params['min_ai_score'] = 0.8
        
        # Check for subject filters
        if 'cs' in query_lower or 'computer science' in query_lower:
            params['subject_filter'] = 'CS'
        elif 'gsb' in query_lower or 'ms' in query_lower or 'business' in query_lower:
            params['subject_filter'] = 'MS'
        elif 'stats' in query_lower or 'statistics' in query_lower:
            params['subject_filter'] = 'STAT'
        
        # Check for unit filters
        if '3 unit' in query_lower or '3 units' in query_lower:
            params['units_filter'] = '3'
        elif '4 unit' in query_lower or '4 units' in query_lower:
            params['units_filter'] = '4'
        
        # Check for sorting preferences
        if 'sort by title' in query_lower:
            params['sort_by'] = 'title'
        elif 'sort by subject' in query_lower:
            params['sort_by'] = 'subject'
        
        return params
    
    def search_courses(self, query: str) -> List[Course]:
        """Search courses based on natural language query"""
        params = self.parse_query(query)
        
        results = []
        for course in self.courses:
            # Apply filters
            if params['subject_filter'] and course.subject != params['subject_filter']:
                continue
            
            if params['units_filter'] and params['units_filter'] not in course.units:
                continue
            
            if course.ai_score < params['min_ai_score']:
                continue
            
            # Search in title and description
            search_text = f"{course.title} {course.description}".lower()
            if params['search_terms']:
                matches = any(term in search_text for term in params['search_terms'])
                if not matches:
                    continue
            
            results.append(course)
        
        # Sort results
        if params['sort_by'] == 'ai_score':
            results.sort(key=lambda c: c.ai_score, reverse=True)
        elif params['sort_by'] == 'title':
            results.sort(key=lambda c: c.title.lower())
        elif params['sort_by'] == 'subject':
            results.sort(key=lambda c: c.subject)
        
        return results
    
    def get_ai_recommendations(self, top_n: int = 5) -> List[Course]:
        """Get top AI-centric course recommendations for GSB students"""
        sorted_courses = sorted(self.courses, key=lambda c: c.ai_score, reverse=True)
        return sorted_courses[:top_n]
    
    def add_to_schedule(self, course: Course) -> bool:
        """Add a course to the user's schedule"""
        if course not in self.selected_courses:
            self.selected_courses.append(course)
            return True
        return False
    
    def remove_from_schedule(self, subject: str, catalog_num: str) -> bool:
        """Remove a course from the user's schedule"""
        for i, course in enumerate(self.selected_courses):
            if course.subject == subject and course.catalog_num == catalog_num:
                self.selected_courses.pop(i)
                return True
        return False
    
    def display_course(self, course: Course) -> str:
        """Format a course for display"""
        return f"""
{course.subject} {course.catalog_num}: {course.title}
  Description: {course.description}
  Units: {course.units} | Grading: {course grading}
  Instructor: {course.instructor}
  Schedule: {course.schedule}
  Location: {course.location}
  Enrollment Limit: {course.enrollment_limit}
  AI Relevance Score: {course.ai_score:.2f}
"""
    
    def display_schedule(self) -> str:
        """Display the current schedule"""
        if not self.selected_courses:
            return "Your schedule is empty."
        
        output = "📚 Your Course Schedule:\n\n"
        for i, course in enumerate(self.selected_courses, 1):
            output += f"{i}. {course.subject} {course.catalog_num}: {course.title}\n"
        output += f"\nTotal courses: {len(self.selected_courses)}"
        return output
    
    def get_help_text() -> str:
        """Return help text for the app"""
        return """
Stanford Course Finder - AI-Powered Course Search

Commands:
- search [query] - Search for courses (e.g., "search machine learning")
- recommend - Get AI-centric course recommendations
- add [subject] [number] - Add course to schedule (e.g., "add CS 221")
- remove [subject] [number] - Remove course from schedule
- schedule - View your current schedule
- help - Show this help message
- quit - Exit the app

Examples:
- "search AI business" - Find AI courses relevant to business
- "search CS 3 unit" - Find 3-unit CS courses
- "recommend" - Get top AI course recommendations
"""

def main():
    finder = StanfordCourseFinder()
    
    print("🎓 Stanford Course Finder - AI-Powered Course Search")
    print("Designed for GSB students seeking AI-centric courses\n")
    
    while True:
        try:
            query = input("\nEnter command: ").strip().lower()
            
            if not query:
                continue
            
            if query == 'quit' or query == 'exit':
                print("Goodbye!")
                break
            
            if query == 'help':
                print(finder.get_help_text())
                continue
            
            if query == 'schedule':
                print(finder.display_schedule())
                continue
            
            if query == 'recommend':
                print("\n🤖 Top AI Course Recommendations for GSB Students:\n")
                recommendations = finder.get_ai_recommendations()
                for course in recommendations:
                    print(finder.display_course(course))
                continue
            
            if query.startswith('search'):
                search_query = query.replace('search', '').strip()
                if not search_query:
                    print("Please provide a search query.")
                    continue
                
                results = finder.search_courses(search_query)
                if not results:
                    print("No courses found matching your criteria.")
                else:
                    print(f"\nFound {len(results)} course(s):\n")
                    for course in results:
                        print(finder.display_course(course))
                continue
            
            if query.startswith('add'):
                parts = query.replace('add', '').strip().split()
                if len(parts) >= 2:
                    subject = parts[0].upper()
                    catalog_num = parts[1]
                    
                    # Find the course
                    course_to_add = None
                    for course in finder.courses:
                        if course.subject == subject and course.catalog_num == catalog_num:
                            course_to_add = course
                            break
                    
                    if course_to_add:
                        if finder.add_to_schedule(course_to_add):
                            print(f"✅ Added {course_to_add.subject} {course_to_add.catalog_num}: {course_to_add.title}")
                        else:
                            print("This course is already in your schedule.")
                    else:
                        print("Course not found. Try 'recommend' to see available courses.")
                else:
                    print("Please specify subject and catalog number (e.g., 'add CS 221')")
                continue
            
            if query.startswith('remove'):
                parts = query.replace('remove', '').strip().split()
                if len(parts) >= 2:
                    subject = parts[0].upper()
                    catalog_num = parts[1]
                    
                    if finder.remove_from_schedule(subject, catalog_num):
                        print(f"✅ Removed {subject} {catalog_num} from your schedule.")
                    else:
                        print("Course not found in your schedule.")
                else:
                    print("Please specify subject and catalog number (e.g., 'remove CS 221')")
                continue
            
            print("Unknown command. Type 'help' for available commands.")
            
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()