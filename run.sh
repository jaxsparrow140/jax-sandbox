#!/bin/bash

# Stanford Course Scheduler - Startup Script

# Change to the project directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Run the course scheduler
python src/courses/course_search.py

# Keep terminal open after exit (for debugging)
echo "\nPress any key to exit..."
read -n 1 -s