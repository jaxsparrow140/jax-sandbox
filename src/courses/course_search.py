"""
Stanford Course Scheduler for GSB Students
A simple natural language interface to search and recommend AI-centric courses
"""

import sys
import json
from explorecourses import CourseConnection
from explorecourses import filters
import re
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StanfordCourseScheduler:
    def __init__(self):
        self.connect = CourseConnection()
        self.current_year = "2024-2025"  # Default to next academic year
        
        # Define AI-centric departments and keywords for GSB students
        self.ai_departments = [
            "CS", "STATS", "EE", "MS&E", "SYMSYS", "CME", "DS", "AI", "MATH"
        ]
        
        self.ai_keywords = [
            "machine learning", "artificial intelligence", "data science", "big data", 
            "analytics", "predictive modeling", "optimization", "algorithm", "neural network",
            "deep learning", "natural language processing", "computer vision", "reinforcement learning",
            "decision science", "quantitative analysis", "business analytics", "AI", "ML"
        ]
        
        # GSB-specific course recommendations
        self.gsb_ai_recommendations = [
            "CS 229: Machine Learning",
            "CS 230: Deep Learning",
            "CS 221: Artificial Intelligence: Principles and Techniques",
            "STATS 315A: Modern Applied Statistics: Learning",
            "MS&E 238: Machine Learning for Social and Economic Applications",
            "CS 224N: Natural Language Processing with Deep Learning",
            "CS 231N: Convolutional Neural Networks for Visual Recognition",
            "MS&E 241: Decision Analysis",
            "CS 221A: Introduction to Artificial Intelligence",
            "CME 304: Optimization for Machine Learning"
        ]
    
    def search_courses(self, query: str, department: str = None, quarter: str = None) -> List[Dict[str, Any]]:
        """Search courses based on natural language query"""
        results = []
        
        try:
            # If no department specified, search across all departments
            if department:
                courses = self.connect.get_courses_by_department(department, year=self.current_year)
            else:
                # Search across AI departments
                courses = []
                for dept_code in self.ai_departments:
                    dept_courses = self.connect.get_courses_by_department(dept_code, year=self.current_year)
                    courses.extend(dept_courses)
            
            # Filter courses based on query
            for course in courses:
                # Check if course matches query (case-insensitive)
                if self._matches_query(course, query):
                    course_info = {
                        "code": course.code,
                        "title": course.title,
                        "description": course.description,
                        "units": course.units,
                        "department": course.department.code,
                        "quarter": course.quarter,
                        "instructor": course.instructors[0].name if course.instructors else "TBD"
                    }
                    results.append(course_info)
                    
            return results
        except Exception as e:
            logger.error(f"Error searching courses: {e}")
            return []
    
    def _matches_query(self, course, query: str) -> bool:
        """Check if course matches natural language query"""
        if not query:
            return True
        
        query_lower = query.lower()
        
        # Check if query matches course title, description, or code
        if (query_lower in course.title.lower() or 
            query_lower in course.description.lower() or 
            query_lower in course.code.lower()):
            return True
        
        # Check for keyword matches
        for keyword in self.ai_keywords:
            if keyword in query_lower:
                return True
        
        return False
    
    def get_ai_recommendations(self) -> List[Dict[str, Any]]:
        """Get AI-centric course recommendations for GSB students"""
        recommendations = []
        
        for course_code in self.gsb_ai_recommendations:
            try:
                dept_code = course_code.split()[0]
                catalog_num = course_code.split()[1]
                
                # Get course details
                courses = self.connect.get_courses_by_department(dept_code, year=self.current_year)
                for course in courses:
                    if course.code == course_code:
                        recommendations.append({
                            "code": course.code,
                            "title": course.title,
                            "description": course.description,
                            "units": course.units,
                            "department": dept_code,
                            "instructor": course.instructors[0].name if course.instructors else "TBD"
                        })
                        break
            except Exception as e:
                logger.warning(f"Could not find details for {course_code}: {e}")
                continue
        
        return recommendations
    
    def get_departments(self) -> List[str]:
        """Get list of available departments"""
        try:
            schools = self.connect.get_schools(self.current_year)
            departments = []
            for school in schools:
                for dept in school.departments:
                    departments.append(dept.code)
            return departments
        except Exception as e:
            logger.error(f"Error getting departments: {e}")
            return []

