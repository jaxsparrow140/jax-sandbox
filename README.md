# Stanford Course Scheduler for GSB Students

A simple natural language interface to search and recommend AI-centric courses at Stanford University.

## Overview

This application helps GSB students find relevant courses with an AI focus by leveraging Stanford's ExploreCourses API. It provides a conversational interface to search for courses and recommends top AI-centric courses specifically valuable for GSB students.

## Features

- Natural language search for courses ("search for machine learning courses")
- AI-centric recommendations tailored for GSB students
- Department listing
- Support for searching by department and quarter
- Simple command-line interface

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/jaxsparrow140/jax-sandbox.git
   cd jax-sandbox
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python src/courses/course_search.py
```

Example commands:
- "Recommend AI courses for GSB students"
- "Search for machine learning courses"
- "Search for data science courses in Autumn"
- "List departments"
- "quit" to exit

## AI Recommendations for GSB Students

The app recommends these top AI-centric courses for GSB students:

1. CS 229: Machine Learning
2. CS 230: Deep Learning
3. CS 221: Artificial Intelligence: Principles and Techniques
4. STATS 315A: Modern Applied Statistics: Learning
5. MS&E 238: Machine Learning for Social and Economic Applications
6. CS 224N: Natural Language Processing with Deep Learning
7. CS 231N: Convolutional Neural Networks for Visual Recognition
8. MS&E 241: Decision Analysis
9. CS 221A: Introduction to Artificial Intelligence
10. CME 304: Optimization for Machine Learning

These courses combine technical AI skills with business applications, making them ideal for GSB students looking to leverage AI in their careers.

## License

MIT License