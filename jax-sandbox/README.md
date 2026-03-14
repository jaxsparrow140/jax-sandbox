# Stanford Course Scheduler

A simple, AI-powered course scheduling app for Stanford GSB students.

## Features

- **Natural Language Search**: Type what you're looking for in plain English
- **AI-Centric Recommendations**: Automatically recommends courses relevant to AI/ML for GSB students
- **Course Planning**: Add courses to your plan for next quarter
- **Simple Interface**: Clean, minimal UI

## Setup

```bash
pip install -r requirements.txt
python app.py
```

## Usage

Open your browser to `http://localhost:5000` and start searching!

### Natural Language Examples

- "I want AI courses for business students"
- "Show me machine learning classes"
- "Find courses about data analytics"
- "What CS courses can GSB students take?"

## Architecture

- Uses Stanford's Explore Courses API directly
- No external dependencies beyond Flask
- Runs locally in your sandbox