# Natural language interface

def parse_command(user_input: str) -> Dict[str, Any]:
    """Parse natural language commands into structured parameters"""
    user_input = user_input.lower().strip()
    
    # Check for recommendation request
    if any(phrase in user_input for phrase in ["recommend", "suggest", "best ai", "ai courses", "top ai"]):
        return {"action": "recommend"}
    
    # Check for search command
    if any(phrase in user_input for phrase in ["search", "find", "look for", "courses", "class"]):
        # Extract department if mentioned
        department = None
        for dept in ["cs", "stats", "ee", "ms&e", "symsys", "cme", "ds", "math"]:
            if dept in user_input:
                department = dept.upper()
                break
        
        # Extract quarter if mentioned
        quarter = None
        if "autumn" in user_input or "fall" in user_input:
            quarter = "Autumn"
        elif "winter" in user_input:
            quarter = "Winter"
        elif "spring" in user_input:
            quarter = "Spring"
        elif "summer" in user_input:
            quarter = "Summer"
        
        # Extract search query
        query = user_input
        for phrase in ["search", "find", "look for", "courses", "class", "in", "for"]:
            query = query.replace(phrase, "")
        
        # Clean up query
        query = query.strip()
        
        return {
            "action": "search",
            "query": query,
            "department": department,
            "quarter": quarter
        }
    
    # Check for list departments
    if any(phrase in user_input for phrase in ["list departments", "all departments", "show departments"]):
        return {"action": "list_departments"}
    
    # Default to search with empty query
    return {"action": "search", "query": ""}

# Main application
if __name__ == "__main__":
    scheduler = StanfordCourseScheduler()
    
    print("Welcome to Stanford Course Scheduler for GSB Students!")
    print("Type 'quit' to exit. Ask for recommendations, search courses, or list departments.")
    print("Example queries: \n  - 'Recommend AI courses for GSB students'\n  - 'Search for machine learning courses'\n  - 'List departments'")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            # Parse command
            command = parse_command(user_input)
            
            if command["action"] == "recommend":
                print("\n🌟 Top AI Course Recommendations for GSB Students:")
                recommendations = scheduler.get_ai_recommendations()
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i}. {rec['code']}: {rec['title']} ({rec['units']} units)")
                    print(f"   Instructor: {rec['instructor']}")
                    print(f"   Department: {rec['department']}")
                    
            elif command["action"] == "search":
                print(f"\n🔍 Searching for: {command['query'] or 'all courses'}")
                if command["department"]:
                    print(f"   Department: {command['department']}")
                if command["quarter"]:
                    print(f"   Quarter: {command['quarter']}")
                
                results = scheduler.search_courses(
                    command["query"], 
                    command["department"], 
                    command["quarter"]
                )
                
                if results:
                    print(f"\nFound {len(results)} courses:")
                    for i, course in enumerate(results, 1):
                        print(f"{i}. {course['code']}: {course['title']} ({course['units']} units)")
                        print(f"   Instructor: {course['instructor']}")
                        print(f"   Department: {course['department']}")
                        if course['quarter']:
                            print(f"   Quarter: {course['quarter']}")
                else:
                    print("No courses found matching your criteria.")
            
            elif command["action"] == "list_departments":
                print("\n📚 Available Departments:")
                departments = scheduler.get_departments()
                for dept in sorted(departments):
                    print(f"  - {dept}")
            
            else:
                print("I didn't understand that. Try: 'Recommend AI courses', 'Search for machine learning', or 'List departments'")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue
